"""blueskyweb.lib.domain"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import datetime
import logging
import math
import os
from urllib.parse import urlparse

import motor
import tornado.log

class BoundaryNotDefinedError(ValueError):
    pass

class InvalidDomainError(ValueError):
    pass


# TODO: not sure where is the best place to define queues and
#   boundaries...maybe they should be defined in bsslib?...or let them be
#   defined as env vars with defaults....or they should be in mongodb!!
#   if going with mongodb, then don't hard code DOMAINS here, but instead
#   wrap with methods in DomainDB and memoize
DOMAINS = {
    # TODO: add PNW 4km with boundaries [-128, 41, -109, 50]
    # TODO: add LS (Great Lakes?) 4km with boundaries [-96.1, 41.5, -81.5, 49.5]
    'DRI2km': {
        'queue': 'dri', # TODO: define elsewhere ? (see above)
        "boundary": {
            # STI provided the following corners:
            #   CANV 2km - [-124.3549, 32.5479, -113.2558, 41.8884]
            # Then, ran the following on haze:
            #   $ chk_arl file /data/ARL/DRI/2km/2016040400/wrfout_d3.2016040400.f00-11_12hr01.arl |grep corner
            #     Lower left corner:   32.5980 -124.2761
            #    Upper right corner:   41.8444 -113.0910
            "center_latitude": 37.2212, #37.21815, # 37.0,
            "center_longitude": -118.68355, #-118.80535, # -119.0,
            "width_longitude": 11.1851, #11.0991, # 13.0,
            "height_latitude": 9.2464, #9.3405, #11.5,
            "spacing_longitude": 2.0,
            "spacing_latitude": 2.0,
            "projection": "LCC"
        },
        "index_filename_pattern": "arl12hrindex.csv",
        "time_step": 1
    },
    'DRI6km': {
        'queue': 'dri', # TODO: define elsewhere ? (see above)
        "boundary": {
            # Ran the following on haze:
            #   $ chk_arl file /data/ARL/DRI/6km/2016040400/wrfout_d2.2016040400.f00-11_12hr01.arl |grep corner
            #     Lower left corner:   28.7459 -128.4614
            #    Upper right corner:   44.5953 -107.1489
            "center_latitude": 36.6706, #36.5,
            "center_longitude": -117.80515, #-119.0,
            "width_longitude": 21.3125, #25.0,
            "height_latitude": 15.8494, #17.5,
            "spacing_longitude": 6.0,
            "spacing_latitude": 6.0,
            "projection": "LCC"
        },
        "index_filename_pattern": "arl12hrindex.csv",
        "time_step": 1
    },
    'PNW1.33km': {
        'queue': 'pnw', # TODO: define elsewhere ? (see above)
        "boundary": {
            # Ran the following on haze:
            #   $ chk_arl file /data/ARL/PNW/1.33km/2016040400/wrfout_d4.2016040400.f12-23_12hr01.arl |grep corner
            #     Lower left corner:   44.7056 -126.2475
            #    Upper right corner:   48.9398 -113.7484
            "center_latitude": 46.8227,
            "center_longitude": -119.99795,
            "width_longitude": 12.4991,
            "height_latitude": 4.2342,
            "spacing_longitude": 1.33,
            "spacing_latitude": 1.33,
            "projection": "LCC"
        },
        "index_filename_pattern": "arl12hrindex.csv",
        "time_step": 1
    },
    'PNW4km': {
        'queue': 'pnw', # TODO: define elsewhere ? (see above)
        "boundary": {
            # Ran the following on haze:
            #   $ chk_arl file /data/ARL/PNW/4km/2016040400/wrfout_d3.2016040400.f12-23_12hr01.arl |grep corner
            #     Lower left corner:   40.0488 -128.5677
            #    Upper right corner:   49.6821 -107.4911
            "center_latitude": 44.86545, #45.0,
            "center_longitude": -118.0294, #-118.3,
            "width_longitude": 21.0766, #20.0,
            "height_latitude": 9.6333, #10.0,
            "spacing_longitude": 4.0,
            "spacing_latitude": 4.0,
            "projection": "LCC"
        },
        "index_filename_pattern": "arl12hrindex.csv",
        "time_step": 1
    },
    'NAM84': {
        'queue': 'nam', # TODO: define elsewhere ? (see above)
        "boundary": {
            # STI provided the following corners:
            #   NAM 12km - [-131, 18, -64, 55]
            # Then, ran the following on haze:
            #   $ chk_arl file /data/ARL/NAM/12km/2016040400/nam_forecast-2016040400_00-84hr.arl |grep corner
            #     Lower left corner:   12.1900 -133.4600
            #    Upper right corner:   57.3290  -49.4167
            "center_latitude": 34.7595, #36.5, # 37.5,
            "center_longitude": -91.43835, #-97.5, # -95.0,
            "width_longitude": 84.0433, #67.0, # 70.0,
            "height_latitude": 45.139, #37.0, # 30.0,
            "spacing_longitude": 0.15,
            "spacing_latitude": 0.15,
            "projection": "LatLon"
        },
        "index_filename_pattern": "NAM84_ARL_index.csv",
        "time_step": 3
    }
}

ONE_DAY = datetime.timedelta(days=1)

##
## Domain database
##

class DomainDB(object):

    def __init__(self, mongodb_url):
        db_name = (urlparse(mongodb_url).path.lstrip('/').split('/')[0]
            or 'blueskyweb')
        tornado.log.gen_log.debug('Using %s for domain data', mongodb_url)
        self.db = motor.motor_tornado.MotorClient(mongodb_url)[db_name]

    # TODO: memoize/cache
    async def find(self, domain_id=None):
        query = {"domain": domain_id} if domain_id else {}
        data = {}
        async for d in self.db.dates.find(query):
            data[d['domain']] = {
                "dates": sorted(list(set(d['complete_dates'])))
            }
            if d['domain'] in DOMAINS:
                data[d['domain']]['boundary'] = DOMAINS[d['domain']]['boundary']
        return data

    # TODO: memoize/cache
    async def get_root_dir(self, domain_id):
        # Use met_files collection object directly so that we can
        # specify reading only the root_dir field
        d = self.db.met_files.find_one({'domain': domain_id}, {'root_dir': 1})
        if not d:
            raise InvalidDomainError(domain_id)

        return d['root_dir']

    # TODO: memoize/cache
    async def get_availability(self, domain_id, target_date, date_range):
        data = await self.find(domain_id=domain_id)
        if not data:
            raise InvalidDomainError(domain_id)

        date_range *= ONE_DAY

        begin_date_str = (target_date - date_range).strftime('%Y-%m-%d')
        target_date_str = target_date.strftime('%Y-%m-%d')
        end_date_str = (target_date + date_range).strftime('%Y-%m-%d')

        available = target_date_str in data[domain_id]["dates"]
        alternatives = [d for d in data[domain_id]["dates"]
            if d >= begin_date_str and d <= end_date_str and
            d != target_date_str]

        return {
            "available": available,
            "alternatives": alternatives
        }

##
## Utility methods
##

def get_met_boundary(domain):
    if domain not in DOMAINS:
        raise InvalidDomainError(domain_id)

    if not DOMAINS[domain].get('boundary'):
        raise BoundaryNotDefinedError(domain)

    return DOMAINS[domain]['boundary']
