"""blueskyweb.lib.domain

Notes:
 - the arlindexer works in terms of 'domains', but bluesky web
   uses works with met 'archives'.  The indexes are per archive,
   but are labeled as 'domain' in the database
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import datetime
import logging
import math
import os
from urllib.parse import urlparse

import motor
import tornado.log
import blueskyconfig

__all__ = [
    "DOMAINS",
    "BoundaryNotDefinedError",
    "InvalidArchiveError",
    "UnavailableArchiveError",
    "MetArchiveDB"
]

DOMAINS = blueskyconfig.get('domains')
ARCHIVES = blueskyconfig.get('archives')

class BoundaryNotDefinedError(ValueError):
    pass
class ArchiveNotDefinedError(ValueError):
    pass
class InvalidArchiveError(ValueError):
    pass
class UnavailableArchiveError(ValueError):
    pass


ONE_DAY = datetime.timedelta(days=1)

##
## Domain database
##

def get_archive_info(archive_id):
    if archive_id:
        for v in ARCHIVES.values():
            if archive_id in v:
                return dict(v, id=archive_id, **DOMAINS[v['domain']])
        raise InvalidArchiveError(archive_id)


def validate_archive_id(archive_id):
    if archive_id:
        for v in ARCHIVES.values():
            if archive_id in v:
                return archive_id
        raise InvalidArchiveError(archive_id)


class MetArchiveDB(object):
    """Wraps interaction with met archive index mongodb

    TODO: memoize / cache the three main methods
    """

    def __init__(self, mongodb_url):
        db_name = (urlparse(mongodb_url).path.lstrip('/').split('/')[0]
            or 'blueskyweb')
        tornado.log.gen_log.debug('Using %s for domain data', mongodb_url)
        self.db = motor.motor_tornado.MotorClient(mongodb_url)[db_name]

    async def get_root_dir(self, archive_id):
        # Use met_files collection object directly so that we can
        # specify reading only the root_dir field
        d = await self.db.met_files.find_one({'domain': archive_id}, {'root_dir': 1})
        if not d:
            raise UnavailableArchiveError(archive_id)

        return d['root_dir']


    async def get_availability(self, archive_id=None):
        validate_archive_id(archive_id)

        pipeline = []
        if archive_id:
            pipeline.append({"$match": { "domain": archive_id }})
        pipeline.extend([
            {
                "$project": {
                    "archive_id": "$domain",
                    "begin": { "$min": "$complete_dates" },
                    "end": { "$max": "$complete_dates" }
                }
            }
        ])
        r = {}
        async for e in self.db.dates.aggregate(pipeline):
            if e['archive_id'] in r:
                # This shouldn't happen
                r[e['archive_id']]['begin'] = min(
                    r[e['archive_id']]['begin'], e['begin'])
                r[e['archive_id']]['end'] = min(
                    r[e['archive_id']]['end'], e['end'])
            else:
                r[e['archive_id']] = dict(begin=e['begin'], end=e['end'])

        # TODO: modify r?
        if archive_id:
            return r.get(archive_id) or dict(begin=None, end=None)
        return r

    async def check_availability(self, archive_id, target_date, date_range):
        if not archive_id:
            raise ArchiveNotDefinedError()
        validate_archive_id(archive_id)

        date_range *= ONE_DAY
        begin_date_str = (target_date - date_range).strftime('%Y-%m-%d')
        target_date_str = target_date.strftime('%Y-%m-%d')
        end_date_str = (target_date + date_range).strftime('%Y-%m-%d')

        tornado.log.gen_log.debug('Check date availability for %s or between %s and %s',
            target_date_str, begin_date_str, end_date_str)

        pipeline = [
            { "$match": { "domain": archive_id }},
            {
                "$addFields" : {
                    "complete_dates":{
                        "$filter": { # override the existing field
                            "input": "$complete_dates",
                            "as": "single_date",
                            "cond": {
                                '$and': [
                                    {"$gte": ["$$single_date", begin_date_str]},
                                    {"$lte": ["$$single_date", end_date_str]}
                                ]
                            }
                        }
                    }
                }
            }
        ]

        # There should be at most one result
        available_dates = []
        async for e in self.db.dates.aggregate(pipeline):
            tornado.log.gen_log.debug('found availability: %s', e['complete_dates'])
            available_dates.extend(e['complete_dates'])

        # ***** TEMP *****
        # TODO: remove the following once arlindexer is updated to
        #   not save redundant dates
        available_dates = set(available_dates)
        # ***** TEMP *****

        available = target_date_str in available_dates
        alternatives = [d for d in available_dates if d != target_date_str]

        return {
            "available": available,
            "alternatives": alternatives
        }
