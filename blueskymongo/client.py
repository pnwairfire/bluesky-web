import datetime
from urllib.parse import urlparse

import motor
import tornado.log

class BlueSkyWebDB(object):

    def __init__(self, mongodb_url):
        db_name = (urlparse(mongodb_url).path.lstrip('/').split('/')[0]
            or 'blueskyweb')
        self.db = motor.motor_tornado.MotorClient(mongodb_url)[db_name]

    def record_run(self, run_id, status, callback=None, **data):
        def _callback(result, error):
            if error:
                tornado.log.gen_log.error('Error recording run: %s', error)
            else:
                tornado.log.gen_log.debug('Recorded run: %s', result)
            if callback:
                callback(result, error)

        spec = {"run_id": run_id}
        # include run_id in doc in case it's an insert
        doc = {"$set": dict(status=status, **data) }
        ts = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        doc["$set"][status] = ts

        # There should never be multiple entries, since we're always
        # doing upserts
        self.db.runs.update_one(spec, doc, upsert=True, callback=_callback)


    async def find_runs(self, status=None, limit=None, offset=None):
        query = {'status': status} if status else {}
        tornado.log.gen_log.debug('query, limit, offset: %s, %s, %s',
            query, limit, offset)

        cursor = self.db.runs.find(query)
        cursor = cursor.sort([('enqueued', -1)]).limit(limit).skip(offset)

        # runs = []
        # async for r in cursor:
        #     tornado.log.gen_log.debug('run: %s', r)
        #     r.pop('_id')
        #     runs.append(r)
        runs = await cursor.to_list(limit)

        for r in runs:
            r.pop('_id')

        return runs
