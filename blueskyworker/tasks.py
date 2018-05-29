import datetime
import getpass
import glob
import json
import logging
import re
import os
import subprocess
import tarfile
import threading
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

    return BlueSkyRunner(input_data, db=db, **settings).run()


##
## Launching process
##

class configure_logging:
    """Context handler that temporarily (for the life of a bsp run)
    configures logging to go to a run specific file.
    """

    BSP_LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s'

    def __init__(self, output_log_filename, **settings):
        self.output_log_filename = output_log_filename
        self.settings = settings

    def __enter__(self):
        root_logger = logging.getLogger()
        self.root_logger_original_handlers = []
        for h in root_logger.handlers:
            self.root_logger_original_handlers.append(h)
            root_logger.removeHandler(h)
        self.root_logger_original_level = root_logger.level
        self.log_file_handler = logging.FileHandler(self.output_log_filename)
        self.log_file_handler.setFormatter(logging.Formatter(self.BSP_LOG_FORMAT))
        log_level = self.settings.get('bluesky_log_level', logging.INFO)
        root_logger.setLevel(log_level)
        self.log_file_handler.setLevel(log_level) # TODO: is this necessary?
        root_logger.addHandler(self.log_file_handler)

    def __exit__(self, t, value, traceback):
        root_logger = logging.getLogger()
        for h in self.root_logger_original_handlers:
            root_logger.addHandler(h)
        root_logger.setLevel(self.root_logger_original_level)
        root_logger.removeHandler(self.log_file_handler)


class HysplitMonitor(threading.Thread):
    """Monitor thread that scrapes hysplit MESSAGE files to determine
    how many hours are complete
    """
    def __init__(self, m, fires_manager, record_run_func):
        super(HysplitMonitor, self).__init__()
        self.m = m
        self.fires_manager = fires_manager
        self.start_hour = self.fires_manager.get_config_value(
            'dispersion', 'start')
        self.num_hours = self.fires_manager.get_config_value(
            'dispersion', 'num_hours')

        self.record_run_func = record_run_func
        self.terminate = False
        self._message_file_name = None

    @property
    def message_file_name(self):
        if self._message_file_name is None:
            # this code will run again if no message files are found
            working_dir = self.fires_manager.get_config_value(
                'dispersion', 'working_dir')
            mp1 = os.path.join(working_dir, 'MESSAGE')
            if os.path.exists(mp1):
                self._message_file_name = mp1
            else:
                mpN = os.path.join(working_dir, 'MESSAGE.001')
                if os.path.exists(mpN):
                    self._message_file_name = mpN

        return self._message_file_name

    def run(self):
        while not self.terminate:
            self.check_progress()
            time.sleep(5)

    def check_progress(self):
        percent_complete = 2
        if self.message_file_name:
            try:
                # estimate percent complete based on slowest of
                # all hysplit processes
                current_hour = self.get_current_hour()
                # we want percent_complete to be between 3 and 90
                percent_complete = int((90 * (current_hour / self.num_hours)) + 2)
            except Exception as e:
                tornado.log.gen_log.info("Failed to check progress: %s", e)

        # else, leave at 2
        tornado.log.gen_log.info("Run %s hysplit %d complete",
            self.fires_manager.run_id, percent_complete)

        self.record_run_func(RunStatuses.RunningModule, module=self.m,
            percent_complete=percent_complete)

    def get_current_hour(self):
        output_lines = [l for l in subprocess.check_output(
            ["grep", "output", self.message_file_name]).decode().split('\n') if l]
        return len(output_lines)


class monitor_run(object):

    def __init__(self, m, fires_manager, record_run_func):
        tornado.log.gen_log.info("Constructing monitor_run context manager")
        self.m = m
        self.fires_manager = fires_manager
        self.record_run_func = record_run_func
        self.thread = None

    def __enter__(self):
        tornado.log.gen_log.info("Entering monitor_run context manager")
        if self._is_hysplit():
            tornado.log.gen_log.info("Starting thread to monitor hysplit")
            self.thread = HysplitMonitor(self.m, self.fires_manager, self.record_run_func)
            self.thread.start()

    def __exit__(self, e_type, value, tb):
        if self.thread:
            self.thread.terminate = True
            tornado.log.gen_log.info("joining hysplit monitoring thread")
            self.thread.join()

    def _is_hysplit(self):
        if self.m =='dispersion':
            model = self.fires_manager.get_config_value(
                'dispersion', 'model', default='hysplit')
            return model == 'hysplit'
        return False


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
            if self.output_stream:
                return self._run_bsp_modules()

            else:
                with configure_logging(self.output_log_filename, **self.settings) as foo:
                    error = self._run_bsp_modules()

                data = {
                    'output_url': self.output_url,
                    'output_dir': self.output_dir,
                    'percent_complete': 100
                }
                status = RunStatuses.Completed

                if error:
                    data['error'] = error
                    status = RunStatuses.Failed

                self._record_run(status, **data)

        except Exception as e:
            #tornado.log.gen_log.debug(traceback.format_exc())
            self._record_run(RunStatuses.Failed,
                error={"message": str(e)})
            raise BlueSkyJobError(str(e))


    def _run_bsp_modules(self):  # TODO: rename
        fires_manager = models.fires.FiresManager()
        modules = self.input_data.pop('modules')
        fires_manager.load(self.input_data)

        self._record_run(RunStatuses.Running)
        for m in modules:
            try:
                # TODO: if hysplit dispersion, start thread that periodically
                #   tails log and records status; then join thread when call
                #   to run completes
                tornado.log.gen_log.info('Running %s %s',
                    self.input_data['run_id'], m)
                fires_manager.modules = [m]
                self._record_run(RunStatuses.StartingModule, module=m)

                with monitor_run(m, fires_manager, self._record_run) as monitor:
                    fires_manager.run()

                data = {}
                if 'dispersion' in modules:
                    # It's a dispersion run
                    if m == 'export':
                        data['export'] = fires_manager.meta['export']
                elif m == 'plumerising':
                    # It's not a dispersion run, so this must be a
                    # plumerise run
                    data['fire_information'] = prune_for_plumerise(
                        fires_manager.fires)

                self._record_run(RunStatuses.CompletedModule, module=m, **data)

            except exceptions.BlueSkyModuleError as e:
                # The error was added to fires_manager's meta data, and will be
                # included in the output data
                self._record_run(RunStatuses.FailedModule, module=m,
                    status_message=e.args[0])
                break

        # TODO: handle any of the following individually?
        #   (it would be good if they inherited from a common
        #    base class, so that could be handled)
        #     exceptions.BlueSkyImportError
        #     exceptions.BlueSkyConfigurationError
        #     exceptions.MissingDependencyError
        #     exceptions.BlueSkyDatetimeValueError
        #     exceptions.BlueSkyGeographyValueError


        self._record_run(RunStatuses.ProcessingOutput)

        if self.output_stream:
            return fires_manager.dumps(self.output_stream)
        else:
            fires_manager.dumps(output_file=self.output_json_filename)
            return fires_manager.error


    ##
    ## DB
    ##

    def _record_run(self, status, module=None, log=None, stdout=None,
            status_message=None, **data):
        if self.db:
            self.db.record_run(self.input_data['run_id'], status,
                module=module, log=log, stdout=stdout,
                status_message=status_message, **data)


# ##
# ## Helper functions used by BlueSkyRunner, but defined at module
# ## scope to be resused by other modules
# ##


def prune_for_plumerise(fire_info):
    """Creates a new list of fires, pruned to include only data relevant
    to plumerise API requests.

    Note: To avoid modifying fire_into as well as creating a complete
    copy of fire_info, to be pruned in place, this method creates a new
    list of pruned fire information from scratch (i.e. without
    deepcopying fire_info)
    """
    return [prune_fire_for_plumerise(f) for f in fire_info]

def prune_fire_for_plumerise(f):
    return {
        "id": f.get('id'),
        "growth": [prune_growth_for_plumerise(g) for g in f.get('growth', [])]
    }

def prune_growth_for_plumerise(g):
    new_g = slice_dict(g, {'start', 'end', 'location', 'plumerise'})
    new_g['location'] = slice_dict(new_g['location'],
        {'latitude', 'utc_offset', 'longitude', 'area', 'geojson'})
    return new_g

def slice_dict(d, whitelist):
    return {k: d[k] for k in d.keys() & whitelist}
