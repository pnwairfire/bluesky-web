#! /usr/bin/env python

"""test-asynch-request.py: for ad hoc testing the web service's handling of
requests that result in executing bsp asynchrounously"""

__author__ = "Joel Dubowy"
__copyright__ = "Copyright 2015, AirFire, PNW, USFS"

import datetime
import subprocess

from pyairfire import scripting

REQUIRED_ARGS = [
    {
        'long': '--hostname',
        'dest': 'hostname',
        'help': 'hostname of web service; default localhost:8888',
        'action': 'store',
        'default': 'localhost:8888'
    }
]

OPTIONAL_ARGS = [
    {
        'long': '--simple',
        'dest': 'simple',
        'help': 'Run simple asynchrounous request (through emissions',
        'action': "store_true",
        'type': bool,
        'default': False
    },
    {
        'short': '-s',
        'long': '--start',
        'dest': 'start',
        'help': "UTC start time of hysplit run; e.g. '2015-08-15T00:00:00'",
        'action': scripting.args.ParseDatetimeAction,
        'default': datetime.datetime.utcnow().date()
    },
    {
        'short': '-n',
        'long': '--num-hours',
        'dest': 'num_hours',
        'help': 'number of hours in hysplit run',
        'action': "store",
        "type": int,
        'default': 24
    }
]

REQUEST = {
    "config": {
        "emissions": {
            "species": ["PM25"]
        },
        "findmetdata": {
            "met_root_dir": "/DRI_6km/"
        },
        "dispersion": {
            "start": None,  # WILL BE FILLED IN
            "num_hours": None,  # WILL BE FILLED IN
            "model": "hysplit",
            "dest_dir": "/home/vagrant/bsp-dispersion-output/",
            "hysplit": {
                "grid": {
                    "spacing": 6.0,
                    "boundary": {
                        "ne": {
                            "lat": 45.25,
                            "lng": -106.5
                        },
                        "sw": {
                            "lat": 27.75,
                            "lng": -131.5
                        }
                    }
                }
            }
        },
        "visualization": {
            "target": "dispersion",
            "hysplit": {
                "images_dir": "images/",
                "data_dir": "data/"
            }
        },
        "export": {
            "modes": ["email"],
            "extra_exports": ["dispersion", "visualization"],
            "email": {
                "recipients": ["foo@bar.com"],
                "sender": "bluesky@blueskywebhost.com",
                "subject": "BSP output",
                "smtp_server": "127.0.0.1",
                "smtp_port": 1025
            }
        }
    },
    "fire_information": [
        {
            "event_of": {
                "id": "SF11E826544",
                "name": "Natural Fire near Yosemite, CA"
            },
            "id": "SF11C14225236095807750",
            "type": "natural",
            "location": {
                "area": 10000,
                "ecoregion": "western",
                "latitude": 37.909644,
                "longitude": -119.7615805,
                "utc_offset": "-07:00"
            },
            "growth": [
                {
                    "start": None,  # WILL BE FILLED IN
                    "end": None,  # WILL BE FILLED IN
                    "pct": 100.0
                }
            ]
        }
    ]
}
WRITE_OUT_PATTERN="%{http_code} (%{time_total}s)"

DT_STR = '%Y-%m-%dT%H:%M:%S'

if __name__ == "__main__":
    parser, args = scripting.args.parse_args(REQUIRED_ARGS, OPTIONAL_ARGS)
    REQUEST['modules'] = ['ingestion', 'fuelbeds', 'consumption', 'emissions']
    if not args.simple:
        REQUEST['modules'].extend(['timeprofiling', 'findmetdata', 'localmet',
            'plumerising', 'dispersion', 'visualization', 'export'])

    start_str = args.start.strftime(DT_STR)
    REQUEST['config']['dispersion']['start'] = start_str
    REQUEST['config']['dispersion']['num_hours'] = args.num_hours
    local_start_str = (
        args.start + datetime.timedelta(hours=-7)).strftime(DT_STR)
    local_end_str = (
        args.start + datetime.timedelta(hours=args.num_hours-7)).strftime(DT_STR)
    REQUEST['fire_information'][0]['growth'][0]['start'] = local_start_str
    REQUEST['fire_information'][0]['growth'][0]['end'] = local_end_str

    logging.info("UTC start: {}".format(start_str))
    logging.info("Num hours: {}".format(args.num_hours))
    logging.info("Local start: {}".format(local_start_str))
    logging.info("Locatl end: {}".format(local_end_str))

    url = "http://{}/api/v1/run/".format(args.hostname)
    if args.simple:
        url += '?run_asynch='
    logging.info("Testing {} ... ".format(url))

    response = subprocess.check_output([
       'curl', '"{}"'.format(url),
        '--write-out',  '"{}"'.format(WRITE_OUT_PATTERN),
        '--silent', '-H', '"Content-Type: application/json"',
        '-X', 'POST', '-d', "'{}'".format(REQUEST)])

    import pdb;pdb.set_trace()
    logging.info("Response: {}".format(response))
    # TODO: log response, parse run_id, and poll for results, printing progress

    # echo -n "http://$BLUESKY_API_HOSTNAME/api/v1/run/ - " >> $OUTPUT_FILE
