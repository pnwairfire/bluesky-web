import getpass
import json
import logging
import re
import os
import tarfile
import time
import uuid
from io import BytesIO
from urllib.parse import urlparse

import ipify
import tornado.log
from celery import Celery
from bluesky import exceptions, models

from blueskymongo.client import BlueSkyWebDB, RunStatuses

MONGODB_URL = os.environ.get('MONGODB_URL') or 'mongodb://localhost:27018/blueskyweb'
app = Celery('blueskyworker.tasks', broker=MONGODB_URL)

parse_object = urlparse(MONGODB_URL)
app.conf.update(
    result_backend='mongodb',
    mongodb_backend_settings={
        "host": parse_object.hostname,
        "port": parse_object.port or 27017,
        "user": parse_object.username,
        "password": parse_object.password,
        "database": parse_object.path.strip('/'),
        "taskmeta_collection": "stock_taskmeta_collection"
    }
)

try:
    IP_ADDRESS = ipify.get_ip()
except:
    # this should only happen in dev, if working without internet connection
    IP_ADDRESS = 'localhost'
HOSTNAME = os.environ.get('PUBLIC_HOSTNAME') or IP_ADDRESS

##
## Public Job Interface
##

class BlueSkyJobError(RuntimeError):
    pass

@app.task
def run_bluesky(input_data, **settings):
    """
    args:
     - input_data -- bsp input data
    Settings:
     See `_run_bluesky` helpstring for required settings
    """
    db = BlueSkyWebDB(MONGODB_URL)
    db.record_run(input_data['run_id'], RunStatuses.Dequeued,
        server={"ip": IP_ADDRESS})
    tornado.log.gen_log.info("Running %s from queue %s",
        input_data['run_id'],  '/') # TODO: get queue from job process

    if hasattr(input_data, 'lower'):
        input_data = json.loads(input_data)

    # TODO: (maybe run each module separately, so that more granular status
    #       can be saved in mongodb; or have this method parse logs as bsp
    #       is running
    return BlueSkyRunner(input_data, db=db, **settings).run()


##
## Launching process
##

class BlueSkyRunner(object):

    def __init__(self, input_data, output_stream=None, db=None, **settings):
        """Constructor
        args:
         - input_data -- bsp input data
        kwargs:
         - db -- bsp web mongodb client to record run status
        Settings:
         Required if writing to db (i.e. if `db` is defined):
          - output_url_scheme
          - output_url_port
          - output_url_path_prefix

        If this is an asynchronous run (i.e. `db` is defined), then we'll
        mount the output directory to the host machine's output directory;
        otherwise, we'll mount to host machines /tmp/, since we'll just
        read it here and then forget about it.
        """
        self.input_data = input_data
        self.output_stream = output_stream
        self.db = db
        self.settings = settings

    def run(self):
        self.input_data['run_id'] = (self.input_data.get('run_id')
            or str(uuid.uuid1()).replace('-',''))
        if not self.output_stream:
            self._set_output_params()
            self._set_output_url()

        return self._run_bsp()

    ##
    ## Setup
    ##

    def _set_output_params(self):
        self.output_dir = os.path.abspath(os.path.join(
            self.settings['output_root_dir'],
            self.settings['output_url_path_prefix'],
            self.input_data['run_id']))
        os.makedirs(self.output_dir, exist_ok=True) # TODO: is this necessary, or will docker create it?
        tornado.log.gen_log.debug('Output dir: %s', self.output_dir)
        self.output_json_filename = os.path.join(
            self.output_dir, 'output.json')
        self.output_log_filename = os.path.join(
            self.output_dir, 'output.log')

    def _set_output_url(self):
        scheme = self.settings.get('output_url_scheme') or 'https'
        port_str = (':' + self.settings['output_url_port']
            if self.settings.get('output_url_port') else '')
        prefix = (self.settings.get('output_url_path_prefix') or '').strip('/')
        self.output_url = "{}://{}{}/{}/{}".format(
            scheme, HOSTNAME, port_str, prefix, self.input_data['run_id'])

    ##
    ## Execution
    ##

    def _run_bsp(self):
        """Runs bluesky in-process, running each module individually for
        finer granularity in status logging.
        """
        try:
            if not self.output_stream:
                logging.basicConfig(filename=self.output_log_filename,
                    level=self.settings.get('bluesky_log_level', logging.INFO))
            # TODO: temporarily configure logging to go to file specifuc
            #  for this run; keep emissions/fuelbeds (non-async) runs
            #  in separate dir or indicate with file name if the run is async
            #  or not (which we know based on self.output_stream)
            #  Use params self.output_log_filename and self.settings['bluesky_log_level']
            fires_manager = models.fires.FiresManager()
            modules = self.input_data.pop('modules')
            fires_manager.load(self.input_data)
            for m in modules:
                # TODO: if hysplit dispersion, start thread that periodically
                #   tails log and records status; then join thread when call
                #   to run completes
                fires_manager.modules = [m]
                self._record_run(RunStatuses.Running, module=m)

                fires_manager.run()

            self._record_run(RunStatuses.ProcessingOutput)

            if self.output_stream:
                return fires_manager.dumps(self.output_stream)

            else:
                fires_manager.dumps(output_file=self.output_json_filename)

                data = {
                    'output_url': self.output_url,
                    'output_dir': self.output_dir
                }
                status = RunStatuses.Completed

                if fires_manager.error:
                    data['error'] = fires_manager.error
                    status = RunStatuses.Failed

                self._record_run(status, **data)

        except Exception as e:
            #tornado.log.gen_log.debug(traceback.format_exc())
            self._record_run(RunStatuses.Failed,
                error={"message": str(e)})
            raise BlueSkyJobError(str(e))

    ##
    ## DB
    ##

    def _record_run(self, status, log=None, stdout=None, **data):
        if self.db:
            self.db.record_run(self.input_data['run_id'], status, log=log,
                stdout=stdout, **data)
