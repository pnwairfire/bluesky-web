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
    'DRI2km': {
        'queue': 'dri', # TODO: define elsewhere ? (see above)
        'met_root_dir': '/DRI_2km/', # TODO: don't hardcode (see above)
        "boundary": {
            "center_latitude": 37.0,
            "center_longitude": -119.0,
            "width_longitude": 13.0,
            "height_latitude": 11.5,
            "spacing_longitude": 0.1,
            "spacing_latitude": 0.1
        }
    },
    'DRI6km': {
        'queue': 'dri', # TODO: define elsewhere ? (see above)
        'met_root_dir': '/DRI_6km/', # TODO: don't hardcode (see above)
        "boundary": {
            "center_latitude": 36.5,
            "center_longitude": -119.0,
            "width_longitude": 25.0,
            "height_latitude": 17.5,
            "spacing_longitude": 0.5,
            "spacing_latitude": 0.5
        }
    },
    'NAM84': {
        'queue': 'nam', # TODO: define elsewhere ? (see above)
        'met_root_dir': '/NAM84/', # TODO: don't hardcode (see above)
        "boundary": {
            "center_latitude": 37.5,
            "center_longitude": -95.0,
            "width_longitude": 70.0,
            "height_latitude": 30.0,
            "spacing_longitude": 0.5,  # TODO: is this correct?
            "spacing_latitude": 0.5  # TODO: is this correct?
        }
    }
}

class DomainDB(object):

    def find(self, domain_id=None):
        data = {}
        for d in MetDatesCollection(MONGODB_URL).find(domain=domain_id):
            data[d['domain']] = {
                "dates": d['complete_dates']
            }
            if d['domain'] in DOMAINS:
                data[d['domain']]['boundary'] = DOMAINS[d['domain']]['boundary']
        return data
