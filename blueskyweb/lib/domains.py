"""blueskyweb.lib.domain"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import os

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
        "index_filename_pattern": "arl12hrindex.csv"
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
        "index_filename_pattern": "arl12hrindex.csv"
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
        "index_filename_pattern": "NAM84_ARL_index.csv"
    }
}

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
