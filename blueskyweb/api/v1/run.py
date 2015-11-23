"""bluesky.web.api.v1.run"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import copy
import io
import json
import logging
import os
import uuid
import tornado.web
import traceback

#from bluesky.web.lib.auth import b_auth
from bluesky import modules, models, process
from bluesky.exceptions import BlueSkyImportError, BlueSkyModuleError

# TODO: import vs call executable?
from bsslib.scheduling.schedulers.bsp.runs import BspRunScheduler


## ***
## *** TODO: REPLACE HARDCODED MET DATA WITH REAL!!!
## ***
## *** Will need to add configuration options to web service to point
## *** to source of data (e.g. url of mongodb containing the data vs.
## *** root url or path to crawl for data vs. something else...)
## ***
# TODO: not sure where is the best place to define queues...maybe they should be
#  defined in bsslib?...or let them be defined as env vars with defaults
DOMAINS = {
    'DRI2km': {
        'queue': 'dri', # TODO: define elsewhere ? (see above)
        'met_root_dir': '/DRI_2km/' # TODO: don't hardcode (see above)
    },
    'NAM84': {
        'queue': 'nam', # TODO: define elsewhere ? (see above)
        'met_root_dir': '/NAM84/' # TODO: don't hardcode (see above)
    }
}

EXPORT_CONFIGURATIONS = {
    "localsave": {
        "dest_dir": (os.environ.get('BSPWEB_EXPORT_LOCALSAVE_DEST_DIR')
            or "/bluesky/playground-output/"),  # TODO: fill in appropriate default
        "url_root_dir": (os.environ.get('BSPWEB_EXPORT_LOCALSAVE_URL_ROOT_DIR')
            or "/playground-output/"),
        # host will be set to hostname in api request if not defined in env var
        "host": os.environ.get('BSPWEB_EXPORT_LOCALSAVE_HOST'),

    },
    "upload": {
        "scp": {
            "user": os.environ.get('BSPWEB_EXPORT_UPLOAD_SCP_USER') or "bluesky",
            # host will be set to hostname in api request if not defined in env var
            "host": os.environ.get('BSPWEB_EXPORT_UPLOAD_SCP_HOST'),
            "port": os.environ.get('BSPWEB_EXPORT_UPLOAD_SCP_PORT') or 22,
            "dest_dir": (os.environ.get('BSPWEB_EXPORT_UPLOAD_SCP_DEST_DIR')
                or "/bluesky/playground-output/"),
            "url_root_dir": (os.environ.get('BSPWEB_EXPORT_UPLOAD_SCP_URL_ROOT_DIR')
                or "/playground-output/")
        }
    }
}
# TODO: change default export mode to 'upload' once fab tasks support setting the mode
EXPORT_MODE = (os.environ.get('BSPWEB_EXPORT_MODE') or 'localsave').lower()
if EXPORT_MODE not in EXPORT_CONFIGURATIONS:
    raise ValueError("Invalid value for BSPWEB_EXPORT_MODE - {}. Must be one"
        " of the following: {}".format(EXPORT_MODE,
        ', '.join(EXPORT_CONFIGURATIONS.keys())))
EXPORT_CONFIGURATION = EXPORT_CONFIGURATIONS[EXPORT_MODE]

# TODO: require host to be specified if uploading?
# if EXPORT_MODE == "upload" and not EXPORT_CONFIGURATION['scp']['host']:
#     raise ValueError("Specify scp host for upload")

class RunHandlerBase(tornado.web.RequestHandler):

    def _get_host(self):
        return self.request.host

class RunExecuter(RunHandlerBase):

    def post(self, domain=None):
        if domain and domain not in DOMAINS:
            self.set_status(404, 'Bad request: Unrecognized domain')
            return

        if not self.request.body:
            self.set_status(400, 'Bad request: empty post data')
            return

        data = json.loads(self.request.body)
        if "fire_information" not in data:
            self.set_status(400, "Bad request: 'fire_information' not specified")
        if "modules" in data:
            self.set_status(400, "Bad request: Don't specify modules")

        try:
            if domain:
                data['modules'] = ['timeprofiling', 'findmetdata', 'localmet',
                    'plumerising', 'dispersion', 'visualization', 'export']
                self._configure_findmetdata(data, domain)
                self._configure_dispersion(data, domain)
                self._configure_visualization(data, domain)
                # TODO: configure anything else (e.g. setting domain where
                #  appropriate)
                self._run_asynchronously(data, domain=domain)
            else:
                data['modules'] = ['ingestion', 'fuelbeds', 'consumption', 'emissions']
                if self.get_query_argument('run_asynch', default=None) is not None:
                    self._run_asynchronously(data)
                else:
                    self._run_in_process(data)

        except Exception, e:
            # IF exceptions aren't caught, the traceback is returned as
            # the response body
            logging.debug(traceback.format_exc())
            logging.error('Exception: {}'.format(e))
            self.set_status(500)

    ## Helpers

    # def _bad_request(self, msg):
    #     self.set_status(400)
    #     self.write({"error": msg})

    def _run_asynchronously(self, data, domain=None):

        if not data.get('run_id'):
            data['run_id'] = str(uuid.uuid1())

        self._configure_export(data)

        # TODO: determine appropriate queue from met domain
        queue_name = DOMAINS.get(domain, {}).get('queue') or 'all-met'

        # TODO: import vs call bss-scheduler?
        # TODO: dump data to json?  works fine without doing so, so this may
        #  only serve the purpose of being able to read data in scheduler ui
        BspRunScheduler().schedule(queue_name, data)
        self.write({"run_id": data['run_id']})

    def _run_in_process(self, data):
        fires_manager = models.fires.FiresManager()
        try:
            fires_manager.load(data)
            fires_manager.run()
        except BlueSkyModuleError, e:
            # Exception was caught while running modules and added to
            # fires_manager's meta data, and so will be included in
            # the output data
            # TODO: should module error not be reflected in http error status?
            pass
        except BlueSkyImportError, e:
            self.set_status(400, "Bad request: {}".format(e.message))
        except Exception, e:
            logging.error('Exception: {}'.format(e))
            self.set_status(500)

        # If you pass a dict into self.write, it will dump it to json and set
        # content-type to json;  we need to specify a json encoder, though, so
        # we'll manaually set the header adn dump the json
        self.set_header('Content-Type', 'application/json') #; charset=UTF-8')
        fires_manager.dumps(output_stream=self)

    def _configure_findmetdata(self, data, domain):
        data['config'] = data.get('config', {})
        data['config']['findmetdata'] = {
            "met_root_dir": DOMAINS[domain]['met_root_dir']
        }
    def _configure_dispersion(self, data, domain):
        # TODO: allow some config in data?  maybe *expect* some in data (like
        #   start and end dates)?
        # TODO: set grid and grid spacing? based on what's in
        #   api.v1.domain.DUMMY_DOMAIN_DATA or what's in redis/mongodb...
        #   *or* is dispersion grid independent of met grid (e.x. it can be a
        #   smaller region within met domain)
        # TODO: set dest_dir, etc?
        pass

    def _configure_visualization(self, data, domain):
        # TODO: set dest_dir, etc?
        pass


    def _configure_export(self, data):
        # only allow email export to be specified nin request
        if 'export' in data['modules']:
            if set(data.get('config', {}).get('export', {}).get('modes', [])) - set(['email']):
                self.set_status(400, "Bad request: only 'email' export mode allowed")
                return
            # Make sure 'export' module is executed only once, at that it
            # happens at the end
            data['modules'] = [e for e in data['modules'] if e != 'export'] + ['export']
        else:
            data['modules'].append('export')

        # add upload export, configured to scp
        # Note: we need to use 'upload' export, esince we don't know where bsp workers
        #  will be run.  The bsp code should (or at least will) dynamically switch
        #  to saving locally instead of scp'ing if the hostname of the server it's running
        #  on is the sam
        data['config'] = data.get('config', {})
        data['config']['export'] = data['config'].get('export', {})
        data['config']['export']['modes'] = data['config']['export'].get('modes', [])
        data['config']['export']['modes'].append(EXPORT_MODE)
        data['config']['export']['extra_exports'] = ["dispersion", "visualization"]
        # TODO: no real need to copy.deepcopy
        data['config']['export'][EXPORT_MODE] = copy.deepcopy(EXPORT_CONFIGURATION)
        if EXPORT_MODE == 'upload':
            if not data['config']['export']['upload']['scp']['host']:
                data['config']['export']['upload']['scp']['host'] = self._get_host()
        elif EXPORT_MODE == 'localsave':
            # TODO: set any values?
            pass

        # TODO: update bsp to allow configuring export to exclude absolute
        #   output dir (at least for 'localsave', for 'upload' too if
        #   necessary), and configure it to do so

class RunStatus(RunHandlerBase):

    def get(self, run_id):
        # This simply looks for the existence of output
        # TODO: actually look for status
        if EXPORT_MODE == 'upload':
            # TODO: use EXPORT_CONFIGURATIONS along with _get_host to find out where
            #   to look for output
            self.set_status(501, "Not yet able to check on status of uploaded output")
            return
        else:
            # if bsp workers are on another machine, this will never return an
            # accurate response. ('localsave' should only be used when running
            # everything on one server)
            output_dir = os.path.join(EXPORT_CONFIGURATION['dest_dir'], run_id)
            if os.path.exists(output_dir):
                output_json_file = os.path.join(output_dir, 'output.json')
                failed = True
                if os.path.exists(output_json_file):
                    with open(output_json_file) as f:
                        try:
                            output_json = json.loads(f.read())
                            failed = "error" in output_json
                        except:
                            pass
                self.write({
                    "complete": True,
                    "percent": 100.0,
                    "failed": failed
                    # TODO: include 'message'
                })
            else:
                self.write({
                    "complete": False,
                    "percent": 0.0  # TODO: determine % from output directories
                    # TODO: include 'message'
                })

class RunOutput(RunHandlerBase):

    def _parse_output(output_json):
        export_info = output_json.get('export', {}).get(EXPORT_MODE)
        if not export_info:
           return {}

        r = {}
        vis_info = export_info.get('visualization')
        if vis_info:
            # images
            images_info = vis_info.get('images', {})
            if images_info:
                r['images'] = {
                    "hourly": ['{}/{}'.format(vis_info['sub_directory'], e)
                        for e in images_info.get('hourly', [])],
                    "daily": {
                        "average": ['{}/{}'.format(vis_info['sub_directory'], e)
                            for e in images_info.get('daily', {}).get('average', [])],
                        "maximum": ['{}/{}'.format(vis_info['sub_directory'], e)
                            for e in images_info.get('daily', {}).get('maximum', [])],
                    }
                }
            # kmzs
            kmz_info = vis_info.get('kmzs', {})
            if kmz_info:
                r['kmzs'] = {k: '{}/{}'.format(vis_info['sub_directory'], v)
                    for k, v in kmz_info.items() if k in ('fire', 'smoke')}

        disp_info = export_info.get('dispersion')
        if disp_info:
            r.update(**{k: disp_info[k.lower()] for k in ('netCDF', 'netCDFs')
                if k.lower() in disp_info})

        # TODO: list fire_*.csv if specified in output_json

        return r

    def get(self, run_id):
        if EXPORT_MODE == 'upload':
            # TODO: use EXPORT_CONFIGURATIONS along with _get_host to find out where
            #   to look for output
            self.set_status(501, "Not yet able to check on status of uploaded output")
            return
        else:
            # if bsp workers are on another machine, this will never return an
            # accurate response. ('localsave' should only be used when running
            # everything on one server)
            output_dir = os.path.join(EXPORT_CONFIGURATION['dest_dir'], run_id)
            if not os.path.exists(output_dir):
                self.set_status(404)
            else:
                r = {
                    "root_url": "{}://{}{}".format(
                        self.request.protocol,
                        # TODO: use self.request.remote_ip instead of self.request.host
                        # TODO: call _get_host
                        EXPORT_CONFIGURATION['host'] or self.request.host,
                        EXPORT_CONFIGURATION['url_root_dir'])
                }
                output_json_file = os.path.join(output_dir, 'output.json')
                if os.path.exists(output_json_file):
                    with open(output_json_file) as f:
                        try:
                            r.update(self._parse_output(json.loads(f.read())))
                            # TODO: set fields here, using , etc.
                        except:
                            pass

                self.write(r)
