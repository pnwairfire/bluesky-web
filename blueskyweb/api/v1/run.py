"""blueskyweb.api.v1.run"""

# TODO: replace each reference to domains.DOMAINS with call
#   to some method (to be implemented) in domains.DomainDB or to
#   a module level function in domains wrapping the hardcoded data

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import copy
import io
import json
import logging
import os
import re
import requests
import socket
import urllib2
import uuid
import tornado.web
import tornado.log
import traceback

# TODO: import vs call executable?
from bsslib.scheduling.schedulers.bsp.runs import BspRunScheduler
from bsslib.jobs.bsp import _launch as _launch_bsp

from blueskyweb.lib import domains

# TODO: pass configuration settings into bsp-web (and on to
#   blueskyweb.app.main) as arg options rather than as env vars ?


EXPORT_CONFIGURATIONS = {
    "localsave": {
        "dest_dir": (os.environ.get('BSPWEB_EXPORT_LOCALSAVE_DEST_DIR')
            or "/bluesky/playground-output/"),  # TODO: fill in appropriate default
        "url_root_dir": (os.environ.get('BSPWEB_EXPORT_LOCALSAVE_URL_ROOT_DIR')
            or "/playground-output/"),
        # host will be set to hostname in api request if not defined in env var
        "host": os.environ.get('BSPWEB_EXPORT_LOCALSAVE_HOST')
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


##
## Utilities for working with remote output
##

class remote_open(object):
    """Context manager that clones opens remote file and closes it on exit
    """

    def __init__(self, url):
        self.url = url

    def __enter__(self):
        self.f = urllib2.urlopen(self.url)
        return self.f

    def __exit__(self, type, value, traceback):
        self.f.close()

def remote_exists(url):
    return requests.head(url).status_code != 404

def get_output_url(run_id):
    return "http://{}".format(
        os.path.join(EXPORT_CONFIGURATION["scp"]["host"],
        EXPORT_CONFIGURATION["scp"]["url_root_dir"].strip('/'),
        run_id))

PORT_IN_HOSTNAME_MATCHER = re.compile(':\d+')
def is_same_host(web_request_host):
    """Checks to see if the uploaded exports are local to the web service

    If they are local, the run status and output APIS can carry out their
    checks more efficiently and quickly.

    This function is a complete hack, but it works, at least some of the time.
    (And when it fails, it should only result in false negatives, which
    don't affect the correctness of the calling APIs - it just means they
    don't take advantage of working with local files.)
    """
    # first check if same hostname
    try:
        web_service_host = socket.gethostbyaddr(socket.gethostname())[0]
    except:
        web_service_host = PORT_IN_HOSTNAME_MATCHER.sub('', web_request_host)
    if EXPORT_CONFIGURATION["scp"]["host"] == web_service_host:
        return True

    # TODO: determine ip address of upload host and web service host and
    #   check if ip addresses match

    return False

###
### API Handlers
###

class RunHandlerBase(tornado.web.RequestHandler):

    def _get_host(self):
        return self.request.host

class RunExecuter(RunHandlerBase):

    def post(self, mode=None, domain=None):
        if domain and domain not in domains.DOMAINS:
            self.set_status(404, 'Bad request: Unrecognized domain')
            return

        if not self.request.body:
            self.set_status(400, 'Bad request: empty post data')
            return

        data = json.loads(self.request.body)
        if "fire_information" not in data:
            self.set_status(400, "Bad request: 'fire_information' not specified")
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
            self._set_modules(domain, mode, data)

            # TODO: check data['modules'] specifically for 'localmet',
            # 'dispersion', 'visualization' (and 'export'?)
            if mode not in ('fuelbeds', 'emissions'):
                # Hysplit or VSMOKE request
                for m in data['modules']:
                    # 'export' module is configured in _run_asynchronously
                    if m != 'export':
                        f = getattr(self, '_configure_{}'.format(m), None)
                        if f:
                            f(data, domain)

                # TODO: configure anything else (e.g. setting domain where
                #  appropriate)
                #logging.debug("BSP input data: %s", json.dumps(data))
                self._run_asynchronously(data, domain=domain)

            else:
                # fuelbeds or emissions request
                if self.get_query_argument('_a', default=None) is not None:
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

    FUELBEDS_MODULES = [
        'ingestion', 'fuelbeds'
    ]
    EMISSIONS_MODULES = [
        'consumption', 'emissions'
    ]
    # Note: export module is added in _configure_export when necessary
    # TODO: for hysplit requests, instead of running findmetdata, get
    #   met data from indexed met data in mongodb;  maybe fall back on running
    #   findmetdata if indexed data isn't there or if mongodb query
    #   fails or if web service isn't configured with mongodb
    MET_DISPERSION_MODULES = [
        'timeprofiling', 'findmetdata', 'localmet',
        'plumerising', 'dispersion', 'visualization'
    ]
    METLESS_DISPERSION_MODULES = [
        'timeprofiling', 'dispersion'
    ]

    def _set_modules(self, domain, mode, data):
        def _set(default_modules):
            if "modules" in data:  #data.get('modules'):
                invalid_modules = set(data['modules']).difference(
                    default_modules)
                if invalid_modules:
                    self.set_status(400, "Bad request: invalid module(s) for "
                        "emissions request: {}".format(','.join(invalid_modules)))
                    self.finish()
                # else, leave as is
            else:
                data['modules'] = default_modules


        if mode in ('dispersion', 'all'):
            dispersion_modules = (self.MET_DISPERSION_MODULES
                if domain else self.METLESS_DISPERSION_MODULES)
            if mode == 'all':
                _set(self.FUELBEDS_MODULES + self.EMISSIONS_MODULES +
                    dispersion_modules)

            else:
                _set(dispersion_modules)
        elif mode == 'emissions':
            _set(self.EMISSIONS_MODULES)
        elif mode == 'fuelbeds':
            _set(self.FUELBEDS_MODULES)
        # There are no other possibilities for mode

        logging.debug("Modules be run: {}".format(', '.join(data['modules'])))


    # def _bad_request(self, msg):
    #     self.set_status(400)
    #     self.write({"error": msg})

    def _run_asynchronously(self, data, domain=None):

        self._configure_export(data, domain is not None)

        queue_name = domains.DOMAINS.get(domain, {}).get('queue') or 'all-met'

        # TODO: import vs call bss-scheduler?
        # TODO: dump data to json?  works fine without doing so, so this may
        #  only serve the purpose of being able to read data in scheduler ui
        tornado.log.gen_log.debug('input: %s', data)
        BspRunScheduler().schedule(queue_name, data)
        self.write({"run_id": data['run_id']})

    def _run_in_process(self, data):
        try:
            tornado.log.gen_log.debug('input: %s', data)
            stdout_data, stderr_data = _launch_bsp(data, capture_output=True)
            # TODO: make sure stdout_data is valid json?
            tornado.log.gen_log.debug('output: %s', stdout_data)
            self.write(stdout_data)

        # TODO: return 404 if output has error related to bad module, etc.
        except Exception, e:
            logging.error('Exception: {}'.format(e))
            self.set_status(500)


    def _configure_findmetdata(self, data, domain):
        logging.debug('Configuring findmetdata')
        data['config'] = data.get('config', {})
        data['config']['findmetdata'] = {
            "met_root_dir": domains.DOMAINS[domain]['met_root_dir'],
            "arl": {
                "index_filename_pattern":
                    domains.DOMAINS[domain]['index_filename_pattern'],
                "fewer_arl_files": True
            }
        }

    def _configure_localmet(self, data, domain):
        logging.debug('Configuring localmet')
        data['config'] = data.get('config', {})
        data['config']['localmet'] = {
            "time_step": domains.DOMAINS[domain]['time_step']
        }

    def _configure_plumerising(self, data, domain):
        logging.debug('Configuring plumerising')
        data['config'] = data.get('config', {})
        data['config']['plumerising'] = {
            "model": "sev"
        }

    DEFAULT_HYSPLIT_GRID_LENGTH = 2000

    def _configure_dispersion(self, data, domain):
        logging.debug('Configuring dispersion')
        if (not data.get('config', {}).get('dispersion', {}) or not
                data['config']['dispersion'].get('start') or not
                data['config']['dispersion'].get('num_hours')):
            self.set_status(400,
                "Bad request: dispersion 'start' and 'num_hours' must be specified")
            return

        data['config']['dispersion']['output_dir'] = os.path.join(
            os.path.dirname(EXPORT_CONFIGURATION['dest_dir'].rstrip('/')),
            'bsp-dispersion-output', '{run_id}')
        data['config']['dispersion']['working_dir'] = os.path.join(
            os.path.dirname(EXPORT_CONFIGURATION['dest_dir'].rstrip('/')),
            'bsp-dispersion-working', '{run_id}')
        logging.debug("Output dir: %s", data['config']['dispersion']['output_dir'])
        logging.debug("Working dir: %s", data['config']['dispersion']['working_dir'])

        if not domain:
            data['config']['dispersion']['model'] = 'vsmoke'

        # TODO: if data['config']['dispersion']['hysplit']['grid'] is not defined
        #   *and* if grid isn't defined in hardcoded data, then raise exception
        if data['config']['dispersion'].get('model') in ('hysplit', None):
            if not data['config']['dispersion'].get('hysplit'):
                data['config']['dispersion']['hysplit'] = {}

            # configure grid spacing if it's not already set in request
            if not any([
                    data['config']['dispersion']['hysplit'].get(k) or
                    data['config']['dispersion']['hysplit'].get(k.lower())
                    for k in ('GRID', 'USER_DEFINED_GRID', 'COMPUTE_GRID')]):
                met_boundary = domains.get_met_boundary(domain)
                if len(data['fire_information']) != 1:
                    # just use met domain
                    data['config']['dispersion']['hysplit']["USER_DEFINED_GRID"] = True
                    data['config']['dispersion']['hysplit'].update(
                        {k.upper(): v for k, v in met_boundary.items()})
                else:
                    data['config']['dispersion']['hysplit'].update({
                        "compute_grid": True,
                        "spacing_latitude": met_boundary["spacing_latitude"],
                        "spacing_longitude": met_boundary["spacing_longitude"],
                        "projection": met_boundary["projection"],
                        "NUMPAR": 1000,
                        "MAXPAR": 10000000,
                        "VERTICAL_EMISLEVELS_REDUCTION_FACTOR": 5,
                        "VERTICAL_LEVELS": [100],
                        "INITD": 0,
                        "NINIT": 0,
                        "DELT": 0.0,
                        "KHMAX": 72, # number of hours after which particles are removed
                        "MPI": True,
                        "NCPUS": 4
                    })

            logging.debug("hysplit configuration: %s", data['config']['dispersion']['hysplit'])

        # TODO: any other model-specific configuration?

    def _configure_visualization(self, data, domain):
        logging.debug('Configuring visualization')
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
        logging.debug('visualization config: %s', data['config']['visualization'])
        # TODO: set anything else?

    def _configure_export(self, data, include_visualization):
        logging.debug('Configuring export')
        # only allow email export to be specified nin request
        if 'export' in data['modules']:
            if set(data.get('config', {}).get('export', {}).get('modes', [])) - set(['email']):
                self.set_status(400, "Bad request: only 'email' export mode allowed")
                return
            # Make sure 'export' module is executed only once, and that it
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
        data['config']['export']['extra_exports'] = ["dispersion"]
        if include_visualization:
            data['config']['export']['extra_exports'].append("visualization")
        # TODO: no real need to copy.deepcopy
        data['config']['export'][EXPORT_MODE] = copy.deepcopy(EXPORT_CONFIGURATION)

        # ***** BEGIN -- TODO: DELETE ONCE 'v1' is removed
        try:
            image_results_version = self.get_argument('image_results_version')
            if image_results_version:
                logging.debug('Setting image_results_version: %s',
                    image_results_version)
                data['config']['export'][EXPORT_MODE]['image_results_version'] = image_results_version
        except tornado.web.MissingArgumentError:
            logging.debug('image_results_version not specified')
            pass
        # ***** END

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

    ## Generic status check method

    def _check(self, output_location, exists_func, open_func):
        """Checks output, which may be in local dir or on remote host

        args:
         - output_location -- local pathname or url
         - exists_func -- function to check existence of dir or file
            (local or via http)
         - open_func -- function to open output json file (local or via http)
        """
        if exists_func(output_location):
            logging.debug('%s exists', output_location)
            # use join instead of os.path.join in case output_location is a remote url
            output_json_file = '/'.join([output_location.rstrip('/'), 'output.json'])
            logging.debug('checking %s', output_json_file)
            failed = True  ## TODO: REMOVE
            status = "Unknown"
            if exists_func(output_json_file):
                logging.debug('%s exists', output_json_file)
                with open_func(output_json_file) as f:
                    try:
                        output_json = json.loads(f.read())
                        if "error" in output_json: #[str(k) for k in output_json]:
                            failed = True  ## TODO: REMOVE
                            status = "Failure"
                        else:
                            failed = False  ## TODO: REMOVE
                            status = "Success"
                    except:
                        # Note that status is already defaulted to "Unknown"
                        pass
            self.write({
                "complete": True,
                "percent": 100.0,
                "failed": failed,  ## TODO: REMOVE
                "status": status
                # TODO: include 'message'
            })
        else:
            logging.debug('%s does *NOT* exists', output_location)
            self.write({
                "complete": False,
                "percent": 0.0,  # TODO: determine % from output directories
                "status": "Unknown"
                # TODO: include 'message'
            })

    ## Localsave

    def _check_localsave(self, run_id):
        # if bsp workers are on another machine, this will never return an
        # accurate response. ('localsave' should only be used when running
        # everything on one server)
        output_dir = os.path.join(EXPORT_CONFIGURATION['dest_dir'], run_id)
        self._check(output_dir, os.path.exists, open)

    ## Upload

    def _check_upload(self, run_id):
        if is_same_host(self.request.host):
            logging.debug("Uploaded export is local")
            EXPORT_CONFIGURATION['dest_dir'] = EXPORT_CONFIGURATION['scp']['dest_dir']
            self._check_localsave(run_id)
        else:
            self._check(get_output_url(run_id), remote_exists, remote_open)

    ## CRUD API

    def get(self, run_id):
        # This simply looks for the existence of output and absence of failure
        # TODO: actually look for status
        getattr(self, '_check_{}'.format(EXPORT_MODE))(run_id)

class RunOutput(RunHandlerBase):

    ## Output json parsing methods

    def _parse_kmzs_info(self, r, section_info):
        kmz_info = section_info.get('kmzs', {})
        if kmz_info:
            r['kmzs'] = {k: '{}/{}'.format(section_info['sub_directory'], v)
                for k, v in kmz_info.items() if k in ('fire', 'smoke')}

    ## ******************** TO DELETE - BEGIN  <-- (once v1 is obsoleted)
    def _parse_images_v1(self, r, vis_info):
        images_info = vis_info.get('images')
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
    ## ******************** TO DELETE - END

    def _parse_images_v2(self, r, vis_info):
        r["images"] = vis_info.get('images')
        for d in r['images']:
            for c in r['images'][d]:
                r['images'][d][c]["directory"] = os.path.join(
                    vis_info['sub_directory'], r['images'][d][c]["directory"])

    def _parse_output(self, output_json):
        export_info = output_json.get('export', {})
        # try both export modes, in case run was initiated with other mode
        other_em = set(EXPORT_CONFIGURATIONS.keys()).difference([EXPORT_MODE]).pop()
        export_info = export_info.get(EXPORT_MODE) or export_info.get(other_em)
        if not export_info:
           return {}

        r = {}
        vis_info = export_info.get('visualization')
        if vis_info:
            # images
            # TODO: simplify code once v1 is obsoleted
            image_results_version = output_json.get('config', {}).get(
                'export',{}).get(EXPORT_MODE, {}).get('image_results_version')
            if image_results_version == 'v2':
                self._parse_images_v2(r, vis_info)
            else:
                self._parse_images_v1(r, vis_info)

            # kmzs
            self._parse_kmzs_info(r, vis_info)

        disp_info = export_info.get('dispersion')
        if disp_info:
            r.update(**{
                k: '{}/{}'.format(disp_info['sub_directory'], disp_info[k.lower()])
                for k in ('netCDF', 'netCDFs') if k.lower() in disp_info})

            # kmzs (vsmoke dispersion produces kmzs)
            self._parse_kmzs_info(r, disp_info)

        # TODO: list fire_*.csv if specified in output_json

        return r

    ## Generic output get methdo

    def _get(self, output_location, exists_func, open_func, config, run_id):
        """Gets information about the outpu output, which may be in local dir
        or on remote host

        args:
         - output_location -- local pathname or url
         - exists_func -- function to check existence of dir or file
            (local or via http)
         - open_func -- function to open output json file (local or via http)
        """
        logging.debug('Looking for output in %s', output_location)
        if not exists_func(output_location):
            self.set_status(404)
        else:
            r = {
                # TODO: use get_output_url for form root_url
                "root_url": "{}://{}{}".format(self.request.protocol,
                    # TODO: use self.request.remote_ip instead of self.request.host
                    # TODO: call _get_host
                    config['host'] or self.request.host,
                    os.path.join(config['url_root_dir'], run_id))
            }
            # use join instead of os.path.join in case output_location is a remote url
            output_json_file = '/'.join([output_location.rstrip('/'), 'output.json'])
            if exists_func(output_json_file):
                with open_func(output_json_file) as f:
                    try:
                        r.update(self._parse_output(json.loads(f.read())))
                        # TODO: set fields here, using , etc.
                    except:
                        pass

            self.write(r)

    ## localsave

    def _get_localsave(self, run_id):
        # if bsp workers are on another machine, this will never return an
        # accurate response. ('localsave' should only be used when running
        # everything on one server)
        output_dir = os.path.join(EXPORT_CONFIGURATION['dest_dir'], run_id)
        self._get(output_dir, os.path.exists, open, EXPORT_CONFIGURATION, run_id)

    ## upload

    def _get_upload(self, run_id):
        if is_same_host(self.request.host):
            logging.debug("Uploaded export is local")
            # Note: alternatively, we could do the following:
            #  > EXPORT_CONFIGURATION['dest_dir'] = EXPORT_CONFIGURATION['scp']['dest_dir']
            #  > EXPORT_CONFIGURATION['url_root_dir'] = EXPORT_CONFIGURATION['scp']['url_root_dir']
            #  > EXPORT_CONFIGURATION['host'] = EXPORT_CONFIGURATION['scp']['host']
            #  > self._get_localsave(run_id)
            output_dir = os.path.join(EXPORT_CONFIGURATION['scp']['dest_dir'], run_id)
            self._get(output_dir, os.path.exists, open, EXPORT_CONFIGURATION['scp'], run_id)
        else:
            self._get(get_output_url(run_id), remote_exists, remote_open,
                EXPORT_CONFIGURATION['scp'], run_id)

    ## CRUD API

    def get(self, run_id):
        getattr(self, '_get_{}'.format(EXPORT_MODE))(run_id)
