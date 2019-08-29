"""blueskyweb.api.run"""

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
from blueskyweb.lib.runs.output import BlueSkyRunOutput
from . import RequestHandlerBase


try:
    IP_ADDRESS = ipify.get_ip()
except:
    # IP_ADDRESS is only used to see if worker is running on
    # same machine as web server.  If ipify fails, we'll just
    # resort to loading all output as if from remote server
    pass




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

class RunExecute(RequestHandlerBase, metaclass=abc.ABCMeta):

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
    async def post(self, api_version, mode=None, archive_id=None):
        if not self.request.body:
            self._raise_error(400, 'empty post data')
            return

        try:
            data = json.loads(self.request.body.decode())
        except json.JSONDecodeError as e:
            self._raise_error(400, 'Invalid JSON post data')

        self._pre_process(data)

        executer = BlueSkyRunExecuter(api_version, mode, archive_id,
            self._raise_error, self.write)
        await executer.execute(data,
            run_asynchronously=self.get_query_argument(
                '_a', default=None) is not None)




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
    async def get(self, api_version, run_id):
        # TODO: implement using data form mongodb
        run = await self.settings['mongo_db'].find_run(run_id)
        if not run:
            self._raise_error(404, "Run doesn't exist")
        else:
            await self.process(run)
            self.write(run)


class RunsInfo(RunStatusBase):

    @tornado.web.asynchronous
    async def get(self, api_version, status=None):
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
    async def get(self, api_version, run_id):
        # TODO: implement using data form mongodb
        run = await self.settings['mongo_db'].find_run(run_id)
        if not run:
            self._raise_error(404, "Run doesn't exist")

        elif not run.get('output_url'):
            self._raise_error(404, "Run output doesn't exist")

        else:
            BlueSkyRunOutput(run, self._raise_error, self.write).process()
