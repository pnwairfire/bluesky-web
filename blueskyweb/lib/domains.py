"""blueskyweb.lib.domain"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import logging
import math
import os

from bluesky.exceptions import BlueSkyConfigurationError
from bluesky.met.arlindexer import MetDatesCollection

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
        'queue': 'dri', # TODO: define elsewhere ? (see above)
        'met_root_dir': '/DRI_2km/', # TODO: don't hardcode (see above)
        "boundary": {
            # from STI: CANV 2km - [-124.3549, 32.5479, -113.2558, 41.8884]
            "center_latitude": 37.21815, # 37.0,
            "center_longitude": -118.80535, # -119.0,
            "width_longitude": 11.0991, # 13.0,
            "height_latitude": 9.3405, #11.5,
            "spacing_longitude": 0.1,  # TODO: is this correct?
            "spacing_latitude": 0.1  # TODO: is this correct?
        },
        "index_filename_pattern": "arl12hrindex.csv",
        "time_step": 1
    },
    'DRI6km': {
        'queue': 'dri', # TODO: define elsewhere ? (see above)
        'met_root_dir': '/DRI_6km/', # TODO: don't hardcode (see above)
        "boundary": {
            "center_latitude": 36.5,
            "center_longitude": -119.0,
            "width_longitude": 25.0,
            "height_latitude": 17.5,
            "spacing_longitude": 0.5,  # TODO: is this correct?
            "spacing_latitude": 0.5  # TODO: is this correct?
        },
        "index_filename_pattern": "arl12hrindex.csv",
        "time_step": 1
    },
    'NAM84': {
        'queue': 'nam', # TODO: define elsewhere ? (see above)
        'met_root_dir': '/NAM84/', # TODO: don't hardcode (see above)
        "boundary": {
            # from STI: NAM 12km - [-131, 18, -64, 55]
            "center_latitude": 36.5, # 37.5,
            "center_longitude": -97.5, # -95.0,
            "width_longitude": 67.0, # 70.0,
            "height_latitude": 37.0, # 30.0,
            "spacing_longitude": 0.5,  # TODO: is this correct?
            "spacing_latitude": 0.5  # TODO: is this correct?
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

KM_PER_DEG_LAT = 111
DEG_LAT_PER_KM = 1.0 / KM_PER_DEG_LAT
RADIANS_PER_DEG = math.pi / 180
KM_PER_DEG_LNG_AT_EQUATOR = 111.32

def km_per_deg_lng(lat):
    return KM_PER_DEG_LNG_AT_EQUATOR * math.cos(RADIANS_PER_DEG * lat)

def square_grid_from_lat_lng(lat, lng, length, domain):
    """

    args
     - lat -- latitude of grid center
     - lng -- longitude of grid center
     - length -- length of each side of grid
    """
    logging.debug("calculating {length}x{length} grid around {lat},{lng}".format(
        length=length, lat=lat, lng=lng))
    met_boundary = get_met_boundary(domain)
    width_lng = length / km_per_deg_lng(lat)
    d = {
        "CENTER_LATITUDE": lat,
        "CENTER_LONGITUDE": lng,
        "HEIGHT_LATITUDE": DEG_LAT_PER_KM * length,
        "WIDTH_LONGITUDE": width_lng,
        "SPACING_LONGITUDE": met_boundary["spacing_longitude"],
        "SPACING_LATITUDE": met_boundary["spacing_latitude"]
    }
    # TODO: truncate grid to keep within met domain grid
    #  boundary if the square extends ouside of met domain
    # TODO: truncate grid to keep from crossing pole and equator?
    return d
