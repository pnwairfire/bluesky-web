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
    "InvalidDomainError",
    "MetArchiveDB"
]

DOMAINS = blueskyconfig.get('domains')

class BoundaryNotDefinedError(ValueError):
    pass

class InvalidDomainError(ValueError):
    pass


ONE_DAY = datetime.timedelta(days=1)

##
## Domain database
##

class MetArchiveDB(object):

    def __init__(self, mongodb_url):
        db_name = (urlparse(mongodb_url).path.lstrip('/').split('/')[0]
            or 'blueskyweb')
        tornado.log.gen_log.debug('Using %s for domain data', mongodb_url)
        self.db = motor.motor_tornado.MotorClient(mongodb_url)[db_name]

    # TODO: memoize/cache
    async def find(self, archive_id=None):
        query = {"domain": archive_id} if archive_id else {}
        data = {}
        async for d in self.db.dates.find(query):
            data[d['domain']] = {
                "dates": sorted(list(set(d['complete_dates'])))
            }
            if d['domain'] in DOMAINS:
                data[d['domain']]['grid'] = DOMAINS[d['domain']]['grid']
        return data

    # TODO: memoize/cache
    async def get_root_dir(self, archive_id):
        # Use met_files collection object directly so that we can
        # specify reading only the root_dir field
        d = await self.db.met_files.find_one({'domain': archive_id}, {'root_dir': 1})
        if not d:
            raise InvalidDomainError(archive_id)

        return d['root_dir']

    # TODO: memoize/cache
    async def get_availability(self, archive_id, target_date, date_range):
        data = await self.find(archive_id=archive_id)
        if not data:
            raise InvalidDomainError(archive_id)

        date_range *= ONE_DAY

        begin_date_str = (target_date - date_range).strftime('%Y-%m-%d')
        target_date_str = target_date.strftime('%Y-%m-%d')
        end_date_str = (target_date + date_range).strftime('%Y-%m-%d')

        available = target_date_str in data[archive_id]["dates"]
        alternatives = [d for d in data[archive_id]["dates"]
            if d >= begin_date_str and d <= end_date_str and
            d != target_date_str]

        return {
            "available": available,
            "alternatives": alternatives
        }

