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
            #'tlsAllowInvalidHostnames': True, # Note: makes vulnerable to man-in-the-middle attacks
            'tlsAllowInvalidCertificates': True,
            # 'tlsCertificateKeyFile': '/etc/ssl/bluesky-web-client-cert.pem',
            'tlsCAFile': '/etc/ssl/bluesky-web-client.pem'
        }
        self.db = motor.motor_tornado.MotorClient(
            mongodb_url, **client_args)[db_name]

    def record_run(self, run_id, status, module=None, log=None, stdout=None,
            percent_complete=None, status_message=None, **data):

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
        try:
            result = self.db.runs.update_one(spec, doc, upsert=True)
            tornado.log.gen_log.debug('Recorded run: %s', result)
        except Exception as e:
            tornado.log.gen_log.error('Error recording run: %s', e)

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
            return await self.db.runs.count_documents(query)

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

    async def run_counts_by_month(self, run_id=None):
        """Returns run counts, per month, for past year
        """
        # TOOD: support query parameters to override default of past year,
        #   and set argument to `to_list`, below, accordingly
        year_ago = datetime.datetime.now() - datetime.timedelta(days=365)
        since_str = datetime.date(year_ago.year, year_ago.month, 1).strftime("%Y-%m-%dT00:00:00")

        pipeline = [
            {
                "$match": {
                    "initiated_at": { "$gte": since_str }
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": {"$substr": [ "$initiated_at", 0, 4 ] },
                        "month": {"$substr": [ "$initiated_at", 5, 2 ] },
                        "queue": "$queue",
                    },
                    "count": { "$sum": 1 }
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": "$_id.year",
                        "month": "$_id.month",
                    },
                    "count": { "$sum": '$count' },
                    "by_queue": {
                        "$push": {
                            "queue": '$_id.queue',
                            "count": '$count'
                        }
                    }
                }
            },
            {
                '$sort': {'_id': -1}
            }
        ]

        if run_id:
            # insert at beginning
            pipeline.insert(0, {
                "$match": {
                    "run_id": { '$regex': run_id }
                }
            })

        cursor = self.db.runs.aggregate(pipeline)
        r = await cursor.to_list(12)

        return [{
            'year': e['_id']['year'],
            'month': e['_id']['month'],
            'count': e['count'],
            'by_queue': sorted(e['by_queue'], key=lambda e: -e["count"])
        } for e in r]

    async def run_counts_by_day(self, run_id=None):
        """Returns run counts, per day, for past 30 days
        """
        # TOOD: support query parameters to override default of past
        #   30 days, and set argument to `to_list`, below, accordingly
        month_ago = datetime.datetime.now() - datetime.timedelta(days=30)
        since_str = month_ago.strftime("%Y-%m-%dT00:00:00")

        pipeline = [
            {
                "$match": {
                    "initiated_at": { "$gte": since_str }
                }
            },
            {
                "$group": {
                    "_id": {
                        "date": { "$substr": [ "$initiated_at", 0, 10 ] },
                        "queue": "$queue",
                    },
                    "count": { "$sum": 1 }
                }
            },
            {
                "$group": {
                    "_id":  "$_id.date",
                    "count": { "$sum": "$count"},
                    "by_queue": {
                        "$push": {
                            "queue": "$_id.queue",
                            "count": "$count"
                        }
                    }
                }
            },
            {
                "$sort": {"_id": -1}
            }
        ]

        if run_id:
            # insert at beginning
            pipeline.insert(0, {
                "$match": {
                    "run_id": { '$regex': run_id }
                }
            })

        cursor = self.db.runs.aggregate(pipeline)
        r = await cursor.to_list(30)

        return [{
            'date': e['_id'],
            'count': e['count'],
            'by_queue': sorted(e['by_queue'], key=lambda e: -e["count"])
        } for e in r]
