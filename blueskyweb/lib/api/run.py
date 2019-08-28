"""blueskyweb.lib.api.run"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import abc
import datetime
import json
import os
import re
import requests
import urllib.request, urllib.error, urllib.parse
import uuid
import traceback

import ipify
import tornado.web
import tornado.log

from blueskymongo.client import RunStatuses
from blueskyworker.tasks import (
    run_bluesky, BlueSkyRunner, prune_for_plumerise, process_runtime
)
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

class RunExecuterBase(RequestHandlerBase, metaclass=abc.ABCMeta):

    ##
    ## Abstract methods to be implemebed by derived classes
    ##

    @property
    @abc.abstractmethod
    def fires_key(self):
        pass

    def _pre_process(self, data):
        """Hook for derived class to process request input data before
        anything else.  e.g. v1 can marshal the data to the bluesky v4.1
        data structure.
        """
        pass


    ##
    ## Main interface
    ##

    @tornado.web.asynchronous
    async def post(self, mode=None, archive_id=None):
        self._mode = mode
        self._archive_id = archive_id
        self._archive_info = met.db.get_archive_info(archive_id)

        if not self.request.body:
            self._raise_error(400, 'empty post data')
            return

        data = json.loads(self.request.body.decode())
        if self.fires_key not in data:
            self._raise_error(400, "'{}' not specified".format(self.fires_key))
            return

        self._pre_process(data)

        # TODO: should no configuration be allowed at all?  or only some? if
        #  any restrictions, check here or check in specific _configure_*
        #  methods, below

        self._set_run_id_and_name(data)

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
                await self._run_asynchronously(data, mode)

            else:
                await self._configure_emissions(data)
                # fuelbeds or emissions request
                if self.get_query_argument('_a', default=None) is not None:
                    await self._run_asynchronously(data, mode)
                else:
                    await self._run_in_process(data)

        except tornado.web.Finish as e:
            # this was intentionally raised; re-raise it
            raise

        except Exception as e:
            # IF exceptions aren't caught, the traceback is returned as
            # the response body
            self.return_500(e)

    ##
    ## Helpers
    ##

    def return_500(self, e, skip_traceback=False):
        if not skip_traceback:
            tornado.log.gen_log.debug(traceback.format_exc())
        tornado.log.gen_log.error('Exception: %s', e)
        self.set_status(500)

    RUN_ID_SUFFIX_REMOVER = re.compile('-(plumerise|dispersion)$')

    def _set_run_id_and_name(self, data):
        # run_id is only necessary if running asynchronously, but it doesn't
        # hurt to set it anyway; it's needed in configuring dispersion, so
        # it has to be set before _run_asynchronously
        if not data.get('run_id'):
            data['run_id'] = str(uuid.uuid1())
        tornado.log.gen_log.info("%s request for run id: %s", self._mode,
            data['run_id'])

        # This is really just for PGv3 runs
        if self.RUN_ID_SUFFIX_REMOVER.search(data['run_id']):
            for f in data["fires"]:
                f['event_of'] = f.get('event_of', {})
                if not f['event_of'].get('name'):
                    name = 'Scenario Id {}'.format(
                        self.RUN_ID_SUFFIX_REMOVER.sub('', data['run_id']))
                    f['event_of']['name'] = name

    FUELBEDS_MODULES = [
        'ingestion', 'fuelbeds'
    ]
    EMISSIONS_MODULES = [
        'consumption', 'emissions'
    ]
    PLUMERISE_MODULES = [
        'plumerising', 'extrafiles'
    ]
    # TODO: for dispersion requests, instead of running findmetdata, get
    #   met data from indexed met data in mongodb;  maybe fall back on
    #   running findmetdata if indexed data isn't there or if mongodb
    #   query fails
    MET_DISPERSION_MODULES = [
        'findmetdata', 'extrafiles', 'dispersion', 'visualization', 'export'
    ]
    METLESS_DISPERSION_MODULES = [
        'dispersion', 'export'
    ]

    def _plumerise_modules(self, data):
        # just look at first growth object of first fire
        if 'timeprofile' in data['fires'][0]['growth'][0]:
            return self.PLUMERISE_MODULES
        else:
            return ['timeprofiling'] + self.PLUMERISE_MODULES

    def _set_modules(self, mode, data):
        def _set(default_modules):
            if "modules" in data:  #data.get('modules'):
                invalid_modules = set(data['modules']).difference(
                    default_modules)
                if invalid_modules:
                    self._raise_error(400, "invalid module(s) for {} "
                        "request: {}".format(mode, ','.join(invalid_modules)))
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
                        self._plumerise_modules(data) +
                        dispersion_modules)
                else:
                    _set(self.FUELBEDS_MODULES +
                        self.EMISSIONS_MODULES +
                        # vsmoke needs timeprofiling but not plumerise
                        ['timeprofiling'] +
                        dispersion_modules)
            else:
                _set(dispersion_modules)
        elif mode == 'plumerise':
            _set(self._plumerise_modules(data))
        elif mode == 'emissions':
            _set(self.EMISSIONS_MODULES)
        elif mode == 'fuelbeds':
            _set(self.FUELBEDS_MODULES)
        # There are no other possibilities for mode

        tornado.log.gen_log.debug("Modules be run: {}".format(', '.join(data['modules'])))

    async def _check_for_existing_run_id(self, run_id):
        run = await self.settings['mongo_db'].find_run(run_id)
        if run:
            # TODO: eventually, when STI's code is updated to handle it,
            #   we want to do one of two things:
            #     - fail and return 409
            #     - create a new run_id for this run, and maybe
            #       include a warning in the API response that the run_id
            #       was changed.
            #   for now, just move existing record in the db
            await self.settings['mongo_db']._archive_run(run)


    async def _run_asynchronously(self, data, mode):
        await self._check_for_existing_run_id(data['run_id'])

        queue_name = self._archive_id or 'no-met'
        if mode == 'plumerise':
            queue_name += '-plumerise'

        #tornado.log.gen_log.debug('input: %s', data)
        args = (data, ) # has to be a tuple

        # TODO: figure out how to enqueue without blocking
        settings = {k:v for k, v in self.settings.items() if k != 'mongo_db'}
        tornado.log.gen_log.debug("About to enqueue run %s",
            data.get('run_id'))
        run_bluesky.apply_async(args=args, kwargs=settings, queue=queue_name)
        # TODO: specify callback in record_run, calling
        #    self.write in callback, so we can handle failure?
        self.settings['mongo_db'].record_run(data['run_id'],
            RunStatuses.Enqueued, queue=queue_name, modules=data["modules"],
            initiated_at=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
        self.write({"run_id": data['run_id']})

    async def _run_in_process(self, data):
        # We need the outer try block to handle any exception raised
        # before the bluesky thread is started. If an exception is
        # encountered in the seperate thread, it's handling
        try:
            # Runs bluesky in a separate thread so that run configurations
            # don't overwrite each other. (Bluesky manages configuration
            # with a singleton that stores config data in thread local)
            # BlueSkyRunner will call self.write.
            t = BlueSkyRunner(data, output_stream=self)
            t.start()
            # block until it completes so that we can return 500 if necessary
            t.join()
            if t.exception:
                self.return_500(t.exception, skip_traceback=True)

        except Exception as e:
            self.return_500(t.exception)

    ##
    ## Configuration
    ##

    ## Emissions

    async def _configure_emissions(self, data):
        tornado.log.gen_log.debug('Configuring emissions')
        data['config'] = data.get('config', {})
        data['config']['emissions'] = data['config'].get('emissions', {})
        data['config']['emissions']['model'] = "prichard-oneill"

    ## Findmetdata

    async def _configure_findmetdata(self, data):
        tornado.log.gen_log.debug('Configuring findmetdata')
        data['config'] = data.get('config', {})
        met_archives_db = met.db.MetArchiveDB(self.settings['mongodb_url'])
        try:
            met_root_dir = await met_archives_db.get_root_dir(self._archive_id)
        except met.db.UnavailableArchiveError as e:
            msg = "Archive unavailable: {}".format(self._archive_id)
            self._raise_error(404, msg)

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
            "time_step": met.db._archive_info['time_step']
        }

    ## Plumerise

    async def _configure_plumerising(self, data):
        tornado.log.gen_log.debug('Configuring plumerising')
        data['config'] = data.get('config', {})
        working_dir = os.path.join(
            self.settings['output_root_dir'],
            self.settings['output_url_path_prefix'],
            '{run_id}', 'plumerise')
        data['config']['plumerising'] = {
            "model": "feps",
            "feps": {
                "working_dir": working_dir
            }
        }

    ## Extra Files

    async def _configure_extrafiles(self, data):
        tornado.log.gen_log.debug('Configuring extrafiles')
        data['config'] = data.get('config', {})
        dest_dir = os.path.join(
            self.settings['output_root_dir'],
            self.settings['output_url_path_prefix'],
            '{run_id}', 'csvs'
        )
        data['config']['extrafiles'] = {
            "dest_dir": dest_dir,
            "sets": ["firescsvs", "emissionscsv"],
            "firescsvs": {
                "fire_locations_filename": "fire_locations.csv",
                "fire_events_filename": "fire_events.csv"
            },
            "emissionscsv": {
                "filename": "fire_emissions.csv"
            }
        }

    ## Dispersion

    DEFAULT_HYSPLIT_GRID_LENGTH = 2000

    async def _configure_dispersion(self, data):
        tornado.log.gen_log.debug('Configuring dispersion')
        if (not data.get('config', {}).get('dispersion', {}) or not
                data['config']['dispersion'].get('start') or not
                data['config']['dispersion'].get('num_hours')):
            self._raise_error(400, "dispersion 'start' and 'num_hours' must be specified")
            return

        data['config']['dispersion']['handle_existing'] = "replace"
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
        hy_con = data['config']['visualization']["hysplit"]
        hy_con["images_dir"] = "images/"
        hy_con["data_dir"] = "data/"
        hy_con["create_summary_json"] = True
        hy_con["blueskykml_config"] = hy_con.get("blueskykml_config", {})
        bkml_con = hy_con["blueskykml_config"]
        bkml_con["SmokeDispersionKMLOutput"] = bkml_con.get("SmokeDispersionKMLOutput", {})
        bkml_con["SmokeDispersionKMLOutput"]["INCLUDE_DISCLAIMER_IN_FIRE_PLACEMARKS"] = "False"
        bkml_con["DispersionImages"] = bkml_con.get("DispersionImages", {})
        bkml_con["GreyColorBar"] = {
            "DEFINE_RGB": "true",
            "DATA_LEVELS": "0 1 12 35 55 150 250 350 500 2000",
            "RED": " 0 200 175 150 125 100 75 50 25",
            "GREEN": "0 200 175 150 125 100 75 50 25",
            "BLUE": "0 200 175 150 125 100 75 50 25",
            "IMAGE_OPACITY_FACTOR": "0.7"
        }
        bkml_con["DispersionGridOutput"] = {
            "HOURLY_COLORS": "GreyColorBar,RedColorBar",
            "THREE_HOUR_COLORS": "GreyColorBar,RedColorBar",
            "DAILY_COLORS": "GreyColorBar,RedColorBar"
        }

        # we want daily images produced for all timezones in which fires
        # are located
        if not bkml_con["DispersionImages"].get("DAILY_IMAGES_UTC_OFFSETS"):
            bkml_con["DispersionImages"]["DAILY_IMAGES_UTC_OFFSETS"] = 'auto'
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
                # if handle_existing == 'write_in_place', export
                # fails in shutil.copytree
                "handle_existing": "write_in_place",
                "dest_dir": dest_dir,
                # HACK: to get re-runs to work, we need to
                #  make sure the extra exports dir is unique
                "extra_exports_dir_name": "extras-"+ str(uuid.uuid4())
            }
        }


class RunStatusBase(RequestHandlerBase):

    VERBOSE_FIELDS = ('output_dir', 'modules', 'server', 'export',
        'fires')
    AVERAGE_RUN_TIME_IN_SECONDS = 360 # 6 minutes

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

            # Note: history will always be defined; a run is never
            #  recorded in the db without adding to the history
            # Note: though history should be in reverse chronological order,
            #  there have been cases where, due to the asynchronous wriing of
            #  statuses to monbodb, they end up out of order in the db. The
            #  timestamps, however, reflect the true order.
            run['status'] = sorted(run.pop('history'),
                key=lambda e:e['ts'])[-1]

            #run['complete'] = 'output_url' in run
            run['complete'] = (run['status']['status']
                in (RunStatuses.Completed, RunStatuses.Failed))

            if 'percent' not in run:
                if (run['status']['status'] in
                        (RunStatuses.Enqueued, RunStatuses.Dequeued)):
                    run['percent'] = 0
                elif (run['status']['status'] in
                        (RunStatuses.Completed, RunStatuses.Failed)):
                    run['percent'] = 100
                elif run['status']['status'] == RunStatuses.ProcessingOutput:
                    run['percent'] = 99  # HACK
                else: # RunStatuses.Running
                    self._estimate_percent_for_running(run)

            # prune
            for k in self.VERBOSE_FIELDS:
                run.pop(k, None)

        return run

    def _estimate_percent_for_running(self, run):
        # TODO: figure out how to estimate percentage from
        #   log and stdout information
        try:
            # HACH 1
            i = datetime.datetime.strptime(run['initiated_at'],
                "%Y-%m-%dT%H:%M:%SZ")
            n = datetime.datetime.utcnow()
            p = int(100 * ((n - i).seconds / self.AVERAGE_RUN_TIME_IN_SECONDS))
            run['percent'] = min(98, max(1, p))
        except:
            run['percent'] = 50  # HACK 2



class RunStatus(RunStatusBase):

    @tornado.web.asynchronous
    async def get(self, run_id):
        # TODO: implement using data form mongodb
        run = await self.settings['mongo_db'].find_run(run_id)
        if not run:
            self._raise_error(404, "Run doesn't exist")
        else:
            await self.process(run)
            self.write(run)


class RunsInfo(RunStatusBase):

    @tornado.web.asynchronous
    async def get(self, status=None):
        # default limit to 10, and cap it at 25
        limit = min(int(self.get_query_argument('limit', 10)), 25)
        offset = int(self.get_query_argument('offset', 0))
        runs, total_count = await self.settings['mongo_db'].find_runs(status=status,
            limit=limit, offset=offset)
        for run in runs:
            await self.process(run)

        # TODO: include total count of runs of *all* statuses?
        self.write({
            "runs": runs,
            "count": len(runs),
            "limit": limit,
            "offset": offset,
            "total": total_count
        })


class RunOutput(RequestHandlerBase):

    @tornado.web.asynchronous
    async def get(self, run_id):
        # TODO: implement using data form mongodb
        run = await self.settings['mongo_db'].find_run(run_id)
        if not run:
            self._raise_error(404, "Run doesn't exist")

        elif not run.get('output_url'):
            self._raise_error(404, "Run output doesn't exist")

        else:
            if 'dispersion' in run['modules']:
                #if output['config']['dispersion'].get('model') != 'vsmoke'):
                self._get_dispersion(run)
            elif 'plumerising' in run['modules']:
                self._get_plumerise(run)
            else:
                # TODO: is returning raw input not ok?
                output = self._load_output(run)
                self.write(output)

    ##
    ## Plumerise
    ##

    def _slice(self, info_dict, whitelist):
        # Need to create list of keys in order to pop within iteration
        for k in list(info_dict.keys()):
            if k not in whitelist:
                info_dict.pop(k)

    def _get_plumerise(self, run):
        version_info = run.get('version_info') or {}
        run_info = run if 'fires' in run else self._load_output(run)
        fires = run_info['fires']
        runtime_info = process_runtime(run_info.get('runtime'))

        self.write(dict(run_id=run['run_id'],
            fires=fires,
            runtime=runtime_info,
            version_info=version_info))

    ##
    ## Dispersion
    ##

    def _get_dispersion(self, run):
        r = {
            "root_url": run['output_url'],
            "version_info": run.get('version_info') or {}
        }
        run_info = run if 'export' in run else self._load_output(run)

        # TODO: refine what runtime info is returned
        r['runtime'] = process_runtime(run_info.get('runtime'))

        export_info = run_info['export']

        vis_info = export_info['localsave'].get('visualization')
        if vis_info:
            # images
            self._parse_images(r, vis_info)

            # kmzs
            self._parse_kmzs_info(r, vis_info)

        disp_info = export_info['localsave'].get('dispersion')
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
            self._raise_error(404, msg)

        # use join instead of os.path.join in case output_location is a remote url
        output_json_file = '/'.join([output_location.rstrip('/'), 'output.json'])
        if not exists_func(output_json_file):
            msg = "Output file doesn't exist: {}".format(output_json_file)
            self._raise_error(404, msg)

        with open_func(output_json_file) as f:
            try:
                j = f.read()
                if hasattr(j, 'decode'):
                    j = j.decode()
                return json.loads(j)
                # TODO: set fields here, using , etc.
            except:
                msg = "Failed to open output file: {}".format(output_json_file)
                self._raise_error(500, msg)

