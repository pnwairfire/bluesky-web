# BlueSky Web APIs





## GET /api/v1/domains/

This API returns information about all domains with ARL data

### Request

 - url: http://$BLUESKY_API_HOSTNAME/api/v1/domains/
 - method: GET

### Response

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

### Example

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





## GET /api/v1/domains/<domain_id>/

This API returns information about a specific domain with ARL data

### Request

 - url: http://$BLUESKY_API_HOSTNAME/api/v1/domains/<domain_id>/
 - method: GET

### Response

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

### Example

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





## GET /api/v1/domains/<domain_id>/available-dates/

This API returns the dates for which a specific d has ARL data

### Request

 - url: http://$BLUESKY_API_HOSTNAME/api/v1/domains/<domain_id>/available-dates
 - method: GET

### Response

    {
        "dates": [
           <date>,
           ...
        ]
    }


### Example

    $ curl "http://$BLUESKY_API_HOSTNAME/api/v1/domains/DRI2km/available-dates" | python -m json.tool

    {
        "dates": [
            "20151124",
            "20151123",
            "20151122"
        ]
    }






## GET /api/v1/available-dates/

This API returns the dates, by domain, for which there exist ARL data

### Request

 - url: http://$BLUESKY_API_HOSTNAME/api/v1/available-dates/
 - method: GET

### Response

    {
        "dates": [
            "<domain_id>": [
                <date>,
                ...
            ]
           ...
        ]
    }


### Example

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





## POST /api/v1/run/fuelbeds/

This API runs bluesky through ingestion and fuelbeds.
It requires posted JSON with three possible top level keys -
'fire_information', and 'config', and 'modules'. The
'fire_information' key is required, and it lists the one or
more fires to process. The 'config' key is
optional, and it specifies configuration data and other control
parameters.  The 'modules' is also optional, and is used to
specify a subset of the modules normally run by this API.

### Request

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

### Response

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

### Examples

An example with fire location data specified as a geojson

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
                            "geojson": {
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





## POST /api/v1/run/emissions/

This API runs bluesky through consumption and emissions.
It requires posted JSON with three possible top level keys -
'fire_information', and 'config', and 'modules'. The
'fire_information' key is required, and it lists the one or
more fires to process. The 'config' key is
optional, and it specifies configuration data and other control
parameters.  The 'modules' key is also optional, and is used to
specify a subset of the modules normally run by this API.

### Request

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

### Response

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

### Examples

An example with fire location data specified as geojson

    $ curl "http://$BLUESKY_API_HOSTNAME/api/v1/run/emissions/" -H 'Content-Type: application/json' -d '
    {
        "fire_information": [
            {
                "id": "SF11C14225236095807750",
                "event_id": "SF11E826544",
                "name": "Natural Fire near Snoqualmie Pass, WA",
                "location": {
                    "geojson": {
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





## POST /api/v1/run/plumerise/<met_domain>/

docker run --rm \
    -v $HOME/code/pnwairfire-bluesky/:/bluesky/ \
    -v $HOME/DRI_6km/:/DRI_6km/ bluesky bsp -i /bluesky/test/data/json/1-fire-24hr-20140530-CA-post-ingestion.json -c /bluesky/test/config/findmetdata/findmetdata-input-DRI6km-w-timewindow.json -C plumerising.model=sev -C fuelbeds.foo=bar ingestion  findmetdata localmet plumerising|python -m json.tool |grep -A5 'plumerise":'

This API runs bluesky localmet and plumerise modules.  (The bluesky
web serives runs SEV plumerise which, unlike FEPS plumerise, requires
localmet data.)

Like the fuelbeds and emissions APIS, the plumerise API requires
posted JSON with three possible top level keys -
'fire_information', and 'config', and 'modules'. The
'fire_information' key is required, and it lists the one or
more fires to process. The 'config' key is
optional, and it specifies configuration data and other control
parameters.  The 'modules' key is also optional, and is used to
specify a subset of the modules normally run by this API.

Since plumerise requires met data that may not exist on the web
server, bluesky will be run asynchronously, and the
API response will include a guid to identify the run in subsequent
status and output API requests (described below).

    {
        run_id: <guid>
    }

### Examples

An example with fire location data specified as geojson

    $ curl "http://$BLUESKY_API_HOSTNAME/api/v1/run/plumerise/DRI2km/" -H 'Content-Type: application/json' -d '
    {
        "fire_information": [
            {
                "id": "SF11C14225236095807750",
                "event_id": "SF11E826544",
                "name": "Natural Fire near Snoqualmie Pass, WA",
                "location": {
                    "geojson": {
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
                }
            }
        ]
    }' | python -m json.tool





## POST /api/v1/run/dispersion/<met_domain>/

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

Bluesky will be run asynchronously, and the
API response will include a guid to identify the run in subsequent
status and output API requests (described below).

    {
        run_id: <guid>
    }

### Examples

Since this API requires emissions data, consumption data is not required,
and so has been optionally stripped from the following requests

#### Localmet and plumerise already run

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
                        "start": "2015-11-24T17:00:00",
                        "end": "2015-11-25T17:00:00",
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
                        "localmet": {
                            ...
                        },
                        "plumerise": {
                            ...
                        }
                    }
                ]
            }
        ],
        "config": {
            "dispersion": {
                "start": "2015-11-25T00:00:00",
                "num_hours": 24
            }
        }
        "met": {
            "files": [
                {
                    "file": "/DRI_2km/2015112500/wrfout_d2.2015112500.f00-11_12hr01.arl",
                    "first_hour": "2015-11-25T00:00:00",
                    "last_hour": "2015-11-25T11:00:00"
                },
                {
                    "file": "/DRI_2km/2015112500/wrfout_d2.2015112512.f00-11_12hr01.arl",
                    "first_hour": "2015-11-25T12:00:00",
                    "last_hour": "2015-11-25T23:00:00"
                }
            ]
        },

    }' | python -m json.tool

The fact that the emissions data is in an array is because the
consumption module (more specifically, the underlying 'consume'
module) outputs arrays. The length of each array equals the
number of fuelbeds passed into consume. Since consume is called
on each fuelbed separately, the arrays of consumption
and emissions data will all be of length 1.

Note that the growth start and end timestamps are local time, whereas the
dispersion start time is in UTC.



#### Localmet and plumerise not yet run

NOTE: passing data in without plumerise and localmet data may
not be supported. It's TBD

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
            }
        }
    }' | python -m json.tool





## POST /api/v1/run/all/<met_domain>/

This API is very similar to the met-dependent dispersion API,
described above, except that it starts off with the
'ingestion' module rather than with 'findmetdata', and so doesn't
require emissions data.

### Example

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





## POST /api/v1/run/dispersion/

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

### Example

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




## POST /api/v1/run/all/

This API is very similar to met-independent dispersion API, except that
it starts off with the
'ingestion' module rather than with 'findmetdata', and so doesn't require
consumption and emissions data.

### Example

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





## GET /api/v1/run/<guid>/status

This API returns the status of a specific dispersion run

### Request

 - url: http://$BLUESKY_API_HOSTNAME/api/v1/run/<guid>/status
 - method: GET

### Response

    {
        "complete": <boolean>,
        "percent": <double>, /* (if available) */
        "status": <string>  /* ('Success', 'Failure', or 'Unknown') */
    }

### Example:

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





## GET /api/v1/run/<guid>/output

This API returns the output location for a specific run

### Request

 - url: http://$BLUESKY_API_HOSTNAME/api/v1/run/<guid>/output
 - method: GET

### Response

    ... ADD SPEC ...

### Examples:

#### Plumerise run output

    $ curl "http://$BLUESKY_API_HOSTNAME/api/v1/run/abc123/output"

    {
        "fire_information": [
            {
                "type": "wildfire",
                "fuel_type": "natural",
                "growth": [
                    {
                        "end": "2014-05-30T17:00:00",
                        "start": "2014-05-29T17:00:00",
                        "localmet": {
                            ...
                        },
                        "plumerise": {
                            ...
                        },
                        "location": {
                            "longitude": -119.7615805,
                            "utc_offset": "-07:00",
                            "area": 10000,
                            "latitude": 37.909644,
                            "ecoregion": "western"
                        }
                    }
                ],
                "id": "SF11C14225236095807750"
            }
        ],
        "met": {
            "files": [
                ...
            ]
        },
        "today": "2017-07-13",
        "config": {
            "plumerising": {
                "model": "sev"
            },
            "findmetdata": {
                "time_window": {
                    "last_hour": "...",
                    "first_hour": "..."
                },
                "arl": {
                    "index_filename_pattern": "arl12hrindex.csv"
                },
                "met_format": "arl",
                "met_root_dir": "/DRI_6km/"
            }
        },
        "counts": {
            "fires": 1
        },
        "run_id": "7b0ad162-67f0-11e7-8754-0242ac110002",
        "processing": [
            {
                "module_name": "findmetdata",
                "module": "bluesky.modules.findmetdata",
                "version": "0.1.0"
            },
            {
                "module_name": "localmet",
                "module": "bluesky.modules.localmet",
                "version": "0.1.0"
            },
            {
                "module_name": "plumerising",
                "module": "bluesky.modules.plumerising",
                "version": "0.1.1",
                "model": "sev",
                "plumerise_version": "1.0.0"
            }
        ],
        "runtime": {
            "total": "0.0011111111111111111h 0.06666666666666667m 4s",
            "modules": [
                {
                    "module_name": "findmetdata",
                    "total": "0.0h 0.0m 0s",
                    "end": "2017-07-13T17:27:01Z",
                    "start": "2017-07-13T17:27:01Z"
                },
                {
                    "module_name": "localmet",
                    "total": "0.0011111111111111111h 0.06666666666666667m 4s",
                    "end": "2017-07-13T17:27:05Z",
                    "start": "2017-07-13T17:27:01Z"
                },
                {
                    "module_name": "plumerising",
                    "total": "0.0h 0.0m 0s",
                    "end": "2017-07-13T17:27:05Z",
                    "start": "2017-07-13T17:27:05Z"
                }
            ],
            "end": "2017-07-13T17:27:05Z",
            "start": "2017-07-13T17:27:01Z"
        }
    }



#### Dispersion run output

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
