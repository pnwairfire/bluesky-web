#! /usr/bin/env python3

"""test-asynch-request.py: for ad hoc testing the web service's handling of
requests that result in executing bsp asynchrounously"""

__author__ = "Joel Dubowy"
__copyright__ = "Copyright 2015, AirFire, PNW, USFS"

import datetime
import json
import logging
import requests
import subprocess
import sys
import time
import urllib.request, urllib.parse, urllib.error

import afscripting as scripting

# Note: the trailing space seems to be the only way to add an extra trailing line
EPILOG_STR = """
Simple case, running only through emissions

  $ {script_name} --simple \\
        -r http://localhost:8887/bluesky-web/ \\
        --log-level=DEBUG

  (Change root url for test and prod envs.)


Full run (ingestiont through visualization)

  $ {script_name} \\
        -r http://localhost:8887/bluesky-web/ \\
        --log-level=DEBUG -s 2014-05-30T00:00:00 -n 12 \\
        --met-archive ca-nv_6-km

  $ {script_name} \\
        -r https://www.blueskywebhost.com/bluesky-web-test/ \\
        --log-level=DEBUG -s `date -v-1d +%Y-%m-%dT00:00:00` -n 12 \\
        --met-archive ca-nv_6-km

  $ {script_name} \\
        -r https://www.blueskywebhost.com/bluesky-web/ \\
        --log-level=DEBUG -s `date -v-1d +%Y-%m-%dT00:00:00` -n 12 \\
        --met-archive ca-nv_6-km

 """.format(script_name=sys.argv[0])

REQUIRED_ARGS = [
    {
        'short': '-r',
        'long': '--root-url',
        'help': 'api root url ; default http://localhost:8887/bluesky-web/',
        'default': 'http://localhost:8887/bluesky-web/'
    }
]

HYSPLIT_OPTIONS = {
    'standard': {
        'dispersion_speed': 'faster',
    },
    'advanced': {
        'number_of_particles': 'low',
        'grid_resolution': 'low'
    },
    'expert': {
        'number_of_particles': 'low',
        'grid_resolution': 'low',
        'grid_size': 0.25
    },
}

_NOW = datetime.datetime.utcnow()
OPTIONAL_ARGS = [
    {
        'long': '--run-id'
    },
    {
        'long': '--simple',
        'help': 'Run simple emissions request asynchronously',
        'action': "store_true",
        'default': False
    },
    {
        'short': '-s',
        'long': '--start',
        'help': "UTC start time of hysplit run; e.g. '2015-08-15T00:00:00'",
        'action': scripting.args.ParseDatetimeAction,
        'default': datetime.datetime(_NOW.year, _NOW.month, _NOW.day)
    },
    {
        'short': '-n',
        'long': '--num-hours',
        'help': 'number of hours in hysplit run',
        "type": int,
        'default': 12
    },
    {
        'short': '-a',
        'long': '--area',
        'help': 'area of fire, in acres; default 10000',
        "type": float,
        'default': 10000.0
    },
    {
        'long': '--smtp-server',
        'help': 'SMTP server; ex. localhost:25'
    },
    {
        'long': "--latitude",
        'help': 'latitude of fire location; default: 37.909644',
        'default':  37.909644,
        'type': float
    },
    {
        'long': "--longitude",
        'help': 'longitude of fire location; default: -119.7615805',
        'default': -119.7615805,
        'type': float
    },
    {
        'long': "--utc-offset",
        'help': 'utc offest of fire location; default: "-07:00"',
        'default': '-07:00'
    },
    {
        'long': "--met-archive",
        'help': "met archive; default 'ca-nv_6-km'",
        'default': 'ca-nv_6-km'
    },
    {
        'long': "--hysplit-options",
        'help': ', '.join(HYSPLIT_OPTIONS)
    },
    {
        'short': '-m',
        'long': '--module',
        'dest': 'modules',
        'help': "alternate module(s) to run",
        'default': [],
        'action': scripting.args.AppendOrSplitAndExtendAction
    },
    {
        'long': "--vsmoke",
        'help': "run VSMOKE dispersion model (if not running '--simple' mode)",
        'action': "store_true",
        'default': False
    },
    {
        'long': "--reproject-images",
        'help': "reproject images in blueskykml",
        'action': "store_true",
        'default': False
    }
]

REQUEST = {
    "config": {
        "emissions": {
            "species": ["PM2.5"]
        },
        "dispersion": {
            "start": None,  # WILL BE FILLED IN
            "num_hours": None,  # WILL BE FILLED IN
            'hysplit': {
                "VERTICAL_LEVELS": [100, 500, 1000]
            }
        },
        'visualization': {
            'hysplit': {
                "blueskykml_config": {
                    "DispersionGridInput": {
                        "LAYERS": [0, 1, 2]
                    },
                    "DispersionImages": {
                        "DAILY_IMAGES_UTC_OFFSETS": [-7, 0]
                    }
                }
            }
        },
        "export": {
            "extra_exports": ["dispersion", "visualization", "extrafiles"]
        }
    },
    "fire_information": [
        {
            "meta": {
                "vsmoke": {
                    "ws": 12,
                    "wd": 232
                }
            },
            "event_of": {
                "id": "SF11E826544",
                "name": "Natural Fire near Yosemite, CA"
            },
            "id": "SF11C14225236095807750",
            "type": "wildfire",
            "fuel_type": "natural",
            "growth": [
                {
                    "start": None,  # WILL BE FILLED IN
                    "end": None,  # WILL BE FILLED IN
                    "location": {
                        "area": None,  # WILL BE FILLED IN
                        "ecoregion": "western",
                        "latitude": None,  # WILL BE FILLED IN
                        "longitude": None,  # WILL BE FILLED IN
                        "utc_offset": None,  # WILL BE FILLED IN
                    }
                }
            ]
        },
        {
            "meta": {
                "vsmoke": {
                    "ws": 12,
                    "wd": 232
                }
            },
            "event_of": {
                "id": "SF11E826544",
                "name": "Activity Fire near Yosemite, CA"
            },
            "id": "ljo4tosghsjfdsdkf",
            "type": "rx",
            "fuel_type": "activity",
            "growth": [
                {
                    "start": None,  # WILL BE FILLED IN
                    "end": None,  # WILL BE FILLED IN
                    "location": {
                        "area": None,  # WILL BE FILLED IN
                        "ecoregion": "western",
                        "latitude": None,  # WILL BE FILLED IN
                        "longitude": None,  # WILL BE FILLED IN
                        "utc_offset": None,  # WILL BE FILLED IN
                    }
                }
            ]
        }
    ]
}
WRITE_OUT_PATTERN="%{http_code} (%{time_total}s)"

DT_STR = '%Y-%m-%dT%H:%M:%S'

HEADERS = {
    'Content-type': 'application/json',
    'Accept': 'application/json'
}

if __name__ == "__main__":
    parser, args = scripting.args.parse_args(REQUIRED_ARGS, OPTIONAL_ARGS,
        epilog=EPILOG_STR)

    if args.simple and args.modules:
        logging.error("Don't specify both '--simple' and '--modules'")
        sys.exit(1)

    if args.hysplit_options:
        if args.simple:
            logging.error("Don't specify both '--simple' and '--hysplit_options'")
            sys.exit(1)
        if args.hysplit_options not in HYSPLIT_OPTIONS:
            logging.error("Invalid value for '--hysplit_options': %s",
                args.hysplit_options)
            sys.exit(1)

    start_str = args.start.strftime(DT_STR)
    REQUEST['config']['dispersion']['start'] = start_str
    REQUEST['config']['dispersion']['num_hours'] = args.num_hours
    local_start_str = (
        args.start + datetime.timedelta(hours=-7)).strftime(DT_STR)
    local_end_str = (
        args.start + datetime.timedelta(hours=args.num_hours-7)).strftime(DT_STR)
    for i in range(2):
        REQUEST['fire_information'][i]['growth'][0]['start'] = local_start_str
        REQUEST['fire_information'][i]['growth'][0]['end'] = local_end_str
        REQUEST['fire_information'][i]['growth'][0]['location']['area'] = args.area
        REQUEST['fire_information'][i]['growth'][0]['location']['latitude'] = args.latitude + ((i-0.5)/10.0)
        REQUEST['fire_information'][i]['growth'][0]['location']['longitude'] = args.longitude
        REQUEST['fire_information'][i]['growth'][0]['location']['utc_offset'] = args.utc_offset

    if args.smtp_server:
        smtp_server, smtp_port = args.smtp_server.split(':')
        REQUEST['config']['export']['modes'] = ["email"]
        REQUEST['config']['export']["email"] = {
            "recipients": ["foo@bar.com"],
            "sender": "bluesky@blueskywebhost.com",
            "subject": "BSP output",
            "smtp_server": smtp_server,
            "smtp_port": smtp_port
        }

    if args.run_id:
        REQUEST['run_id'] = args.run_id

    if args.modules:
        REQUEST['modules'] = args.modules

    if args.reproject_images:
        REQUEST['config']['visualization']["hysplit"]["blueskykml_config"]["DispersionImages"] = {
            "REPROJECT_IMAGES": "True"
        }

    args.root_url = args.root_url.rstrip('/')

    logging.info("UTC start: {}".format(start_str))
    logging.info("Num hours: {}".format(args.num_hours))
    logging.info("Local start: {}".format(local_start_str))
    logging.info("Local end: {}".format(local_end_str))
    logging.info("Lat: {}".format(args.latitude))
    logging.info("Lng: {}".format(args.longitude))
    logging.info("Area: {}".format(args.area))
    if args.run_id:
        logging.info("Run Id: {}".format(args.run_id))
    if args.modules:
        logging.info("Modules: {}".format(args.modules))
    logging.info("Reprojecting images?: %s", args.reproject_images)

    data = json.dumps(REQUEST)
    logging.info("Request JSON: {}".format(data))

    url = "{}/api/v1/run/".format(args.root_url)
    query = {}
    if args.simple:
        #first get fuelbeds
        response = requests.post(url + 'fuelbeds/', data=data, headers=HEADERS)
        if response.status_code != 200:
            logging.error("Failed to look up fuelbeds to run emissions")
            sys.exit(1)
        data = response.content

        url += 'emissions/'
        query['_a'] = ''
    else:
        url += 'all/'
        if not args.vsmoke:
            url += '{}/'.format(args.met_archive)

    if args.hysplit_options:
        for k, v in HYSPLIT_OPTIONS[args.hysplit_options].items():
            query[k] = v
        if 'grid_size' in HYSPLIT_OPTIONS[args.hysplit_options]:
            # can only specify 'grid_size' option for single-fire runs
            data = json.loads(data)
            data['fire_information'].pop()
            data = json.dumps(data)

    url = '?'.join([url, urllib.parse.urlencode(query)])
    logging.info("Request URL: {}".format(data))

    logging.info("Testing {} ... ".format(url))

    response = requests.post(url, data=data, headers=HEADERS)
    logging.info("Response: {} - {}".format(response.status_code, response.content))

    if response.status_code != 200:
        logging.error("Failed initiate run")
        sys.exit(1)

    run_id = json.loads(response.content.decode())['run_id']
    logging.info("Run id: {}".format(run_id))
    while True:
        time.sleep(5)
        logging.info("Checking status...")
        url = "{}/api/v1/runs/{}/".format(args.root_url, run_id)
        response = requests.get(url, HEADERS)
        if response.status_code == 200:
            data = json.loads(response.content.decode())
            if data['complete']:
                logging.info("Complete")
                break
            else:
                logging.info("{} Complete".format(data['percent']))

    url =  "{}/api/v1/runs/{}/output/".format(args.root_url, run_id)
    response = requests.get(url, HEADERS)
    if response.status_code != 200:
        # TODO: add retry logic, since the run did succeed and complete
        logging.error("Failed to get output")
        sys.exit(1)

    data = json.loads(response.content.decode())
    # TODO: log individual bits of information
    logging.info("Reponse: {}".format(data))
    logging.info("Root Url: %s", data.get('root_url', 'N/A'))

