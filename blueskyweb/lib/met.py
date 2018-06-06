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
import ssl
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
                archive_info = v[archive_id]
                return dict(archive_info, id=archive_id,
                    **DOMAINS[archive_info['domain_id']])
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
        client_args = {
            'ssl': True,
            'ssl_match_hostname': False, # Note: makes vulnerable to man-in-the-middle attacks
            'ssl_cert_reqs': ssl.CERT_NONE,
            'ssl_certfile': '/etc/ssl/mongo-client-cert.crt',
            'ssl_keyfile': '/etc/ssl/mongo-client-cert.key',
            #'ssl_ca_certs': '/etc/ssl/mongo-client.pem'
        }
        self.db = motor.motor_tornado.MotorClient(
            mongodb_url, **client_args)[db_name]

    async def get_root_dir(self, archive_id):
        # Use met_files collection object directly so that we can
        # specify reading only the root_dir field
        d = await self.db.met_files.find_one({'domain': archive_id}, {'root_dir': 1})
        if not d:
            raise UnavailableArchiveError(archive_id)

        return d['root_dir']

    async def get_availability(self, archive_id=None):
        validate_archive_id(archive_id)

        query = { "domain": archive_id } if archive_id else {}
        select_set = {'domain': 1, 'start': 1, 'end': 1, 'latest_forecast': 1}
        r = {}
        async for e in self.db.dates.find(query, select_set):
            # Note what we're calling 'begin' here is called 'start'
            # in the arl index db
            if e['domain'] in r:
                # This should never happen, since dates collection
                # is already aggregated across all servers
                r[e['domain']]['begin'] = min(
                    r[e['domain']]['begin'], e['start'])
                r[e['domain']]['end'] = min(
                    r[e['domain']]['end'], e['end'])
                r[e['domain']]['latest_forecast'] = min(
                    r[e['domain']]['latest_forecast'], e['latest_forecast'])
            else:
                r[e['domain']] = dict(begin=e['start'], end=e['end'],
                    latest_forecast=e['latest_forecast'])

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

    async def list_obsolete_archives(self, prune=False):
        """Lists obsolete archives in db and optionally removes them.
        """
        obsolete = []

        async for r in self.db.dates.find({}, {'domain': 1, '_id': 0}):
            try:
                validate_archive_id(r['domain'])
                tornado.log.gen_log.info('Valid archive %s', r['domain'])
            except InvalidArchiveError as e:
                tornado.log.gen_log.info('Obsolete archive %s', r['domain'])
                obsolete.append(r['domain'])
                if prune:
                    q = {'domain': r['domain']}
                    self.db.dates.remove(q)
                    self.db.met_files.remove(q)

        return obsolete

    async def clear_index(self):
        """Compeletely clears the index - i.e. deletes all dates and
        met files recorded in the index.
        """
        self.db.dates.remove({})
        self.db.met_files.remove({})
