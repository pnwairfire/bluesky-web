"""blueskyworker.tasks"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import abc
import datetime
import json
import logging
import re
import os
import ssl
import threading
import traceback
import uuid

import ipify
import tornado.log
from celery import Celery
from bluesky import (
    exceptions, models, __version__ as bluesky_version
)
from bluesky.config import Config

from blueskymongo.client import BlueSkyWebDB, RunStatuses

from .monitor import monitor_run

# mongodb used for recording run information, status, etc.
MONGODB_URL = os.environ.get('MONGODB_URL') or 'mongodb://blueskyweb:blueskywebmongopassword@mongo/blueskyweb'
# rabbitmq used for enqueueing runs
RABBITMQ_URL = os.environ.get('RABBITMQ_URL') or 'amqps://blueskyweb:blueskywebrabbitpassword@rabbit:5671'

app = Celery('blueskyworker.tasks', broker=RABBITMQ_URL)
app.conf.update(
    task_ignore_result=True,
    broker_use_ssl={
        'ssl_keyfile': '/etc/ssl/bluesky-web-client-cert.key',
        'ssl_certfile': '/etc/ssl/bluesky-web-client-cert.crt',
        'ssl_ca_certs': '/etc/ssl/bluesky-web-client.pem',
        'ssl_cert_reqs': ssl.CERT_NONE
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
def run_bluesky(input_data, api_version, **settings):
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

    output_processor = OUTPUT_PROCESSORS.get(api_version)

    t = BlueSkyRunner(input_data, db=db, output_processor=output_processor,
        **settings)
    t.start()
    t.join() # block until it completes


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


class BlueSkyRunner(threading.Thread):

    def __init__(self, input_data, output_stream=None, db=None,
            output_processor=None, **settings):
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
        super().__init__()
        self.input_data = input_data
        self.output_stream = output_stream
        self.db = db
        self.output_processor = output_processor
        self.settings = settings
        self.exception = None

    def run(self):
        try:
            self.input_data['run_id'] = (self.input_data.get('run_id')
                or str(uuid.uuid1()).replace('-',''))
            # self.input_data will be set to an empty dict when ingested by
            # FiresManager, so record run_id
            self.run_id = self.input_data['run_id']
            if not self.output_stream:
                self._set_output_params()
                self._set_output_url()

            return self._run_bsp()

        except Exception as e:
            self.exception = BlueSkyJobError(str(e))
            tornado.log.gen_log.debug(traceback.format_exc())
            self._record_run(RunStatuses.Failed,
                error={"message": str(e)})
            # store exception rather than raise it so
            # that main thread can act on it


    ##
    ## Setup
    ##

    def _set_output_params(self):
        self.output_dir = os.path.abspath(os.path.join(
            self.settings['output_root_dir'],
            self.settings['output_url_path_prefix'],
            self.run_id))
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
            scheme, HOSTNAME, port_str, prefix, self.run_id)

    ##
    ## Execution
    ##

    def _run_bsp(self):
        """Runs bluesky in-process, running each module individually for
        finer granularity in status logging.
        """
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



    def _run_bsp_modules(self):  # TODO: rename
        fires_manager = models.fires.FiresManager()
        modules = self.input_data.pop('modules')
        config = self.input_data.pop('config')
        Config().set(config)
        fires_manager.load(self.input_data)

        # Note that, once the run completes, this runtime will be
        # overwritten with a different start time, though the two
        # starts should be within milliseconds of each other
        runtime = {
            "start": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end": None
        }
        self._record_run(RunStatuses.Running, runtime=runtime)

        for m in modules:
            try:
                tornado.log.gen_log.info('Running %s %s',
                    self.run_id, m)
                fires_manager.modules = [m]
                self._record_run(RunStatuses.StartingModule, module=m)

                with monitor_run(m, fires_manager, self._record_run) as monitor:
                    fires_manager.run()

                data = {}
                if 'dispersion' in modules:
                    # It's a dispersion run
                    if m == 'export':
                        data['export'] = fires_manager.meta['export']
                elif m == 'plumerise':
                    # It's not a dispersion run, so this must be a
                    # plumerise run
                    data['fires'] = prune_for_plumerise(
                        fires_manager.fires)

                self._record_run(RunStatuses.CompletedModule, module=m, **data)

            except exceptions.BlueSkyModuleError as e:
                # The error was added to fires_manager's meta data, and will be
                # included in the output data
                self._record_run(RunStatuses.FailedModule, module=m,
                    status_message=e.args and e.args[0])
                break

        # TODO: handle any of the following individually?
        #   (it would be good if they inherited from a common
        #    base class, so that could be handled)
        #     exceptions.BlueSkyImportError
        #     exceptions.BlueSkyConfigurationError
        #     exceptions.MissingDependencyError
        #     exceptions.BlueSkyDatetimeValueError
        #     exceptions.BlueSkyGeographyValueError

        fires_manager.version_info = process_version_info(
            fires_manager.processing)
        self._record_run(RunStatuses.ProcessingOutput,
            runtime=process_runtime(fires_manager.runtime),
            version_info=fires_manager.version_info)

        if self.output_stream:
            return fires_manager.dumps(self.output_stream)

        else:
            if self.output_processor:
                output_writer = OutputFileWriter(self.output_json_filename)
                self.output_processor(output_writer).write(
                    fires_manager.dump())
            else:
                fires_manager.dumps(output_file=self.output_json_filename)

            return fires_manager.error


    ##
    ## DB
    ##

    def _record_run(self, status, module=None, log=None, stdout=None,
            status_message=None, **data):
        if self.db:
            self.db.record_run(self.run_id, status,
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
        "activity": [prune_activity_for_plumerise(a) for a in f.get('activity', [])]
    }

def prune_activity_for_plumerise(a):
    new_a = {
        'active_areas': []
    }

    for aa in a.active_areas:
        new_aa = slice_dict(aa, {'start', 'end', 'utc_offset'})
        if aa.get('specified_points'):
            new_aa['specified_points'] = [
                slice_dict(sp, {'lat', 'lng', 'area', 'plumerise'})
                    for sp in aa['specified_points']
            ]
        elif aa.get(perimeter):
            new_aa['perimeter'] = slice_dict(aa['perimeter'],
                {'polygon', 'area', 'plumerise'})
        new_a['active_areas'].append(new_aa)
    return new_a

def slice_dict(d, whitelist):
    return {k: d[k] for k in d.keys() & whitelist}

MICRO_SECOND_REMOVER = re.compile("\.[0-9]+Z$")

def process_runtime(runtime_info):
    runtime_info = runtime_info or {}
    processed = {}
    modules = runtime_info.get('modules', [])
    if modules:
        processed['start'] = min([e['start'] for e in modules])
        processed['end'] = max([e['end'] for e in modules])
    else:
        processed = {k: runtime_info.get(k) for k in ('start', 'end')}

    for k in ('start', 'end'):
        if processed[k]:
            processed[k] = MICRO_SECOND_REMOVER.sub('Z', processed[k])

    return processed

def process_version_info(processing_info):
    v = {
        "bluesky_version": bluesky_version,
    }
    for p in processing_info:
        v[p['module'].split('.')[-1]] = {k: p[k] for k in p if k.endswith('version') }

    return v


##
## Post processing to marshal between bluesky
##

class BlueskyProcessorBase(object, metaclass=abc.ABCMeta):

    def __init__(self, output_stream):
        self.output_stream = output_stream

    def write(self, data):
        if hasattr(data, 'lower'):
            data = json.loads(data)

        data = self._process(data)

        self.output_stream.write(data)


    @abc.abstractmethod
    def _process(self, data):
        pass


class BlueskyV1OutputProcessor(BlueskyProcessorBase):

    def _process(self, data):
        # converts data from v4.1/v4.2 to v1 output structure

        if data.get('fires'):
            data['fire_information'] = [
                self.convert_fire(models.fires.Fire(f)) for f in data.pop('fires')
            ]

        if data.get('run_config'):
            data['config'] = data.pop('run_config')

        return data

    def convert_fire(self, fire):
        """Converts each location into a growth object

        It's easier to just create a separate growth object out of
        each active area, rather than group active areas by day
        """
        growth = []
        for aa in fire.active_areas:
            for loc in aa.locations:
                g = self.convert_location(aa, loc)
                if g:
                    growth.append(g)

        if growth:
            fire['growth'] = growth

        fire.pop('activity', None)
        return fire

    def convert_location(self, aa, loc):
        g = {
            "location": {
                "ecoregion": aa.get('ecoregion'),
                "utc_offset": aa.get('utc_offset'),
                "area": loc.pop('area')
            }
        }

        if loc.get('lat') and loc.get('lng'):
            g['location']['latitude'] = loc.pop('lat')
            g['location']['longitude'] = loc.pop('lng')

        elif loc.get('polygon'):
            g['location']['geojson'] = {
                "type": "MultiPolygon",
                "coordinates": [[loc.pop('polygon')]]
            }

        else:
            return None

        g.update(**loc)
        g.update(**{k:v for k, v in aa.items() if k not in
            ('ecoregion','utc_offset', 'specified_points', 'perimeter')})

        return g

class BlueskyV4_1OutputProcessor(BlueskyProcessorBase):

    def _process(self, data):
        # covnerts older output data from v1 to v4.1 output structure
        if data.get('fire_information'):
            data['fires'] = Blueskyv4_0To4_1().marshal(
                data.pop('fire_information'))

        if data.get('config'):
            data['run_config'] = data.pop('config')

        # TODO: move export->localsave->visualization->dispersion->[images|kmzs]
        #   to export->localsave->visualization->[images|kmzs]
        #   (if other targets are under export->localsave->visualization,
        #    leave them in place)

        return data

class BlueskyV4_2OutputProcessor(BlueskyProcessorBase):

    def _process(self, data):
        # covnerts older output data from v1 to v4.2 output structure
        if data.get('fire_information'):
            data['fires'] = Blueskyv4_0To4_1().marshal(
                data.pop('fire_information'))

        if data.get('config'):
            data['run_config'] = data.pop('config')

        return data

OUTPUT_PROCESSORS = {
    '1': BlueskyV1OutputProcessor,
    '4.1': BlueskyV4_1OutputProcessor,
    '4.2': BlueskyV4_2OutputProcessor
}

def apply_output_processor(api_version, output_stream):
    if api_version in OUTPUT_PROCESSORS:
        output_stream = OUTPUT_PROCESSORS[api_version](output_stream)

    return output_stream


class OutputFileWriter(object):

    def __init__(self, output_json_filename):
        self.output_json_filename = output_json_filename

    def write(self, data):
        json_data = json.dumps(data, sort_keys=True, cls=models.fires.FireEncoder)
        with open(self.output_json_filename, 'w') as f:
            f.write(json_data)
