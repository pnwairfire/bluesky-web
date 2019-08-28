"""blueskyweb.lib.api.run"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import abc
import datetime
import json
import os
import requests
import urllib.request
import traceback

import ipify
import tornado.web
import tornado.log

from blueskymongo.client import RunStatuses
from blueskyworker.tasks import process_runtime
from blueskyweb.lib import met
from blueskyweb.lib.runs.execute import BlueSkyRunExecuter
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

class RunExecuteBase(RequestHandlerBase, metaclass=abc.ABCMeta):

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
        self._archive_id = archive_id
        self._archive_info = met.db.get_archive_info(archive_id)

        if not self.request.body:
            self._raise_error(400, 'empty post data')
            return

        try:
            data = json.loads(self.request.body.decode())
        except json.JSONDecodeError as e:
            self._raise_error(400, 'Invalid JSON post data')

        if self.fires_key not in data:
            self._raise_error(400, "'{}' not specified".format(self.fires_key))
            return

        self._pre_process(data)

        executer = BlueSkyRunExecuter(mode, self.get_query_argument,
            self._raise_error, self.write)
        await executer.execute(data)




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

