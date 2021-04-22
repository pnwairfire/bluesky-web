"""blueskyweb.lib.runs.execute"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import datetime
import json
import os
import re
import requests
import uuid
import traceback

import tornado.log
import tornado.web

from bluesky.marshal import Blueskyv4_0To4_1
from bluesky.models import fires

from blueskymongo.client import RunStatuses
from blueskyweb.lib import met, hysplit
from blueskyweb.lib.runs import output
from blueskyworker.tasks import (
    run_bluesky, BlueSkyRunner, apply_output_processor, OUTPUT_PROCESSORS
)

__all__ = [
    "BlueSkyRunExecutor",
    "ExecuteMode"
]

def pre_process_v1(data, handle_error):
    if 'fire_information' not in data:
        handle_error(400, "'fire_information' not specified")

    fires = data.pop('fire_information')
    data['fires'] = Blueskyv4_0To4_1().marshal(fires)

PRE_PROCESSORS = {
    '1': pre_process_v1
}

class ExecuteMode(object):
    IN_PROCESS = 1
    ASYNC = 2

class BlueSkyRunExecutor(object):

    def __init__(self, api_version, mode, archive_id, handle_error_func,
            output_stream, settings, hysplit_query_params):
        self.api_version = api_version
        self.mode = mode
        self.archive_id = archive_id # may be None
        self.archive_info = met.db.get_archive_info(archive_id)
        self.handle_error = handle_error_func
        self.output_stream = output_stream
        self.settings = settings
        self.hysplit_query_params = hysplit_query_params

    async def execute(self, data, execute_mode=None):
        # TODO: should no configuration be allowed at all?  or only some? if
        #  any restrictions, check here or check in specific _configure_*
        #  methods, below

        if self.api_version in PRE_PROCESSORS:
            PRE_PROCESSORS[self.api_version](data, self.handle_error)

        if 'fires' not in data:
            self.handle_error(400, "'{}' not specified".format(self.fires_key))
            return

        self._set_run_id_and_name(data)

        try:
            self._set_modules(data)

            f = await self._configure_and_get_run_func(data, execute_mode)

            tornado.log.gen_log.debug("BSP input data (before modules and"
                " config are popped, and run_id is set, in BlueSkyRunner): %s",
                json.dumps(data))
            await f(data)

        except tornado.web.Finish as e:
            # this was intentionally raised; re-raise it
            raise

        except Exception as e:
            # IF exceptions aren't caught, the traceback is returned as
            # the response body
            tornado.log.gen_log.debug(traceback.format_exc())
            self.handle_error(500, str(e), exception=e)

    ##
    ## Helpers
    ##

    async def _configure_and_get_run_func(self, data, execute_mode):
        # TODO: check data['modules'] specifically for 'localmet',
        # 'dispersion', 'visualization' (and 'export'?)
        if self.mode not in ('fuelbeds', 'emissions'):
            # plumerise or dispersion (Hysplit or VSMOKE) request
            for m in data['modules']:
                f = getattr(self, '_configure_{}'.format(m), None)
                if f:
                    await f(data)

            # TODO: configure anything else (e.g. setting archive_id where
            #  appropriate)

            # This should only ever use _run_in_process in dev ad hoc
            # testing; otherwise, if should always be run asynchronously
            return (self._run_in_process
                if execute_mode == ExecuteMode.IN_PROCESS
                else self._run_asynchronously)

        else:
            await self._configure_fuelbeds(data)
            await self._configure_emissions(data)

            # fuelbeds or emissions request; default is to run in process
            return (self._run_asynchronously
                if execute_mode == ExecuteMode.ASYNC
                else self._run_in_process)


    RUN_ID_SUFFIX_REMOVER = re.compile('-(plumerise|dispersion)$')

    def _set_run_id_and_name(self, data):
        # run_id is only necessary if running asynchronously, but it doesn't
        # hurt to set it anyway; it's needed in configuring dispersion, so
        # it has to be set before _run_asynchronously
        if not data.get('run_id'):
            data['run_id'] = str(uuid.uuid1())
        tornado.log.gen_log.info("%s request for run id: %s", self.mode,
            data['run_id'])

        # This is really just for PGv3 runs
        if self.RUN_ID_SUFFIX_REMOVER.search(data['run_id']):
            for f in data["fires"]:
                f['event_of'] = f.get('event_of', {})
                if not f['event_of'].get('name'):
                    name = 'Scenario Id {}'.format(
                        self.RUN_ID_SUFFIX_REMOVER.sub('', data['run_id']))
                    f['event_of']['name'] = name

    MODULES = {
        'fuelbeds': {
            'default': ['fuelbeds']
        },
        'emissions': {
            'default': ['ecoregion', 'consumption', 'emissions'],
            'other_allowed': ['fuelbeds']
        },
        # TODO: for dispersion requests, instead of running findmetdata, get
        #   met data from indexed met data in mongodb;  maybe fall back on
        #   running findmetdata if indexed data isn't there or if mongodb
        #   query fails
        'met_dispersion': {
            'default': ['findmetdata', 'extrafiles',
                'dispersion', 'visualization', 'export']
        },
        'metless_dispersion': {
            'default': ['dispersion', 'export']
        },
    }

    def _plumerise_modules(self, data, exclude_extrafiles=False):
        modules = []

        # just look at first active area of first fire
        if 'timeprofile' not in data['fires'][0]['activity'][0]['active_areas'][0]:
            modules.append('timeprofile')

        modules.append('plumerise')

        if not exclude_extrafiles:
            modules.append('extrafiles')

        return modules

    def _set_modules(self, data):
        def _set(default_modules, other_allowed=None):
            other_allowed  = other_allowed or []
            if "modules" in data:  #data.get('modules'):
                invalid_modules = set(data['modules']).difference(
                    default_modules + other_allowed)
                if invalid_modules:
                    self.handle_error(400, "invalid module(s) for {} "
                        "request: {}".format(self.mode, ','.join(invalid_modules)))
                    return
                # else, leave as is
            else:
                data['modules'] = default_modules


        if self.mode in ('dispersion', 'all'):
            dispersion_modules = (self.MODULES['met_dispersion']['default']
                if self.archive_id else self.MODULES['metless_dispersion']['default'])
            if self.mode == 'all':
                if self.archive_id:
                    _set(self.MODULES['fuelbeds']['default'] +
                        self.MODULES['emissions']['default'] +
                        self._plumerise_modules(data, exclude_extrafiles=(
                            'extrafiles' in dispersion_modules)) +
                        dispersion_modules)
                else:
                    _set(self.MODULES['fuelbeds']['default'] +
                        self.MODULES['emissions']['default'] +
                        # vsmoke needs timeprofile but not plumerise
                        ['timeprofile'] +
                        dispersion_modules)
            else:
                _set(dispersion_modules)
        elif self.mode == 'plumerise':
            _set(self._plumerise_modules(data))
        elif self.mode in ('fuelbeds', 'emissions'):
            _set(self.MODULES[self.mode]['default'],
                self.MODULES[self.mode].get('other_allowed'))
        # There are no other possibilities for self.mode

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


    async def _run_asynchronously(self, data):
        await self._check_for_existing_run_id(data['run_id'])

        queue_name = self.archive_id or 'no-met'
        if self.mode == 'plumerise':
            queue_name += '-plumerise'

        #tornado.log.gen_log.debug('input: %s', data)
        args = (data, self.api_version)

        # TODO: figure out how to enqueue without blocking
        settings = {k:v for k, v in self.settings.items() if k != 'mongo_db'}
        tornado.log.gen_log.debug("About to enqueue run %s",
            data.get('run_id'))
        run_bluesky.apply_async(args=args, kwargs=settings, queue=queue_name)
        # TODO: specify callback in record_run, calling
        #    self.output_stream.write in callback, so we can handle failure?
        self.settings['mongo_db'].record_run(data['run_id'],
            RunStatuses.Enqueued, queue=queue_name, modules=data["modules"],
            initiated_at=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
        self.output_stream.write({"run_id": data['run_id']})

    async def _run_in_process(self, data):
        # We need the outer try block to handle any exception raised
        # before the bluesky thread is started. If an exception is
        # encountered in the seperate thread, it's handling
        try:
            output_stream = apply_output_processor(self.api_version,
                self.output_stream)
            # Runs bluesky in a separate thread so that run configurations
            # don't overwrite each other. (Bluesky manages configuration
            # with a singleton that stores config data in thread local)
            # BlueSkyRunner will call self.output_stream.write.
            t = BlueSkyRunner(data, output_stream=output_stream)
            t.start()
            # block until it thread completes so that self.output_stream.write
            # is called before the main thread exits and so that we can return
            # 500 if necessary
            t.join()
            if t.exception:
                self.handle_error(500, str(t.exception),
                    exception=t.exception)

        except Exception as e:
            tornado.log.gen_log.debug(traceback.format_exc())
            self.handle_error(500, str(e), exception=e)

    ##
    ## Configuration
    ##

    ## Fuelbeds

    async def _configure_fuelbeds(self, data):
        tornado.log.gen_log.debug('Configuring fuelbeds')
        data['config'] = data.get('config', {})
        data['config']['fuelbeds'] = data['config'].get('fuelbeds', {})
        data['config']['fuelbeds']['ignored_fuelbeds'] = []

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
            met_root_dir = await met_archives_db.get_root_dir(self.archive_id)
        except met.db.UnavailableArchiveError as e:
            msg = "Archive unavailable: {}".format(self.archive_id)
            self.handle_error(404, msg)

        data['config']['findmetdata'] = {
            "met_root_dir": met_root_dir,
            "arl": {
                "index_filename_pattern":
                    self.archive_info['arl_index_file']
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

    async def _configure_plumerise(self, data):
        tornado.log.gen_log.debug('Configuring plumerise')
        data['config'] = data.get('config', {})
        working_dir = os.path.join(
            self.settings['output_root_dir'],
            self.settings['output_url_path_prefix'],
            '{run_id}', 'plumerise')
        data['config']['plumerise'] = {
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
            "sets": ["firescsvs"],
            "firescsvs": {
                "fire_locations_filename": "fire_locations.csv",
                "fire_events_filename": "fire_events.csv"
            }

        }
        # only write emissions csv if emissions is one of the modules to run
        # or if fire data includes emissions
        if self._include_emissionscsv(data):
            data['config']['extrafiles']["sets"].append("emissionscsv")
            data['config']['extrafiles']["emissionscsv"] = {
                "filename": "fire_emissions.csv"
            }

    def _include_emissionscsv(self, data):
        if 'emissions' in data['modules']:
            return True

        locations_defined = False
        for f in data['fires']:
            for loc in fires.Fire(f).locations:
                locations_defined = True
                if not loc.get('fuelbeds') or any(
                        [not fb.get('emissions') for fb in loc['fuelbeds']]):
                    return False

        # there are fire locations defined, and all have emissions data
        return locations_defined

    ## Dispersion

    DEFAULT_HYSPLIT_GRID_LENGTH = 2000

    async def _configure_dispersion(self, data):
        tornado.log.gen_log.debug('Configuring dispersion')
        if (not data.get('config', {}).get('dispersion', {}) or not
                data['config']['dispersion'].get('start') or not
                data['config']['dispersion'].get('num_hours')):
            self.handle_error(400, "dispersion 'start' and 'num_hours' must be specified")
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

        if not self.archive_id:
            data['config']['dispersion']['model'] = 'vsmoke'

        if data['config']['dispersion'].get('model') in ('hysplit', None):
            configurator = hysplit.HysplitConfigurator(
                self.hysplit_query_params, self.handle_error,
                data, self.archive_info)
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
            "HOURLY_COLORS_PM25": "GreyColorBar,RedColorBar",
            "THREE_HOUR_COLORS_PM25": "GreyColorBar,RedColorBar",
            "DAILY_COLORS_PM25": "GreyColorBar,RedColorBar"
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

        extras = ["dispersion", "visualization"] if self.archive_id else ["dispersion"]
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
