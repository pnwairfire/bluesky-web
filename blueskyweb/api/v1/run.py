"""blueskyweb.api.v1.run"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import datetime
import json
import os
import requests
import urllib.request, urllib.error, urllib.parse
import uuid
import traceback

import ipify
import tornado.web
import tornado.log

from blueskymongo.client import RunStatuses
from blueskyworker.tasks import run_bluesky, BlueSkyRunner
from blueskyweb.lib import met, hysplit
from . import RequestHandlerBase


try:
    IP_ADDRESS = ipify.get_ip()
except:
    # IP_ADDRESS is only used to see if worker is running on
    # same machine as web server.  If ipify fails, we'll just
    # resort to loading all output as if from remote server
    pass

##
## Utilities for working with remote output
##

class remote_open(object):
    """Context manager that clones opens remote file and closes it on exit
    """

    def __init__(self, url):
        self.url = url

    def __enter__(self):
        self.f = urllib.request.urlopen(self.url)
        return self.f

    def __exit__(self, type, value, traceback):
        self.f.close()

def remote_exists(url):
    return requests.head(url).status_code != 404

def get_output_server_info(run_id):
    output_server_info = {} # TODO: Get info from mongodb
    return output_server_info

def get_output_url(run_id):

    return "{}{}".format(get_output_root_url(run_id), url_root_dir)

# PORT_IN_HOSTNAME_MATCHER = re.compile(':\d+')
# def is_same_host(web_request_host):
#     """Checks to see if the output is local to the web service
#
#     If they are local, the run status and output APIS can carry out their
#     checks more efficiently and quickly.
#
#     This function is a complete hack, but it works, at least some of the time.
#     (And when it fails, it should only result in false negatives, which
#     don't affect the correctness of the calling APIs - it just means they
#     don't take advantage of working with local files.)
#     """
#     # first check if same hostname
#     try:
#         web_service_host = socket.gethostbyaddr(socket.gethostname())[0]
#     except:
#         web_service_host = PORT_IN_HOSTNAME_MATCHER.sub('', web_request_host)
#
#     output_hostname = "" # TODO: Get hostname from mongodb
#     if output_hostname == web_service_host:
#         return True
#
#     # TODO: determine ip address of upload host and web service host and
#     #   check if ip addresses match
#
#     return False

def is_same_host(run):
    return run['server']['ip'] == IP_ADDRESS

###
### API Handlers
###

class RunExecuter(RequestHandlerBase):

    @tornado.web.asynchronous
    async def post(self, mode=None, archive_id=None):
        self._mode = mode
        self._archive_id = archive_id
        self._archive_info = met.get_archive_info(archive_id)

        if not self.request.body:
            self._bad_request(400, 'empty post data')
            return

        data = json.loads(self.request.body.decode())
        if "fire_information" not in data:
            self._bad_request(400, "'fire_information' not specified")
            return

        # TODO: should no configuration be allowed at all?  or only some? if
        #  any restrictions, check here or check in specific _configure_*
        #  methods, below

        # run_id is only necessary if running asynchronously, but it doesn't
        # hurt to set it anyway; it's needed in configuring dispersion, so
        # it has to be set before _run_asynchronously
        if not data.get('run_id'):
            data['run_id'] = str(uuid.uuid1())

        try:
            self._set_modules(mode, data)

            # TODO: check data['modules'] specifically for 'localmet',
            # 'dispersion', 'visualization' (and 'export'?)
            #tornado.log.gen_log.debug("BSP input data: %s", json.dumps(data))
            if mode not in ('fuelbeds', 'emissions'):
                # plumerise or dispersion (Hysplit or VSMOKE) request
                for m in data['modules']:
                    f = getattr(self, '_configure_{}'.format(m), None)
                    if f:
                        await f(data)

                # TODO: configure anything else (e.g. setting archive_id where
                #  appropriate)
                self._run_asynchronously(data)

            else:
                await self._configure_emissions(data)
                # fuelbeds or emissions request
                if self.get_query_argument('_a', default=None) is not None:
                    self._run_asynchronously(data)
                else:
                    await self._run_in_process(data)

        except tornado.web.HTTPError as e:
            # this was intentionally raised; re-raise it
            self.write({'error': str(e)})
            raise

        except Exception as e:
            # IF exceptions aren't caught, the traceback is returned as
            # the response body
            tornado.log.gen_log.debug(traceback.format_exc())
            tornado.log.gen_log.error('Exception: %s', e)
            self.set_status(500)

    ## Helpers

    FUELBEDS_MODULES = [
        'ingestion', 'fuelbeds'
    ]
    EMISSIONS_MODULES = [
        'consumption', 'emissions'
    ]
    PLUMERISE_MODULES = [
        'timeprofiling', 'plumerising'
    ]
    # TODO: for dispersion requests, instead of running findmetdata, get
    #   met data from indexed met data in mongodb;  maybe fall back on
    #   running findmetdata if indexed data isn't there or if mongodb
    #   query fails
    MET_DISPERSION_MODULES = [
        'findmetdata', 'dispersion', 'visualization', 'export'
    ]
    METLESS_DISPERSION_MODULES = [
        'dispersion', 'export'
    ]

    def _set_modules(self, mode, data):
        def _set(default_modules):
            if "modules" in data:  #data.get('modules'):
                invalid_modules = set(data['modules']).difference(
                    default_modules)
                if invalid_modules:
                    self._bad_request(400, "invalid module(s) for emissions "
                        "request: {}".format(','.join(invalid_modules)))
                    return
                # else, leave as is
            else:
                data['modules'] = default_modules


        if mode in ('dispersion', 'all'):
            dispersion_modules = (self.MET_DISPERSION_MODULES
                if self._archive_id else self.METLESS_DISPERSION_MODULES)
            if mode == 'all':
                if self._archive_id:
                    _set(self.FUELBEDS_MODULES +
                        self.EMISSIONS_MODULES +
                        self.PLUMERISE_MODULES +
                        dispersion_modules)
                else:
                    _set(self.FUELBEDS_MODULES +
                        self.EMISSIONS_MODULES +
                        # vsmoke needs timeprofiling but not plumerise
                        ['timeprofiling'] +
                        dispersion_modules)
            else:
                if self._archive_id and ('met' not in data):
                    _set(['findmetdata'] + dispersion_modules)
                else:
                    _set(dispersion_modules)
        elif mode == 'plumerise':
            _set(self.PLUMERISE_MODULES)
        elif mode == 'emissions':
            _set(self.EMISSIONS_MODULES)
        elif mode == 'fuelbeds':
            _set(self.FUELBEDS_MODULES)
        # There are no other possibilities for mode

        tornado.log.gen_log.debug("Modules be run: {}".format(', '.join(data['modules'])))

    def _bad_request(self, status, msg):
        msg = "Bad request: " + msg
        tornado.log.gen_log.warn(msg)
        self.set_status(status, msg)
        #self.write({"error": msg})
        #self.finish()

    def _run_asynchronously(self, data):
        queue_name = self._archive_id or 'no-met'

        #tornado.log.gen_log.debug('input: %s', data)
        args = (data, ) # has to be a tuple

        # TODO: figure out how to enqueue without blocking
        settings = {k:v for k, v in self.settings.items() if k != 'mongo_db'}
        run_bluesky.apply_async(args=args, kwargs=settings, queue=queue_name)
        # TODO: specify callback in record_run, calling
        #    self.write in callback, so we can handle failure?
        self.settings['mongo_db'].record_run(data['run_id'],
            RunStatuses.Enqueued, queue=queue_name, modules=data["modules"],
            initiated_at=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
        self.write({"run_id": data['run_id']})

    async def _run_in_process(self, data):
        try:
             # will call self.write
            output = BlueSkyRunner(data, output_stream=self).run()

        except Exception as e:
            tornado.log.gen_log.debug(traceback.format_exc())
            tornado.log.gen_log.error('Exception: %s', e)
            self.set_status(500)

    ##
    ## Configuration
    ##

    ## Emissions

    async def _configure_emissions(self, data):
        tornado.log.gen_log.debug('Configuring emissions')
        data['config'] = data.get('config', {})
        data['config']['emissions'] = data['config'].get('emissions', {})
        data['config']['emissions']['efs'] = "urbanski"

    ## Findmetdata

    async def _configure_findmetdata(self, data):
        tornado.log.gen_log.debug('Configuring findmetdata')
        data['config'] = data.get('config', {})
        met_archives_db = met.MetArchiveDB(self.settings['mongodb_url'])
        try:
            met_root_dir = await met_archives_db.get_root_dir(self._archive_id)
        except met.UnavailableArchiveError as e:
            msg = "Archive unavailable: {}".format(self._archive_id)
            raise tornado.web.HTTPError(status_code=404, log_message=msg)

        data['config']['findmetdata'] = {
            "met_root_dir": met_root_dir,
            "arl": {
                "index_filename_pattern":
                    self._archive_info['arl_index_file'],
                "fewer_arl_files": True
            }
        }

    ## Localmet

    async def _configure_localmet(self, data):
        tornado.log.gen_log.debug('Configuring localmet')
        data['config'] = data.get('config', {})
        data['config']['localmet'] = {
            "time_step": met._archive_info['time_step']
        }

    ## Plumerise

    async def _configure_plumerising(self, data):
        tornado.log.gen_log.debug('Configuring plumerising')
        data['config'] = data.get('config', {})
        data['config']['plumerising'] = {
            "model": "feps"
        }

    ## Dispersion

    DEFAULT_HYSPLIT_GRID_LENGTH = 2000

    async def _configure_dispersion(self, data):
        tornado.log.gen_log.debug('Configuring dispersion')
        if (not data.get('config', {}).get('dispersion', {}) or not
                data['config']['dispersion'].get('start') or not
                data['config']['dispersion'].get('num_hours')):
            self._bad_request(400, "dispersion 'start' and 'num_hours' must be specified")
            return

        data['config']['dispersion']['output_dir'] = os.path.join(
            self.settings['output_root_dir'],
            self.settings['output_url_path_prefix'],
            '{run_id}', 'output')
        data['config']['dispersion']['working_dir'] = os.path.join(
            self.settings['output_root_dir'],
            self.settings['output_url_path_prefix'],
            '{run_id}', 'working')
        tornado.log.gen_log.debug("Output dir: %s",
            data['config']['dispersion']['output_dir'])
        tornado.log.gen_log.debug("Working dir: %s",
            data['config']['dispersion']['working_dir'])

        if not self._archive_id:
            data['config']['dispersion']['model'] = 'vsmoke'

        if data['config']['dispersion'].get('model') in ('hysplit', None):
            configurator = hysplit.HysplitConfigurator(self, data,
                self._archive_info)
            data['config']['dispersion']['hysplit'] = configurator.config


    ## Visualization

    async def _configure_visualization(self, data):
        tornado.log.gen_log.debug('Configuring visualization')
        # Force visualization of dispersion, and let output go into dispersion
        # output directory; in case dispersion model was hysplit, specify
        # images and data sub-directories;
        # TODO: if other dispersion models are supported in the future, and if
        #  their visualization results in images and data files, they will
        #  have to be configured here as well.
        data['config'] = data.get('config', {})
        data['config']['visualization'] =  data['config'].get('visualization', {})
        data['config']['visualization']["target"] = "dispersion"
        data['config']['visualization']["hysplit"] = data['config']['visualization'].get("hysplit", {})
        data['config']['visualization']["hysplit"]["images_dir"] = "images/"
        data['config']['visualization']["hysplit"]["data_dir"] = "data/"
        data['config']['visualization']["hysplit"]["create_summary_json"] = True
        tornado.log.gen_log.debug('visualization config: %s', data['config']['visualization'])
        # TODO: set anything else?

    ## Export

    async def _configure_export(self, data):
        # we just run export to get image and file information
        tornado.log.gen_log.debug('Configuring export')
        # dest_dir = data['config']['dispersion']['output_dir'].replace(
        #     'output', 'export')
        # Run id will be
        dest_dir = os.path.join(
            self.settings['output_root_dir'],
            self.settings['output_url_path_prefix'])

        extras = ["dispersion", "visualization"] if self._archive_id else ["dispersion"]
        data['config']['export'] = {
            "modes": ["localsave"],
            "extra_exports": extras,
            "localsave": {
                "handle_existing": "write_in_place",
                "dest_dir": dest_dir
            }
        }


class RunStatusBase(RequestHandlerBase):

    VERBOSE_FIELDS = ('output_dir', 'modules', 'server')

    async def process(self, run):
        if not self.get_boolean_arg('raw'):
            # need to call get_queue_position before converting
            # run['status'] from array to scalar object
            position = await self.settings['mongo_db'].get_queue_position(run)
            if position is not None:
                run['queue'] = {
                    'name': run['queue'],
                    'position': position
                }
            else:
                tornado.log.gen_log.debug(run)
                run.pop('queue', None)

            # history is in reverse chronological order
            # Note: history will always be defined; a run is never
            #  recorded in the db without adding to the history
            run['status'] = run.pop('history')[0] # if run.get('history') else None

            #run['complete'] = 'output_url' in run
            run['complete'] = (run['status']['status']
                in (RunStatuses.Completed, RunStatuses.Failed))

            if (run['status']['status'] in
                    (RunStatuses.Enqueued, RunStatuses.Dequeued)):
                run['percent'] = 0
            elif (run['status']['status'] in
                    (RunStatuses.Completed, RunStatuses.Failed)):
                run['percent'] = 100
            elif run['status']['status'] == RunStatuses.ProcessingOutput:
                run['percent'] = 99  # HACK
            else: # RunStatuses.Running
                # TODO: figure out how to estimate percentage from
                #   log and stdout information
                run['percent'] = 50  # HACK

            # prune
            for k in self.VERBOSE_FIELDS:
                run.pop(k, None)

        return run


class RunStatus(RunStatusBase):

    @tornado.web.asynchronous
    async def get(self, run_id):
        # TODO: implement using data form mongodb
        run = await self.settings['mongo_db'].find_run(run_id)
        if not run:
            self.set_status(404, "Run doesn't exist")
            self.write({"error": "Run doesn't exist"})
        else:
            await self.process(run)
            self.write(run)


class RunsInfo(RunStatusBase):

    @tornado.web.asynchronous
    async def get(self, status=None):
        limit = int(self.get_query_argument('limit', 10))
        offset = int(self.get_query_argument('offset', 0))
        runs = await self.settings['mongo_db'].find_runs(status=status,
            limit=limit, offset=offset)
        for run in runs:
            await self.process(run)

        # TODO: include total count of runs with given status, and of runs
        #    of all statuses?
        self.write({"runs": runs})


class RunOutput(RequestHandlerBase):

    @tornado.web.asynchronous
    async def get(self, run_id):
        # TODO: implement using data form mongodb
        run = await self.settings['mongo_db'].find_run(run_id)
        if not run:
            self.set_status(404, "Run doesn't exist")
            self.write({"error": "Run doesn't exist"})
        elif not run['output_url']:
            self.set_status(404, "Run output doesn't exist")
            self.write({"error": "Run output doesn't exist"})
        else:
            output = self._load_output(run)
            if 'dispersion' in run['modules']:
                #if output['config']['dispersion'].get('model') != 'vsmoke'):
                self._get_dispersion(run, output)
            elif run['modules'][-1] == 'plumerising':
                self._get_plumerise(run, output)
            else:
                # TODO: is returning raw input not ok?
                self.write(output)

    ##
    ## Plumerise
    ##

    def _get_plumerise(self, run, output):
        output = {k:v for k,v in output.items()
            if k in ('run_id', 'fire_information')}
        for f in output['fire_information']:
            for i in range(len(f['growth'])):
                f['growth'][i] = {k:v for k,v in f['growth'][i].items()
                    if k in ('start', 'end', 'location', 'plumerise')}

        self.write(output)

    ##
    ## Dispersion
    ##

    def _get_dispersion(self, run, output):
        r = {
            "root_url": run['output_url']
        }
        vis_info = output['export']['localsave'].get('visualization')
        if vis_info:
            # images
            self._parse_images(r, vis_info)

            # kmzs
            self._parse_kmzs_info(r, vis_info)

        disp_info = output['export']['localsave'].get('dispersion')
        if disp_info:
            r.update(**{
                k: '{}/{}'.format(disp_info['sub_directory'], disp_info[k.lower()])
                for k in ('netCDF', 'netCDFs') if k.lower() in disp_info})

            # kmzs (vsmoke dispersion produces kmzs)
            self._parse_kmzs_info(r, disp_info)

        # TODO: list fire_*.csv if specified in output

        self.write(r)

    def _parse_kmzs_info(self, r, section_info):
        kmz_info = section_info.get('kmzs', {})
        if kmz_info:
            r['kmzs'] = {k: '{}/{}'.format(section_info['sub_directory'], v)
                for k, v in list(kmz_info.items()) if k in ('fire', 'smoke')}

    def _parse_images(self, r, vis_info):
        r["images"] = vis_info.get('images')
        def _parse(r):
            if "directory" in d:
                d["directory"] = os.path.join(
                    vis_info['sub_directory'], d["directory"])
            else:
                for e in d:
                    _parse(e)


    ##
    ## Common methods
    ##

    def _load_output(self, run):
        # TODO: Maybe first try local no matter what, since is_same_host might
        #   give false negative and checking local shouldn't give false postive
        #   (only do this if is_same_host returns false negative in production)
        if is_same_host(run):
            tornado.log.gen_log.debug('Loading local output')
            return self._get(run['output_dir'], os.path.exists, open)
        else:
            tornado.log.gen_log.debug('Loading remote output')
            return self._get(run['output_url'], remote_exists, remote_open)

    def _get(self, output_location, exists_func, open_func):
        """Gets information about the outpu output, which may be in local dir
        or on remote host

        args:
         - output_location -- local pathname or url
         - exists_func -- function to check existence of dir or file
            (local or via http)
         - open_func -- function to open output json file (local or via http)
        """
        tornado.log.gen_log.debug('Looking for output in %s', output_location)
        if not exists_func(output_location):
            msg = "Output location doesn't exist: {}".format(output_location)
            raise tornado.web.HTTPError(status_code=404, log_message=msg)

        # use join instead of os.path.join in case output_location is a remote url
        output_json_file = '/'.join([output_location.rstrip('/'), 'output.json'])
        if not exists_func(output_json_file):
            msg = "Output file doesn't exist: {}".format(output_json_file)
            raise tornado.web.HTTPError(status_code=404, log_message=msg)

        with open_func(output_json_file) as f:
            try:
                j = f.read()
                if hasattr(j, 'decode'):
                    j = j.decode()
                return json.loads(j)
                # TODO: set fields here, using , etc.
            except:
                msg = "Failed to open output file: {}".format(output_json_file)
                raise tornado.web.HTTPError(status_code=500, log_message=msg)

