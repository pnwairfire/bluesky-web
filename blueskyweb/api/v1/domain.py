"""bluesky.web.api.v1.domain"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import datetime
import json
import tornado.web

## ***
## *** TODO: REPLACE DUMMY DATA WITH REAL!!!
## ***
## *** Will need to add configuration options to web service to point
## *** to source of data (e.g. url of mongodb containing the data vs.
## *** root url or path to crawl for data vs. something else...)
## ***

DUMMY_DOMAIN_DATA = {
    "NAM84": {
        "dates": [
            datetime.date.today().strftime("%Y%m%d"),
            (datetime.date.today() - datetime.timedelta(1)).strftime("%Y%m%d"),
            (datetime.date.today() - datetime.timedelta(2)).strftime("%Y%m%d")
        ],
        "boundary": {
            "center_latitude": 37.5,
            "center_longitude": -95.0,
            "width_longitude": 70.0,
            "height_latitude": 30.0,
            "spacing_longitude": 12,  # TODO: is this correct?
            "spacing_latitude": 12  # TODO: is this correct?
        }
    },
    "DRI2km": {
        "dates": [
            datetime.date.today().strftime("%Y%m%d"),
            (datetime.date.today() - datetime.timedelta(1)).strftime("%Y%m%d"),
            (datetime.date.today() - datetime.timedelta(2)).strftime("%Y%m%d")
        ],
        "boundary": {
            "center_latitude": 37.0,
            "center_longitude": -119.0,
            "width_longitude": 13.0,
            "height_latitude": 11.5,
            "spacing_longitude": 2,
            "spacing_latitude": 2
        }
    },
    "DRI6km": {
        "dates": [
            datetime.date.today().strftime("%Y%m%d"),
            (datetime.date.today() - datetime.timedelta(1)).strftime("%Y%m%d"),
            (datetime.date.today() - datetime.timedelta(2)).strftime("%Y%m%d")
        ],
        "boundary": {
            "center_latitude": 36.5,
            "center_longitude": -119.0,
            "width_longitude": 25.0,
            "height_latitude": 17.5,
            "spacing_longitude": 6,
            "spacing_latitude": 6
        }
    }
}

class DomainInfo(tornado.web.RequestHandler):

    def get(self, domain_id=None):
        if not domain_id:
            self.write({
                "domains": DUMMY_DOMAIN_DATA,
                "IS_DUMMY_DATA": True
            })
        elif domain_id in DUMMY_DOMAIN_DATA:
            self.write({
                domain_id: DUMMY_DOMAIN_DATA[domain_id],
                "IS_DUMMY_DATA": True
            })
        else:
            self.set_status(404, "Domain does not exist")


class DomainAvailableDates(tornado.web.RequestHandler):

    def get(self, domain_id=None):
        if not domain_id:
            self.write({
                "dates": {d: data['dates'] for d,data in DUMMY_DOMAIN_DATA.items()},
                "IS_DUMMY_DATA": True
            })
        elif domain_id in DUMMY_DOMAIN_DATA:
            self.write({
                "dates": DUMMY_DOMAIN_DATA[domain_id]["dates"],
                "IS_DUMMY_DATA": True
            })
        else:
            self.set_status(404, "Domain does not exist")
