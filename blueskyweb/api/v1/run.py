"""blueskyweb.api.v1.run"""

# TODO: replace each reference to domains.DOMAINS with call
#   to some method (to be implemented) in domains.DomainDB or to
#   a module level function in domains wrapping the hardcoded data

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import copy
import datetime
import io
import json
import os
import re
import requests
import socket
import urllib.request, urllib.error, urllib.parse
import uuid
import traceback

import ipify
import tornado.web
import tornado.log

from blueskyworker.tasks import run_bluesky, BlueSkyRunner
from blueskyweb.lib import domains


IP_ADDRESS = ipify.get_ip()

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

class RunExecuter(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    async def post(self, mode=None, domain=None):
        if domain and domain not in domains.DOMAINS:
            self._bad_request(404, 'unrecognized domain')
            return

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
            self._set_modules(domain, mode, data)

            # TODO: check data['modules'] specifically for 'localmet',
            # 'dispersion', 'visualization' (and 'export'?)
            #tornado.log.gen_log.debug("BSP input data: %s", json.dumps(data))
            if mode not in ('fuelbeds', 'emissions'):
                # plumerise or dispersion (Hysplit or VSMOKE) request
                for m in data['modules']:
                    f = getattr(self, '_configure_{}'.format(m), None)
                    if f:
                        await f(data, domain)

                # TODO: configure anything else (e.g. setting domain where
                #  appropriate)
                self._run_asynchronously(data, domain=domain)

            else:
                await self._configure_emissions(data)
                # fuelbeds or emissions request
                if self.get_query_argument('_a', default=None) is not None:
                    self._run_asynchronously(data)
                else:
                    await self._run_in_process(data)

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
    # TODO: for plumerise requests, instead of running findmetdata, get
    #   met data from indexed met data in mongodb;  maybe fall back on
    #   running findmetdata if indexed data isn't there or if mongodb
    #   query fails
    PLUMERISE_MODULES = [
        'findmetdata', 'localmet', 'plumerising'
    ]
    MET_DISPERSION_MODULES = [
        'timeprofiling', 'dispersion', 'visualization', 'export'
    ]
    METLESS_DISPERSION_MODULES = [
        'timeprofiling', 'dispersion', 'export'
    ]

    def _set_modules(self, domain, mode, data):
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
                if domain else self.METLESS_DISPERSION_MODULES)
            if mode == 'all':
                _set(self.FUELBEDS_MODULES + self.EMISSIONS_MODULES +
                    self.PLUMERISE_MODULES + dispersion_modules)
            else:
                if 'met' not in data:
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

    def _get_queue_name(self, domain):
        if domain:
            if domain not in domains.DOMAINS:
                msg = "Invalid domain: {}".format(domain)
                raise tornado.web.HTTPError(status_code=404, log_message=msg)
            return domains.DOMAINS[domain]['queue']
        else:
            return 'no-met'


    def _run_asynchronously(self, data, domain=None):
        queue_name = self._get_queue_name(domain)

        #tornado.log.gen_log.debug('input: %s', data)
        args = (data, ) # has to be a tuple

        # TODO: figure out how to enqueue without blocking
        settings = {k:v for k, v in self.settings.items() if k != 'mongo_db'}
        run_bluesky.apply_async(args=args, kwargs=settings, queue=queue_name)
        # TODO: call specify callback in record_run, calling
        #    self.write in callback, so we can handle failure?
        self.settings['mongo_db'].record_run(data['run_id'], 'enqueued',
            queue=queue_name, modules=data["modules"],
            ts=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
        self.write({"run_id": data['run_id']})

    async def _run_in_process(self, data):
        try:
            #tornado.log.gen_log.debug('input: %s', data)
            # TODO: refactor task module so that bluesky can be
            #    run without blocking, and use `await` here
            stdout_data = BlueSkyRunner(data, **self.settings).run()
            # TODO: make sure stdout_data is valid json?
            #tornado.log.gen_log.debug('output: %s', stdout_data)
            self.write(stdout_data)

        # TODO: return 404 if output has error related to bad module, etc.
        except Exception as e:
            tornado.log.gen_log.debug(traceback.format_exc())
            tornado.log.gen_log.error('Exception: %s', e)
            self.set_status(500)

    async def _configure_emissions(self, data):
        tornado.log.gen_log.debug('Configuring emissions')
        data['config'] = data.get('config', {})
        data['config']['emissions'] = data['config'].get('emissions', {})
        data['config']['emissions']['efs'] = "urbanski"

    async def _configure_findmetdata(self, data, domain):
        tornado.log.gen_log.debug('Configuring findmetdata')
        data['config'] = data.get('config', {})
        domains_db = domains.DomainDB(self.settings['mongodb_url'])
        met_root_dir = await domains_db.get_root_dir(domain)
        data['config']['findmetdata'] = {
            "met_root_dir": met_root_dir,
            "arl": {
                "index_filename_pattern":
                    domains.DOMAINS[domain]['index_filename_pattern'],
                "fewer_arl_files": True
            }
        }

    async def _configure_localmet(self, data, domain):
        tornado.log.gen_log.debug('Configuring localmet')
        data['config'] = data.get('config', {})
        data['config']['localmet'] = {
            "time_step": domains.DOMAINS[domain]['time_step']
        }

    async def _configure_plumerising(self, data, domain):
        tornado.log.gen_log.debug('Configuring plumerising')
        data['config'] = data.get('config', {})
        data['config']['plumerising'] = {
            "model": "sev"
        }

    DEFAULT_HYSPLIT_GRID_LENGTH = 2000

    async def _configure_dispersion(self, data, domain):
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
                        {k.upper(): v for k, v in list(met_boundary.items())})
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

            tornado.log.gen_log.debug("hysplit configuration: %s", data['config']['dispersion']['hysplit'])

        # TODO: any other model-specific configuration?

    async def _configure_visualization(self, data, domain):
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

    async def _configure_export(self, data, domain):
        # we just run export to get image and file information
        tornado.log.gen_log.debug('Configuring export')
        # dest_dir = data['config']['dispersion']['output_dir'].replace(
        #     'output', 'export')
        # Run id will be
        dest_dir = os.path.join(
            self.settings['output_root_dir'],
            self.settings['output_url_path_prefix'])

        extras = ["dispersion", "visualization"] if domain else ["dispersion"]
        data['config']['export'] = {
            "modes": ["localsave"],
            "extra_exports": extras,
            "localsave": {
                "handle_existing": "write_in_place",
                "dest_dir": dest_dir
            }
        }
        # ***** BEGIN -- TODO: DELETE ONCE 'v1' is removed
        try:
            image_results_version = self.get_argument('image_results_version')
            if image_results_version:
                tornado.log.gen_log.debug('Setting image_results_version: %s',
                    image_results_version)
                data['config']['export']['localsave']['image_results_version'] = image_results_version
        except tornado.web.MissingArgumentError:
            tornado.log.gen_log.debug('image_results_version not specified')
        # ***** END

class RunStatus(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    async def get(self, run_id):
        # TODO: implement using data form mongodb
        run = await self.settings['mongo_db'].find_run(run_id)
        if not run:
            self.set_status(404, "Run doesn't exist")
            self.write({"error": "Run doesn't exist"})
        else:
            self.write({"run": run})



class RunOutput(tornado.web.RequestHandler):

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
                self.set_status(501, 'Not implemented')
                self.write({'error': "Getting {} output not "
                    "implemented.".format(run['modules'][-1])})

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
            # TODO: simplify code once v1 is obsoleted
            # TODO: make sure both v1 and v2 work
            if output['config']['export']['localsave'].get(
                    'image_results_version') == 'v2':
                self._parse_images_v2(r, vis_info)
            else:
                self._parse_images_v1(r, vis_info)

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


class RunsInfo(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    async def get(self, status=None):
        limit = int(self.get_query_argument('limit', 10))
        offset = int(self.get_query_argument('offset', 0))
        runs = await self.settings['mongo_db'].find_runs(status=status,
            limit=limit, offset=offset)

        # TODO: include total count of runs with given status, and of runs
        #    of all statuses?
        self.write({"runs": runs})
