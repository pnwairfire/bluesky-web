import datetime
from urllib.parse import urlparse

import motor
import tornado.log


class RunStatusesType(type):
    STATUSES = {
        "Enqueued": "enqueued",
        "Dequeued": "dequeued",
        "Running": "running",
        "StartingModule": 'starting_module',
        'CompletedModule': 'completed_module',
        "ProcessingOutput": "processing_output",
        "Completed": "completed",
        "Failed": "failed"
    }

    def __getattr__(self, key):
        if key in self.STATUSES:
            return self.STATUSES[key]
        elif key == 'statuses':
            return list(self.STATUSES.values())
        #return super(RunStatus, self).__getattr__(key)
        raise AttributeError(key)

class RunStatuses(metaclass=RunStatusesType):
    pass


class BlueSkyWebDB(object):

    def __init__(self, mongodb_url):
        db_name = (urlparse(mongodb_url).path.lstrip('/').split('/')[0]
            or 'blueskyweb')
        self.db = motor.motor_tornado.MotorClient(mongodb_url)[db_name]

    def record_run(self, run_id, status, module=None, log=None, stdout=None, callback=None,
            **data):
        def _callback(result, error):
            if error:
                tornado.log.gen_log.error('Error recording run: %s', error)
            else:
                tornado.log.gen_log.debug('Recorded run: %s', result)
            if callback:
                callback(result, error)

        spec = {"run_id": run_id}
        # include run_id in doc in case it's an insert
        ts = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        doc = {
            "$push": {
                "history": {
                    # insert at position in reverse chronological order
                    '$each': [{'status': status, 'ts': ts}],
                    '$position': 0
                }
            }
        }
        if module:
            doc["$push"]["history"]['$each'][0]["module"] = module
        if log:
            doc["$push"]["history"]['$each'][0]["log"] = log
        if stdout:
            doc["$push"]["history"]['$each'][0]["stdout"] = stdout
        if data:
            doc["$set"] = data

        # There should never be multiple entries, since we're always
        # doing upserts
        self.db.runs.update_one(spec, doc, upsert=True, callback=_callback)

    async def find_run(self, run_id):
        run = await self.db.runs.find_one({"run_id": run_id})
        if run:
            run.pop('_id')
        return run

    async def find_runs(self, status=None, limit=None, offset=None):
        query = {'history.0.status': status} if status else {}
        tornado.log.gen_log.debug('query, limit, offset: %s, %s, %s',
            query, limit, offset)

        cursor = self.db.runs.find(query)
        cursor = cursor.sort([('initiated_at', -1)]).limit(limit).skip(offset)

        # runs = []
        # async for r in cursor:
        #     tornado.log.gen_log.debug('run: %s', r)
        #     r.pop('_id')
        #     runs.append(r)
        runs = await cursor.to_list(limit)

        for r in runs:
            r.pop('_id')

        return runs

    async def get_queue_position(self, run):
        """

        args:
         - run -- either run dict or run_id string
        """
        # TODO: do this more efficiently - not querying run first
        if hasattr(run, 'lower'):
            # it's a run id; query run
            run = await self.find_run(run)

        if run['history'][0]['status'] == RunStatuses.Enqueued:
            query = {
                'history.0.status': RunStatuses.Enqueued,
                'initiated_at': {'$lte': run['initiated_at']},
                'queue': run['queue']
            }
            return await self.db.runs.find(query).count()

        # else, returns None -> i.e. not in queue
