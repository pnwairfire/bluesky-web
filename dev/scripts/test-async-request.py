#! /usr/bin/env python3

"""test-async-request.py: for ad hoc testing the web service's handling of
requests that result in executing bsp asynchrounously"""

__author__ = "Joel Dubowy"
__copyright__ = "Copyright 2015, AirFire, PNW, USFS"

import datetime
import json
import logging
import os
import requests
import subprocess
import sys
import time
import urllib.request, urllib.parse, urllib.error

import afscripting as scripting


DEV_LOG_DIR = os.path.abspath(os.path.join(sys.path[0], '..', 'logs', os.path.basename(sys.argv[0]))).strip('.py')
os.makedirs(DEV_LOG_DIR, exist_ok=True)

# Note: the trailing space seems to be the only way to add an extra trailing line
EPILOG_STR = """
Running only through emissions

  $ {script_name} --log-level=DEBUG -v 4.2 --emissions \\
        -r http://localhost:8887/bluesky-web/

  (Change root url for test and prod envs.)

Run through plumerise

  $ {script_name} --log-level=DEBUG -v 4.2 --plumerise \\
        -r http://localhost:8887/bluesky-web/


Full run (ingestiont through visualization)

  $ {script_name} --log-level=DEBUG -v 4.2 \\
        -r http://localhost:8887/bluesky-web/ \\
        --latitude 45 -s 2019-07-26T00:00:00 -n 12 \\
        --met-archive pacific_northwest_4-km

  $ {script_name} --log-level=DEBUG -v 4.2 \\
        -r http://localhost:8887/bluesky-web/ \\
        -s 2019-06-11T00:00:00 -n 12 \\
        --met-archive ca-nv_4-km

  $ {script_name} --log-level=DEBUG -v 4.2 \\
        -r http://localhost:8887/bluesky-web/ \\
        -s `date -d"-1 day" +%Y-%m-%dT00:00:00` -n 12 \\
        --met-archive ca-nv_4-km

(On unix, use `date -v-1d +%Y-%m-%dT00:00:00`.)

 """.format(script_name=sys.argv[0])

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
                        "REPROJECT_IMAGES": "True"
                        #"DAILY_IMAGES_UTC_OFFSETS": [-7, 0]
                    }
                }
            }
        },
        "export": {
            "extra_exports": ["dispersion", "visualization", "extrafiles"]
        }
    }
}

FIRES_DATA = {
    '1': {
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
                            # 'latitude' & longitude or geojson WILL BE FILLED IN
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
                            # 'latitude' & longitude or geojson WILL BE FILLED IN
                            "utc_offset": None,  # WILL BE FILLED IN
                        }
                    }
                ]
            }
        ]
    },
    '4.1': {
        "fires": [
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
                "activity": [
                    {
                        "active_areas": [
                            {
                                "start": None,  # WILL BE FILLED IN
                                "end": None,  # WILL BE FILLED IN
                                # specified_points or polygon WILL BE FILLED IN
                                "utc_offset": None,  # WILL BE FILLED IN
                            }
                        ]
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
                "activity": [
                    {
                        "active_areas": [
                            {
                                "start": None,  # WILL BE FILLED IN
                                "end": None,  # WILL BE FILLED IN
                                "utc_offset": None,  # WILL BE FILLED IN
                            }
                        ]
                    }
                ]
            }
        ]
    },
    # 4.2 input data is the same as for 4.1
    '4.2': {
        "fires": [
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
                "activity": [
                    {
                        "active_areas": [
                            {
                                "start": None,  # WILL BE FILLED IN
                                "end": None,  # WILL BE FILLED IN
                                # specified_points or polygon WILL BE FILLED IN
                                "utc_offset": None,  # WILL BE FILLED IN
                            }
                        ]
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
                "activity": [
                    {
                        "active_areas": [
                            {
                                "start": None,  # WILL BE FILLED IN
                                "end": None,  # WILL BE FILLED IN
                                "utc_offset": None,  # WILL BE FILLED IN
                            }
                        ]
                    }
                ]
            }
        ]
    }
}

REQUIRED_ARGS = [
    {
        'short': '-r',
        'long': '--root-url',
        'help': 'api root url ; default http://localhost:8887/bluesky-web/',
        'default': 'http://localhost:8887/bluesky-web/'
    },
    {
        'short': '-v',
        'long': '--api-version',
        'help': "Must be one of the following: {}".format(
            ', '.join(FIRES_DATA.keys()))
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
        'grid_size': 0.5
    },
}

_NOW = datetime.datetime.utcnow()
OPTIONAL_ARGS = [
    {
        'long': '--run-id'
    },
    {
        'long': '--emissions',
        'help': 'Run emissions request asynchronously',
        'action': "store_true"
    },
    {
        'long': '--plumerise',
        'help': 'Run plumerise',
        'action': "store_true"
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
        'long': '--email-recipient',
        'help': 'email address to send output to'
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
        'help': "met archive; default 'ca-nv_4-km'",
        'default': 'ca-nv_4-km'
    },
    {
        'long': "--single-fire",
        'help': ', '.join(HYSPLIT_OPTIONS),
        'action': 'store_true'
    },
    {
        'long': "--hysplit-options",
        'help': ', '.join(HYSPLIT_OPTIONS)
    },
    {
        'long': "--polygon",
        'help': 'specify polygon area instead of single lat,lng',
        'action': 'store_true'
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
        'help': "run VSMOKE dispersion model (if not running '--emissions' mode)",
        'action': "store_true"
    },
    {
        'long': "--reproject-images",
        'help': "reproject images in blueskykml",
        'action': "store_true"
    },
    {
        'long': "--daily-images-utc-offsets",
        'help': "comma separated list of utc offset for daily images"
    },
    {
        'long': '--indent',
        'help': 'Format output json with newlines and given indent',
        'type': int
    },
    {
        'long': '--write-req-resp-to-file',
        'help': 'write the request and response to file',
        'action': 'store_true'
    },
    {
        'short': '-o',
        'long': '--output-file',
        'help': 'write final output to file'
    }
]



WRITE_OUT_PATTERN="%{http_code} (%{time_total}s)"

DT_STR = '%Y-%m-%dT%H:%M:%S'

HEADERS = {
    'Content-type': 'application/json',
    'Accept': 'application/json'
}

def to_indented_json_string(data):
    try:
        if hasattr(data, 'lower'):
            if hasattr(data, 'decode'):
                data = data.decode()
            data = json.loads(data)
        return json.dumps(data, indent=args.indent)
    except:
        return data

def write_to_req_resp_file(args, title, url, req, resp):
    logging.info("%s: %s", title, data)
    if args.write_req_resp_to_file:
        req = to_indented_json_string(req)
        resp = to_indented_json_string(resp)
        filename = os.path.join(DEV_LOG_DIR, args.run_id + '.log')
        with open(filename, 'a') as f:
            f.write('-' * 80)
            f.write(title + ":\n")
            f.write(url + "\n")
            f.write(req + "\n")
            f.write(resp + "\n")


def load_response_body(response):
    body = response.content.decode()
    try:
        return json.loads(body)
    except Exception:
        logging.error("Failed to load response:  %s", body)
        raise

def get(args, url, title, ignore_fail=False):
    response = requests.get(url, HEADERS)
    if not ignore_fail and response.status_code != 200:
        # TODO: add retry logic, since the run did succeed and complete
        logging.error("Failed to get %s", title)
        sys.exit(1)
    write_to_req_resp_file(args, title,
        url + 'fuelbeds/', data, response.content)

    return response.status_code, load_response_body(response)

def post(args, url, data, desc):
    if not hasattr(data, 'lower'):
        data = json.dumps(data)
    response = requests.post(url, data=data, headers=HEADERS)
    write_to_req_resp_file(args, desc,
        url + 'fuelbeds/', data, response.content)
    if response.status_code != 200:
        logging.error("Failed at %s", desc.lower())
        logging.error("Failed at %s", response.content)
        sys.exit(1)
    return load_response_body(response)

def parse_args():
    parser, args = scripting.args.parse_args(REQUIRED_ARGS, OPTIONAL_ARGS,
        epilog=EPILOG_STR)

    if (args.emissions or args.plumerise) and args.modules:
        logging.error("Don't specify '--modules' with either "
            "'--emissions' and '--plumerise'")
        sys.exit(1)

    if args.hysplit_options:
        if args.emissions or args.plumerise:
            logging.error("Don't specify '--hysplit_options' "
            "with either '--emissions' and '--plumerise'")
            sys.exit(1)
        if args.hysplit_options not in HYSPLIT_OPTIONS:
            logging.error("Invalid value for '--hysplit_options': %s",
                args.hysplit_options)
            sys.exit(1)

    if not args.run_id:
        if args.emissions:
            mode = 'emissions'
        elif args.plumerise:
            mode = 'plumerise'
        elif args.modules:
            mode = 'custom-module'
        else:
            mode = 'dispersion'
        args.run_id = "test-asynch-request-{}-{}".format(mode,
            datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%S"))

    args.root_url = args.root_url.rstrip('/')

    logging.info("Lat: {}".format(args.latitude))
    logging.info("Lng: {}".format(args.longitude))
    logging.info("Area: {}".format(args.area))
    logging.info("Run Id: {}".format(args.run_id))
    if args.modules:
        logging.info("Modules: {}".format(args.modules))
    logging.info("Reprojecting images?: %s", args.reproject_images)
    logging.info("Num hours: {}".format(args.num_hours))

    return args


def create_initial_request(args):
    start_str = args.start.strftime(DT_STR)
    REQUEST['config']['dispersion']['start'] = start_str
    REQUEST['config']['dispersion']['num_hours'] = args.num_hours
    local_start_str = (
        args.start + datetime.timedelta(hours=-7)).strftime(DT_STR)
    local_end_str = (
        args.start + datetime.timedelta(hours=args.num_hours-7)).strftime(DT_STR)

    logging.info("UTC start: {}".format(start_str))
    logging.info("Local start: {}".format(local_start_str))
    logging.info("Local end: {}".format(local_end_str))

    if args.api_version not in FIRES_DATA:
        print('** ERROR - API version not supported: %s', args.api_version)
        print('**    (choose from  %s)', ', '.join(FIRES_DATA.keys()))

    REQUEST.update(FIRES_DATA[args.api_version])

    request_fires = (REQUEST['fire_information']
        if args.api_version == '1' else REQUEST['fires'])

    if args.single_fire:
        request_fires.pop()

    for i in range(len(request_fires)):
        lat = args.latitude + ((i-0.5)/10.0)
        polygon =                         [
            [args.longitude - 0.03, lat + 0.02],
            [args.longitude + 0.03, lat + 0.02],
            [args.longitude + 0.03, lat - 0.02],
            [args.longitude - 0.03, lat - 0.02],
            [args.longitude - 0.03, lat + 0.02]
        ]
        if args.api_version == '1':
            request_fires[i]['growth'][0]['start'] = local_start_str
            request_fires[i]['growth'][0]['end'] = local_end_str
            request_fires[i]['growth'][0]['location']['utc_offset'] = args.utc_offset
            request_fires[i]['growth'][0]['location']['area'] = args.area
            if args.polygon:
                request_fires[i]['growth'][0]['location']['geojson'] = {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [
                            polygon
                        ]
                    ]
                }
            else:
                request_fires[i]['growth'][0]['location']['latitude'] = lat
                request_fires[i]['growth'][0]['location']['longitude'] = args.longitude

        else:
            request_fires[i]['activity'][0]['active_areas'][0]["start"] = local_start_str
            request_fires[i]['activity'][0]['active_areas'][0]["end"] = local_end_str
            request_fires[i]['activity'][0]['active_areas'][0]["utc_offset"] = args.utc_offset
            if args.polygon:
                request_fires[i]['activity'][0]['active_areas'][0]['polygon'] = {
                    'perimeter': polygon,
                    'area': args.area
                }
            else:
                request_fires[i]['activity'][0]['active_areas'][0]["specified_points"] = [
                    {
                        "lat": lat,
                        "lng": args.longitude,
                        "area": args.area,
                    }
                ]


    if args.smtp_server:
        if not args.email_recipient:
            logging.error("Specify --email-recipient along with --smtp-server", title)
            sys.exit(1)

        smtp_server, smtp_port = args.smtp_server.split(':')
        REQUEST['config']['export']['modes'] = ["email"]
        REQUEST['config']['export']["email"] = {
            "recipients": [args.email_recipient],
            "sender": "bluesky@blueskywebhost.com",
            "subject": "BSP output",
            "smtp_server": smtp_server,
            "smtp_port": smtp_port
        }

    REQUEST['run_id'] = args.run_id

    if args.modules:
        REQUEST['modules'] = args.modules

    if args.reproject_images:
        REQUEST['config']['visualization']["hysplit"]["blueskykml_config"]["DispersionImages"] = {
            "REPROJECT_IMAGES": "True"
        }
    if args.daily_images_utc_offsets:
        REQUEST['config']['visualization']["hysplit"]["blueskykml_config"]["DispersionImages"] = {
            "DAILY_IMAGES_UTC_OFFSETS": args.daily_images_utc_offsets.split(',')
        }


    return json.dumps(REQUEST)


if __name__ == "__main__":
    args = parse_args()

    data = create_initial_request(args)

    url = "{}/api/v{}/run/".format(args.root_url, args.api_version)
    query = {}
    if args.emissions or args.plumerise:
        #first get fuelbeds
        data = post(args, url + 'fuelbeds/', data,
            "Looking up fuelbeds to run %s".format(
            'emissions' if args.emissions else 'plumerise'))

        if args.plumerise:
            # next, for plumerise run, get emissions
            data = post(args, url + 'emissions/', data, "Running emissions to run plumerise")
            url += 'plumerise/{}/'.format(args.met_archive)

        else:
            url += 'emissions/'
            query['_a'] = ''

    else:
        url += 'all/'
        if not args.vsmoke:
            url += '{}/'.format(args.met_archive)

    if args.hysplit_options:
        for k, v in HYSPLIT_OPTIONS[args.hysplit_options].items():
            query[k] = v

    url = '?'.join([url, urllib.parse.urlencode(query)])
    data = post(args, url, data, "Initiating Run")

    logging.info("Run id: {}".format(REQUEST['run_id']))
    while True:
        time.sleep(5)
        logging.info("Checking status...")
        url = "{}/api/v{}/runs/{}/".format(
            args.root_url, args.api_version, REQUEST['run_id'])
        status_code, data = get(args, url, "status", ignore_fail=True)
        if status_code == 200:
            if data['complete']:
                logging.info("Complete")
                break
            else:
                logging.info("{} Complete".format(data['percent']))

    url =  "{}/api/v{}/runs/{}/output/".format(
        args.root_url, args.api_version, REQUEST['run_id'])
    status_code, data = get(args, url, "output")

    # TODO: log individual bits of information
    data_str = json.dumps(data, indent=args.indent)
    logging.info("Root Url: %s", data.get('root_url', 'N/A'))

    if args.output_file:
        with open(args.output_file, 'w') as f:
            f.write(data_str)
        logging.info("Reponse written to file: {}".format(args.output_file))
    else:
        logging.info("Reponse: {}".format(data_str))
