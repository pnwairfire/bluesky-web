"""blueskyweb.api.run"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import abc
import datetime
import json
import requests
import urllib.request

import tornado.web
import tornado.log

from blueskymongo.client import RunStatuses
from blueskyweb.lib import met
from blueskyweb.lib.runs.execute import BlueSkyRunExecutor, ExecuteMode
from blueskyweb.lib.runs.output import BlueSkyRunOutput
from . import RequestHandlerBase


###
### API Handlers
###

class RunExecute(RequestHandlerBase):

    ##
    ## Main interface
    ##

    async def post(self, api_version, mode=None, archive_id=None):
        if not self.request.body:
            self._raise_error(400, 'empty post data')
            return

        request_body = self.request.body.decode()
        tornado.log.gen_log.debug("Execute API request data: %s", request_body)
        try:
            data = json.loads(request_body)
        except json.JSONDecodeError as e:
            self._raise_error(400, 'Invalid JSON post data')

        hysplit_query_params = {
            'dispersion_speed': self.get_query_argument('dispersion_speed', None),
            'grid_resolution': self.get_query_argument('grid_resolution', None),
            'number_of_particles': self.get_query_argument('number_of_particles', None),
            'grid_size': self.get_float_arg('grid_size', default=None)
        }

        executor = BlueSkyRunExecutor(api_version, mode, archive_id,
            self._raise_error, self, self.settings, hysplit_query_params)

        scheduleFor = self.get_datetime_arg('schedule_for', None)
        tornado.log.gen_log.info("schedule_for: %s", scheduleFor)

        # The default is for fuelbeds and emissions to be run in process and
        # all other modes asynchronously.  Allow fuelbeds and emissions to
        # be run asynchronously (if either '_a' or 'schedule_for' are specified),
        # but never allow other modes to be run in process.
        execute_mode = (ExecuteMode.ASYNC if (self.get_query_argument(
            '_a', default=None) is not None or scheduleFor) else None)

        await executor.execute(data, execute_mode=execute_mode,
            scheduleFor=scheduleFor)

    def write(self, val):
        """Overrides super's write in order log response data
        and check for errors
        """
        if isinstance(val, dict) and 'error' in val:
            # TODO: raise error and don't return enture bluesky output
            #  (i.e. val) in API response?
            #    self._raise_error(400, val['error'].get('message'))
            # TODO: make sure it is in deed a client request error;
            #    otherwise return 500
            self.set_status(400, val['error'].get('message'))

        tornado.log.gen_log.debug("Execute API response data: %s", val)
        super().write(val)




class RunStatusBase(RequestHandlerBase):

    VERBOSE_FIELDS = ('output_dir', 'modules', 'server', 'export',
        'fires')
    AVERAGE_RUN_TIME_IN_SECONDS = 360 # 6 minutes

    async def process(self, run):
        if not self.get_boolean_arg('raw'):
            if 'queue' in run:
                # need to call get_queue_position before converting
                # run['status'] from array to scalar object
                position = await self.settings['mongo_db'].get_queue_position(run)
                run['queue'] = {
                    'name': run['queue'],
                    'position': position  # will be None if no longer enqueued
                }

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

    async def get(self, api_version, run_id):
        # TODO: implement using data form mongodb
        run = await self.settings['mongo_db'].find_run(run_id)
        if not run:
            self._raise_error(404, "Run doesn't exist")
        else:
            await self.process(run)
            self.write(run)


class RunsInfo(RunStatusBase):

    async def get(self, api_version, status=None):
        # default limit to 10, and cap it at 25
        limit = min(int(self.get_query_argument('limit', 10)), 25)
        offset = int(self.get_query_argument('offset', 0))
        run_id = self.get_query_argument('run_id', None)
        runs, total_count = await self.settings['mongo_db'].find_runs(
            status=status, limit=limit, offset=offset, run_id=run_id)
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

    async def get(self, api_version, run_id):
        # TODO: implement using data form mongodb

        await BlueSkyRunOutput(api_version, self.settings['mongo_db'],
            self._raise_error, self).process(run_id)


class RunStatsMonthly(RequestHandlerBase):

    async def get(self, api_version):
        run_id = self.get_query_argument('run_id', None)
        monthly = await self.settings['mongo_db'].run_counts_by_month(run_id=run_id)
        self.write({
            'monthly': monthly
        })

class RunStatsDaily(RequestHandlerBase):

    async def get(self, api_version):
        run_id = self.get_query_argument('run_id', None)
        daily = await self.settings['mongo_db'].run_counts_by_day(run_id=run_id)
        self.write({
            'daily': daily
        })
