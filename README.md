# BlueSky Web

The blueskyweb package contains a tornado web service, wrapping
[bluesky][https://github.com/pnwairfire/bluesky],
that can be started by simply running ```bsp-web```.

## Non-python Dependencies

## Python dependencies to install manually

blueskyweb depends on the
[bluesky scheduler](https://bitbucket.org/fera/airfire-bluesky-scheduler),
another repo in AirFire's private bitbucket account.  Install it with the following:

    git clone git@bitbucket.org:fera/airfire-bluesky-scheduler.git
    cd airfire-bluesky-scheduler
    pip install --trusted-host pypi.smoke.airfire.org -r requirements.txt
    python setup.py install

### mongodb

BlueSky web connects to a mongodb database to query met data availability.
You just need to provide the url of one that is running.

## Development

### Clone Repo

Via ssh:

    git clone git@bitbucket.org:fera/airfire-bluesky-web.git

or http:

    git clone https://jdubowy@bitbucket.org/fera/airfire-bluesky-web.git

### Install Dependencies

First, install pip (with sudo if necessary):

    apt-get install python-pip

Run the following to install python dependencies:

    pip install --trusted-host pypi.smoke.airfire.org -r requirements.txt

Run the following to install packages required for development:

    pip install -r requirements-dev.txt

## Running

Use the help (-h) option to see usage and available config options:

    bsp-web -h

### Fabric

For the convenience of those wishing to run the web service on a remote server,
this repo contains a fabfile defining tasks for setting up,
deploying to, and restarting the service on a remote server.

To see what tasks are available, clone the repo, cd into it, and run

    git clone git@bitbucket.org:fera/airfire-bluesky-web.git
    cd bluesky-web
    BLUESKYWEB_SERVERS=username@hostname fab -l

(The 'BLUESKYWEB_SERVERS=username@hostname' is needed because it's used to set
the role definitions, which are be done at the module scope.)

To see documentation for a specific task, use the '-d' option. E.g.:

    BLUESKYWEB_SERVERS=username@hostname fab -d deploy

#### Examples

##### VM managed by vagrant

    export PYTHON_VERSION=2.7.8
    export VIRTUALENV_NAME=vm-playground
    export BLUESKYWEB_SERVERS=vagrant@127.0.0.1:2222
    export PROXY_VIA_APACHE=
    export EXPORT_MODE=localsave
    fab -A setup
    fab -A provision
    fab -A deploy

Note that the deploy task takes care of restarting.

##### Two remote servers

    export BLUESKYWEB_SERVERS=username-a@hostname-a,username-b@hostname-b
    export EXPORT_MODE=upload
    fab -A setup
    fab -A provision
    fab -A deploy

##### Playground

    export PYTHON_VERSION=2.7.8
    export VIRTUALENV_NAME=playground
    export BLUESKYWEB_SERVERS=user@server1
    export PROXY_VIA_APACHE=
    export EXPORT_MODE=localsave  # TODO: eventaully make it 'upload' if necessary
    fab -A setup
    fab -A provision
    fab -A deploy


#### Old pg.blueskywebhost.com env (*** DELETE THIS SECTION ONCE RETIRED ***)

    export PYTHON_VERSION=2.7.8
    export VIRTUALENV_NAME=playground
    export BLUESKYWEB_SERVERS=user@server2
    export PROXY_VIA_APACHE=
    export EXPORT_MODE=localsave
    fab -A setup
    fab -A provision
    fab -A deploy



## APIs

### GET /api/v1/domains/

This API returns information about all domains with ARL data

#### Request

 - url: http://$BLUESKY_API_HOSTNAME/api/v1/domains/
 - method: GET

#### Response

    {
        "domains": {
            "<domain_id>": {
                "dates": [
                    <date>,
                    ...
                ],
                "boundary": {
                    "center_latitude": <lat>,
                    "center_longitude": <lng>,
                    "width_longitude": <degrees>,
                    "height_latitude": <degrees>
                },
                <other_domain_data?>: <data>,
                ...
            },
            ...
        }
    }

#### Example

    $ curl "http://$BLUESKY_API_HOSTNAME/api/v1/domains/" | python -m json.tool
    {
         "domains": {
            "DRI2km": {
                "boundary": {
                    "center_latitude": 37.0,
                    "center_longitude": -119.0,
                    "height_latitude": 11.5,
                    "width_longitude": 13.0
                },
                "dates": [
                    "20151124",
                    "20151123",
                    "20151122"
                ]
            },
            "DRI6km": {
                "boundary": {
                    "center_latitude": 36.5,
                    "center_longitude": -119.0,
                    "height_latitude": 17.5,
                    "width_longitude": 25.0
                },
                "dates": [
                    "20151124",
                    "20151123",
                    "20151122"
                ]
            },
            "NAM84": {
                "boundary": {
                    "center_latitude": 37.5,
                    "center_longitude": -95.0,
                    "height_latitude": 30.0,
                    "width_longitude": 70.0
                },
                "dates": [
                    "20151124",
                    "20151123",
                    "20151122"
                ]
            }
        }
    }

### GET /api/v1/domains/<domain_id>/

This API returns information about a specific domain with ARL data

#### Request

 - url: http://$BLUESKY_API_HOSTNAME/api/v1/domains/<domain_id>/
 - method: GET

#### Response

    {
        "<domain_id>": {
            "dates": [
                <date>,
                ...
            ],
            "boundary": {
                "center_latitude": <lat>,
                "center_longitude": <lng>,
                "width_longitude": <degrees>,
                "height_latitude": <degrees>
            },
            <other_domain_data?>: <data>,
            ...
        }
    }

#### Example

    $ curl "http://$BLUESKY_API_HOSTNAME/api/v1/domains/DRI2km/" | python -m json.tool
    {
        "DRI2km": {
            "boundary": {
                "center_latitude": 37.0,
                "center_longitude": -119.0,
                "height_latitude": 11.5,
                "width_longitude": 13.0
            },
            "dates": [
                "20151124",
                "20151123",
                "20151122"
            ]
        }
    }

### GET /api/v1/domains/<domain_id>/available-dates/

This API returns the dates for which a specific d has ARL data

#### Request

 - url: http://$BLUESKY_API_HOSTNAME/api/v1/domains/<domain_id>/available-dates
 - method: GET

#### Response

    {
        "dates": [
           <date>,
           ...
        ]
    }


#### Example

    $ curl "http://$BLUESKY_API_HOSTNAME/api/v1/domains/DRI2km/available-dates" | python -m json.tool

    {
        "dates": [
            "20151124",
            "20151123",
            "20151122"
        ]
    }


### GET /api/v1/available-dates/

This API returns the dates, by domain, for which there exist ARL data

#### Request

 - url: http://$BLUESKY_API_HOSTNAME/api/v1/available-dates/
 - method: GET

#### Response

    {
        "dates": [
            "<domain_id>": [
                <date>,
                ...
            ]
           ...
        ]
    }


#### Example

    $ curl "http://$BLUESKY_API_HOSTNAME/api/v1/available-dates" | python -m json.tool
    {
        "dates": {
            "DRI2km": [
                "20151124",
                "20151123",
                "20151122"
            ],
            "DRI6km": [
                "20151124",
                "20151123",
                "20151122"
            ],
            "NAM84": [
                "20151124",
                "20151123",
                "20151122"
            ]
        }
    }

### POST /api/v1/run/fuelbeds/

This API runs bluesky through ingestion and fuelbeds.
It requires posted JSON with three possible top level keys -
'fire_information', and 'config', and 'modules'. The
'fire_information' key is required, and it lists the one or
more fires to process. The 'config' key is
optional, and it specifies configuration data and other control
parameters.  The 'modules' is also optional, and is used to
specify a subset of the modules normally run by this API.

#### Request

 - url: http://$BLUESKY_API_HOSTNAME/api/v1/run/fuelbeds/
 - method: POST
 - post data:

        {
            "fire_information": [ ... ],
            "config": { ... },
            "modules": [ ... ]
        }

See [BlueSky Pipeline](../../README.md) for more information about required
and optional post data

#### Response

In handling this request, blueskyweb will run bluesky in realtime, and the
bluesky results will be in the API response.  The response data will be the
modified version of the request data.  It will include the
"fire_information" key, the "config" key (if specified), a "processing"
key that includes information from the modules that processed the data, and
a "summary" key.

    {
        "config": { ... },
        "fire_information": [ ... ],
        "modules": [ ... ],
        "processing": [ ... ],
        "run_id": "<RUN_ID>",
        "summary": { ... }
    }

#### Examples

An example with fire location data specified as a perimeter

    $ curl "http://$BLUESKY_API_HOSTNAME/api/v1/run/fuelbeds/" -H 'Content-Type: application/json' -d '
    {
        "fire_information": [
            {
                "id": "SF11C14225236095807750",
                "event_id": "SF11E826544",
                "name": "Natural Fire near Snoqualmie Pass, WA",
                "growth": [
                    {
                        "location": {
                            "perimeter": {
                                "type": "MultiPolygon",
                                "coordinates": [
                                    [
                                        [
                                            [-121.4522115, 47.4316976],
                                            [-121.3990506, 47.4316976],
                                            [-121.3990506, 47.4099293],
                                            [-121.4522115, 47.4099293],
                                            [-121.4522115, 47.4316976]
                                        ]
                                    ]
                                ]
                            },
                            "area": 200,
                            "ecoregion": "southern",
                            "utc_offset": "-09:00"
                        }
                    }
                ]
            }
        ]
    }' | python -m json.tool

Another exmaple, this time running only the fuelbeds
modules, and with fire location data specified as lat + lng + size.

    $ curl "http://$BLUESKY_API_HOSTNAME/api/v1/run/fuelbeds/" -H 'Content-Type: application/json' -d '
    {
        "modules": ["fuelbeds"],
        "fire_information": [
            {
                "id": "SF11C14225236095807750",
                "event_of": {
                    "id": "SF11E826544",
                    "name": "Natural Fire near Snoqualmie Pass, WA"
                },
                "growth": [
                    {
                        "location": {
                            "latitude": 47.4316976,
                            "longitude": -121.3990506,
                            "area": 200,
                            "utc_offset": "-09:00",
                            "ecoregion": "southern"
                        }
                    }
                }
            }
        ]
    }' | python -m json.tool

### POST /api/v1/run/emissions/

This API runs bluesky through consumption and emissions.
It requires posted JSON with three possible top level keys -
'fire_information', and 'config', and 'modules'. The
'fire_information' key is required, and it lists the one or
more fires to process. The 'config' key is
optional, and it specifies configuration data and other control
parameters.  The 'modules' key is also optional, and is used to
specify a subset of the modules normally run by this API.

#### Request

 - url: http://$BLUESKY_API_HOSTNAME/api/v1/run/emissions/
 - method: POST
 - post data:

        {
            "fire_information": [ ... ],
            "config": { ... },
            "modules": [ ... ]
        }

See [BlueSky Pipeline](../../README.md) for more information about required
and optional post data

#### Response

In handling this request, blueskyweb will run bluesky in realtime, and the
bluesky results will be in the API response.  The response data will be the
modified version of the request data.  It will include the
"fire_information" key, the "config" key (if specified), a "processing"
key that includes information from the modules that processed the data, and
a "summary" key.

    {
        "config": { ... },
        "fire_information": [ ... ],
        "modules": [ ... ],
        "processing": [ ... ],
        "run_id": "<RUN_ID>",
        "summary": { ... }
    }

#### Examples

An example with fire location data specified as a perimeter

    $ curl "http://$BLUESKY_API_HOSTNAME/api/v1/run/emissions/" -H 'Content-Type: application/json' -d '
    {
        "fire_information": [
            {
                "id": "SF11C14225236095807750",
                "event_id": "SF11E826544",
                "name": "Natural Fire near Snoqualmie Pass, WA",
                "location": {
                    "perimeter": {
                        "type": "MultiPolygon",
                        "coordinates": [
                            [
                                [
                                    [-121.4522115, 47.4316976],
                                    [-121.3990506, 47.4316976],
                                    [-121.3990506, 47.4099293],
                                    [-121.4522115, 47.4099293],
                                    [-121.4522115, 47.4316976]
                                ]
                            ]
                        ]
                    },
                    "ecoregion": "southern",
                    "utc_offset": "-09:00",
                    "area": 5000
                },
                "fuelbeds": [
                    {
                        "fccs_id": "9",
                        "pct": 100.0
                    }
                ]
            }
        ]
    }' | python -m json.tool

Another exmaple, this time running only the consumption
modules, and with fire location data specified as lat + lng + size.

    $ curl "http://$BLUESKY_API_HOSTNAME/api/v1/run/emissions/" -H 'Content-Type: application/json' -d '
    {
        "modules": ["consumption"],
        "fire_information": [
            {
                "id": "SF11C14225236095807750",
                "event_of": {
                    "id": "SF11E826544",
                    "name": "Natural Fire near Snoqualmie Pass, WA"
                },
                "growth": [
                    {
                        "location": {
                            "latitude": 47.4316976,
                            "longitude": -121.3990506,
                            "area": 200,
                            "utc_offset": "-09:00",
                            "ecoregion": "southern"
                        },
                        "fuelbeds": [
                            {
                                "fccs_id": "9",
                                "pct": 100.0
                            }
                        ]
                    }
                ]
            }
        ]
    }' | python -m json.tool

### POST /api/v1/run/dispersion/<met_domain>/

This API takes emissions data and runs bluesky through dispersion and
visualization.  It's the dispersion API to be used for met-dependent
dispersion models (e.g. hysplit, which currently the only such model
supported).

Like with the emissions API, This API requires posted JSON with three
possible top level keys - 'fire_information', 'config', and 'modules.
The 'fire_information' key is required, and must contain emissions data
and growth time windows for each fire. The 'config' key is also
required, to specify, at the very least, dispersion start time
and num_hours.  The 'modules' key is optional.

Since dispersion is run, bluesky will be run asynchronously, and the
API response will include a guid to identify the run in subsequent
status and output API requests (described below).

    {
        run_id: <guid>
    }

#### Example

Since this API requires emissions data, consumption data is not required,
and so has been optionally stripped from the following request

    $ curl "http://$BLUESKY_API_HOSTNAME/api/v1/run/dispersion/DRI2km/" -H 'Content-Type: application/json' -d '
    {
        "fire_information": [
            {
                "event_of": {
                    "id": "SF11E826544",
                    "name": "Natural Fire near Yosemite, CA"
                },
                "id": "SF11C14225236095807750",
                "type": "wildfire",
                "growth": [
                    {
                        "location": {
                            "area": 10000,
                            "ecoregion": "western",
                            "latitude": 37.909644,
                            "longitude": -119.7615805,
                            "utc_offset": "-07:00"
                        },
                        "fuelbeds": [
                            {
                                "fccs_id": "49",
                                "pct": 50.0,
                                "emissions": {
                                    "flaming": {
                                        "PM25": [3002.3815120047017005]
                                    },
                                    "residual": {
                                        "PM25": [4002.621500211796271]
                                    },
                                    "smoldering": {
                                        "PM25": [623.424985839975172]
                                    }
                                }
                            }
                        ],
                        "start": "2015-11-24T17:00:00",
                        "end": "2015-11-25T17:00:00",
                        "pct": 100.0
                    }
                ]
            }
        ],
        "config": {
            "dispersion": {
                "start": "2015-11-25T00:00:00",
                "num_hours": 24
            },
            "export": {
                "extra_exports": [
                    "dispersion",
                    "visualization"
                ]
            }
        }
    }' | python -m json.tool

The fact that the emissions data is in an array is because the consumption
module (more specifically, the underlying 'consume' module) outputs arrays.
The length of each array equals the number of fuelbeds passed into consume.
Since consume is called on each fuelbed separately, the arrays of consumption
and emissions data will all be of length 1.

Note that the growth start and end timestamps are local time, whereas the
dispersion start time is in UTC.

### POST /api/v1/run/all/<met_domain>/

This API is very similar to the met-dependent dispersion API,
described above, except that it starts off with the
'ingestion' module rather than with 'findmetdata', and so doesn't
require emissions data.

#### Example

    $ curl "http://$BLUESKY_API_HOSTNAME/api/v1/run/all/DRI2km/" -H 'Content-Type: application/json' -d '
    {
        "config": {
            "emissions": {
                "species": [
                    "PM25"
                ]
            },
            "dispersion": {
                "num_hours": 24,
                "start": "2015-11-25T00:00:00"
            },
            "export": {
                "extra_exports": [
                    "dispersion",
                    "visualization"
                ]
            }
        },
        "fire_information": [
            {
                "event_of": {
                    "id": "SF11E826544",
                    "name": "Natural Fire near Yosemite, CA"
                },
                "growth": [
                    {
                        "start": "2015-11-24T17:00:00",
                        "end": "2015-11-25T17:00:00",
                        "pct": 100.0,
                        "location": {
                            "area": 10000,
                            "ecoregion": "western",
                            "latitude": 37.909644,
                            "longitude": -119.7615805,
                            "utc_offset": "-07:00"
                        }
                    }
                ],
                "id": "SF11C14225236095807750",
                "type": "wildfire"
            }
        ]
    }' | python -m json.tool

### POST /api/v1/run/dispersion/

Like the met-dependent API described above, this API takes emissions
data and runs bluesky through dispersion and
visualization.  This API, however, is to be used for dispersion
models not requiring met data (e.g. vsmoke, which currently is the
only such model supported).

Again, this API requires posted JSON with three
possible top level keys - 'fire_information', 'config', and 'modules'.
The 'fire_information' key is required, and must contain emissions data,
consumption data, growth time windows, and vsmoke meta fields (wind
speed and wind direction) for each fire. The 'config' key is also
required, to specify, at the very least, dispersion start time
and num_hours. The 'modules' key is optional.

Since dispersion is run, bluesky will be run asynchronously, and the
API response will include a guid to identify the run in subsequent
status and output API requests (described below).

    {
        run_id: <guid>
    }

#### Example

Unlike the hysplit request, above, this API requires both emissions
and consumption data.

    $ curl "http://$BLUESKY_API_HOSTNAME/api/v1/run/dispersion/" -H 'Content-Type: application/json' -d '
    {
        "fire_information": [
            {
                "meta": {
                    "vsmoke": {
                        "wd": 232,
                        "ws": 12
                    }
                },
                "event_of": {
                    "id": "SF11E826544",
                    "name": "Natural Fire near Yosemite, CA"
                },
                "id": "SF11C14225236095807750",
                "type": "wildfire",
                "growth": [
                    {
                        "location": {
                            "area": 10000,
                            "ecoregion": "western",
                            "latitude": 37.909644,
                            "longitude": -119.7615805,
                            "utc_offset": "-07:00"
                        },
                        "fuelbeds": [
                            {
                                "fccs_id": "49",
                                "pct": 50.0,
                                "heat": {
                                    "total": [
                                        3901187352927.508
                                    ],
                                    "residual": [
                                        1312164844326.5745
                                    ],
                                    "flaming": [
                                        1395852418045.9065
                                    ],
                                    "smoldering": [
                                        1193170090555.0266
                                    ]
                                },
                                "consumption": {
                                    "smoldering": [21712.600892425173],
                                    "flaming": [40988.711969791053],
                                    "residual": [13823.389194227209]
                                },
                                "emissions": {
                                    "flaming": {
                                        "PM25": [3000.3815120047017005]
                                    },
                                    "residual": {
                                        "PM25": [4200.621500211796271]
                                    },
                                    "smoldering": {
                                        "PM25": [634.424985839975172]
                                    }
                                }
                            }
                        ],
                        "start": "2015-11-24T17:00:00",
                        "end": "2015-11-25T17:00:00",
                        "pct": 100.0
                    }
                ]
            }
        ],
        "config": {
            "dispersion": {
                "start": "2015-11-25T00:00:00",
                "num_hours": 24,
                "model": "vsmoke"
            },
            "export": {
                "extra_exports": [
                    "dispersion"
                ]
            }
        }
    }' | python -m json.tool

As mentioned earlier, the fact that the emissions data is in an array
is because the consumption module (more specifically, the underlying
'consume' module) outputs arrays. The consumption data in this example is
much simpler than what would be produced by bluesky (which breaks out
consumption into a hierarchy of fuel categories), but is sufficient
for vsmoke.  The consumption data just needs to be categorized by
categorized by phase (flaming, residual, smoldering) at the inner-most
level.

Note that the growth start and end timestamps are local time, whereas the
dispersion start time is in UTC.

Also note that 'visualization' is not included in 'extra_exports', since
the vsmoke dispersion model includes kml generation.

### POST /api/v1/run/all/

This API is very similar to met-independent dispersion API, except that
it starts off with the
'ingestion' module rather than with 'findmetdata', and so doesn't require
consumption and emissions data.

#### Example

    $ curl "http://$BLUESKY_API_HOSTNAME/api/v1/run/all/" -H 'Content-Type: application/json' -d '
    {
        "config": {
            "emissions": {
                "species": [
                    "PM25"
                ]
            },
            "dispersion": {
                "num_hours": 24,
                "start": "2015-11-25T00:00:00",
                "model": "vsmoke"
            },
            "export": {
                "extra_exports": [
                    "dispersion"
                ]
            }
        },
        "fire_information": [
            {
                "meta": {
                    "vsmoke": {
                        "wd": 232,
                        "ws": 12
                    }
                },
                "event_of": {
                    "id": "SF11E826544",
                    "name": "Natural Fire near Yosemite, CA"
                },
                "growth": [
                    {
                        "start": "2015-11-24T17:00:00",
                        "end": "2015-11-25T17:00:00",
                        "pct": 100.0,
                        "location": {
                            "area": 10000,
                            "ecoregion": "western",
                            "latitude": 37.909644,
                            "longitude": -119.7615805,
                            "utc_offset": "-07:00"
                        }
                    }
                ],
                "id": "SF11C14225236095807750",
                "type": "wildfire"
            }
        ]
    }' | python -m json.tool

### GET /api/v1/run/<guid>/status

This API returns the status of a specific dispersion run

#### Request

 - url: http://$BLUESKY_API_HOSTNAME/api/v1/run/<guid>/status
 - method: GET

#### Response

    {
        "complete": <boolean>,
        "percent": <double>, /* (if available) */
        "status": <string>  /* ('Success', 'Failure', or 'Unknown') */
    }

#### Example:

    $ curl "http://$BLUESKY_API_HOSTNAME/api/v1/run/abc123/status"

    {
        "complete": false,
        "percent": 62.3,
        "status": "Unknown"
    }

or

    {
        "complete": true,
        "percent": 100.0,
        "status": "Success"
    }

### GET /api/v1/run/<guid>/output

This API returns the output location for a specific run

#### Request

 - url: http://$BLUESKY_API_HOSTNAME/api/v1/run/<guid>/output
 - method: GET

#### Response

    ... ADD SPEC ...

#### Example:

    $ curl "http://$BLUESKY_API_HOSTNAME/api/v1/run/abc123/output"

There are currently two ways the visualization images will be specified in
the results json object.  It depends on how you configured your run.  If you
set 'image_results_version=v2' in the original post request, you'll get
something like the following:

    {
        "images": {
            "daily_average": {
                "RedColorBar": {
                    "directory": "dispersion-visualization/images/daily_average/RedColorBar",
                    "legend": "colorbar_daily_average.png",
                    "other_images": [],
                    "series": [
                        "daily_average_20140530.png"
                    ]
                }
            },
            "daily_maximum": {
                "RedColorBar": {
                    "directory": "dispersion-visualization/images/daily_maximum/RedColorBar",
                    "legend": "colorbar_daily_maximum.png",
                    "other_images": [],
                    "series": [
                        "daily_maximum_20140530.png"
                    ]
                }
            },
            "hourly": {
                "RedColorBar": {
                    "directory": "dispersion-visualization/images/hourly/RedColorBar",
                    "legend": "colorbar_hourly.png",
                    "other_images": [],
                    "series": [
                        "hourly_201405300000.png",
                        ...,
                        "hourly_201405302300.png"
                    ]
                }
            },
            "three_hour": {
                "RedColorBar": {
                    "directory": "dispersion-visualization/images/three_hour/RedColorBar",
                    "legend": "colorbar_three_hour.png",
                    "other_images": [],
                    "series": [
                        "three_hour_201405300100.png",
                        ...,
                        "three_hour_201405302200.png"
                    ]
                }
            }
        },
        "kmzs": {
            "fire": "dispersion-visualization/fire_information.kmz",
            "smoke": "dispersion-visualization/smoke_dispersion.kmz"
        },
        "netCDF": "dispersion-visualization/hysplit_conc.nc",
        "root_url": "http://localhost:8888/playground-output/abc123"
    }

Otherwise, if you set 'image_results_version=v1' or if you didn't set it at all,
you'll get something like the following:

    {
        "images": {
            "daily": {
                "average": [
                    "dispersion-visualization/images/daily_average/RedColorBar/daily_average_20140530.png"
                ],
                "maximum": [
                    "dispersion-visualization/images/daily_maximum/RedColorBar/daily_maximum_20140530.png"
                ]
            },
            "hourly": [
                "dispersion-visualization/images/hourly/RedColorBar/hourly_201405300000.png",
                ...,
                "dispersion-visualization/images/hourly/RedColorBar/hourly_201405302300.png"
            ]
        },
        "kmzs": {
            "fire": "dispersion-visualization/fire_information.kmz",
            "smoke": "dispersion-visualization/smoke_dispersion.kmz"
        },
        "netCDF": "dispersion-visualization/hysplit_conc.nc",
        "root_url": "http://localhost:8888/playground-output/812ee94a-cb78-11e5-9d7c-0242ac110003-image-format-v1"
    }
