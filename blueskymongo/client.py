"""blueskymongo.client"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import datetime
import ssl
from urllib.parse import urlparse

import motor
import tornado.log


class RunStatusesType(type):
    STATUSES = {
        "Enqueued": "enqueued",
        "Dequeued": "dequeued",
        "Running": "running",
        "StartingModule": 'starting_module',
        'RunningModule': 'running_module',
        'CompletedModule': 'completed_module',
        'FailedModule': 'failed_module',
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
        client_args = {
            'ssl': True,
            #'ssl_match_hostname': False, # Note: makes vulnerable to man-in-the-middle attacks
            'ssl_cert_reqs': ssl.CERT_NONE,
            # 'ssl_certfile': '/etc/ssl/bluesky-web-client-cert.crt',
            # 'ssl_keyfile': '/etc/ssl/bluesky-web-client-cert.key',
            'ssl_ca_certs': '/etc/ssl/bluesky-web-client.pem'
        }
        self.db = motor.motor_tornado.MotorClient(
            mongodb_url, **client_args)[db_name]

    def record_run(self, run_id, status, module=None, log=None, stdout=None,
            percent_complete=None, status_message=None, callback=None, **data):
        def _callback(result, error):
            if error:
                tornado.log.gen_log.error('Error recording run: %s', error)
            else:
                tornado.log.gen_log.debug('Recorded run: %s', result.raw_result)
            if callback:
                callback(result, error)

        spec = {"run_id": run_id}
        # include run_id in doc in case it's an insert
        ts = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
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
        if percent_complete is not None:
            doc["$push"]["history"]['$each'][0]["perc"] = percent_complete
            # als put percent complete in data
            if data:
                data['percent'] = percent_complete
            else:
                data = {'percent': percent_complete}
        if status_message:
            doc["$push"]["history"]['$each'][0]["msg"] = status_message

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

    async def find_runs(self, status=None, limit=None, offset=None, run_id=None):
        query = {'history.0.status': status} if status else {}
        if run_id:
            # TODO: protect against sql-injection types of attacks
            query['run_id'] = { '$regex': run_id }
        tornado.log.gen_log.debug('query, limit, offset: %s, %s, %s',
            query, limit, offset)

        # Count sometimes returns wront vallue if there are
        # 'orphaned' (?) documents. So, use aggregate instead:
        #total_count = await self.db.runs.count(query)
        cursor = self.db.runs.aggregate([
            { "$match": query },
            { "$count": "count" }
        ])

        r = await cursor.to_list(1)
        total_count = r[0]['count'] if r else 0

        if total_count > 0:
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
        else:
            runs = []

        return runs, total_count

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

    # *** Temporarary HACK ***
    async def _archive_run(self, run):
        if run:
            old_run_id = run['run_id']
            run['run_id'] += '-' + datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')
            tornado.log.gen_log.info('Setting run %s with new run_id %s',
                old_run_id, run['run_id'])
            await self.db.runs.update_one({'run_id': old_run_id},
                {'$set': {'run_id': run['run_id']}})
    # *** Temporarary HACK ***

    async def delete_run(self, run_id):
        r = await self.db.runs.delete_one({'run_id': run_id})
        return r.deleted_count

    async def delete_all_runs(self):
        r = await self.db.runs.delete_many({})
        return r.deleted_count


    ## Stats

    async def run_counts_by_month(self):
        """Returns run counts, per month, for past 12 months
        """
        cursor = self.db.runs.aggregate([

            # TODO: limit by year or time range, based
            #   on query parameters or default to past year,
            #   and set argument to `to_list`, below, accordingly

            {
                '$group': {
                    '_id': {
                        "year": {'$substr': [ "$initiated_at", 0, 4 ] },
                        "month": {'$substr': [ "$initiated_at", 5, 2 ] },
                    },
                    'count': { '$sum': 1 }
                }
            },
            {
                '$sort': {'_id': -1}
            }
        ])
        r = await cursor.to_list(12)

        return [{
            'year': e['_id']['year'],
            'month': e['_id']['month'],
            'count': e['count'],
        } for e in r]
