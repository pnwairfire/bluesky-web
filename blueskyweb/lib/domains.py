"""blueskyweb.lib.domain"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import logging
import math
import os

from met.arlindexer import MetDatesCollection

class BlueSkyConfigurationError(ValueError):
    pass


MONGODB_URL = os.environ.get('MONGODB_URL')

# TODO: not sure where is the best place to define queues, root dirs, and
#   boundaries...maybe they should be defined in bsslib?...or let them be
#   defined as env vars with defaults....or they should be in mongodb!!
#   if going with mongodb, then don't hard code DOMAINS here, but instead
#   wrap with methods in DomainDB and memoize
DOMAINS = {
    # TODO: add PNW 4km with boundaries [-128, 41, -109, 50]
    # TODO: add LS (Great Lakes?) 4km with boundaries [-96.1, 41.5, -81.5, 49.5]
    'DRI2km': {
        'queue': 'all-met', #'dri', # TODO: define elsewhere ? (see above)
        'met_root_dir': '/data/Met/CANSAC/2km/ARL/', # TODO: don't hardcode (see above)
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
        'queue': 'all-met', #'dri', # TODO: define elsewhere ? (see above)
        'met_root_dir': '/data/Met/CANSAC/6km/ARL/', # TODO: don't hardcode (see above)
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
        'queue': 'all-met', #'pnw', # TODO: define elsewhere ? (see above)
        'met_root_dir': '/data/Met/PNW/1.33km/ARL/', # TODO: don't hardcode (see above)
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
        'queue': 'all-met', #'pnw', # TODO: define elsewhere ? (see above)
        'met_root_dir': '/data/Met/PNW/4km/ARL/', # TODO: don't hardcode (see above)
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
        'queue': 'all-met', #'nam', # TODO: define elsewhere ? (see above)
        'met_root_dir': '/data/Met/NAM/12km/ARL/', # TODO: don't hardcode (see above)
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

##
## Domain database
##

class DomainDB(object):

    # TODO: memoize/cache find
    def find(self, domain_id=None):
        data = {}
        for d in MetDatesCollection(MONGODB_URL).find(domain=domain_id):
            data[d['domain']] = {
                "dates": d['complete_dates']
            }
            if d['domain'] in DOMAINS:
                data[d['domain']]['boundary'] = DOMAINS[d['domain']]['boundary']
        return data

##
## Utility methods
##

def get_met_boundary(domain):
    if domain not in DOMAINS:
        raise BlueSkyConfigurationError(
            "Unsupported met domain {}".format(domain))

    if not DOMAINS[domain].get('boundary'):
        raise BlueSkyConfigurationError(
            "Boundary not defined for met domain {}".format(domain))

    return DOMAINS[domain]['boundary']
