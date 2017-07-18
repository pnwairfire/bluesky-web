# BlueSky Web APIs

In the request urls listed below, $BLUESKY_API_ROOT_URL would be
something like 'http://localhost:8887' in development or
'https://www.blueskywebhost.com/bluesky' in production





## GET /api/v1/domains/

This API returns information about all domains with ARL data

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v1/domains/
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
                    "height_latitude": <degrees>,
                    "spacing_latitude": <km>,
                    "spacing_longitude": <km>,
                    "projection": "..."
                },
                <other_domain_data?>: <data>,
                ...
            },
            ...
        }
    }

### Example

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/domains/" | python -m json.tool
    {
         "domains": {
            "DRI2km": {
                "boundary": {
                    "center_latitude": 36.6706,
                    "center_longitude": -117.80515,
                    "height_latitude": 15.8494,
                    "width_longitude": 21.3125,
                    "spacing_latitude": 2.0,
                    "spacing_longitude": 2.0,
                    "projection": "LCC"
                },
                "dates": [
                    "2014-05-29",
                    "2014-05-30",
                    "2014-05-31",
                    "2014-06-01"
                ]
            },
            "DRI6km": {
                "boundary": {
                    "center_latitude": 44.86545,
                    "center_longitude": -118.0294,
                    "width_longitude": 21.0766,
                    "height_latitude": 9.6333,
                    "spacing_latitude": 6.0,
                    "spacing_longitude": 6.0,
                    "projection": "LCC"
                },
                "dates": [
                    "2014-05-29",
                    "2014-05-30",
                    "2014-05-31",
                    "2014-06-01"
                ]
            },
            "NAM84": {
                "boundary": {
                    "center_latitude": 34.7595,
                    "center_longitude": -91.43835,
                    "width_longitude": 84.0433,
                    "height_latitude": 45.139,
                    "spacing_longitude": 0.15,
                    "spacing_latitude": 0.15,
                    "projection": "LatLon"
                },
                "dates": [
                    "2014-05-29",
                    "2014-05-30",
                    "2014-05-31",
                    "2014-06-01"
                ]
            }
        }
    }




## GET /api/v1/domains/<domain_id>/

This API returns information about a specific domain with ARL data

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v1/domains/<domain_id>/
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
                "height_latitude": <degrees>,
                "spacing_latitude": <km>,
                "spacing_longitude": <km>,
                "projection": "..."

            },
            <other_domain_data?>: <data>,
            ...
        }
    }

### Example

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/domains/DRI6km/" | python -m json.tool
    {
        "DRI6km": {
            "dates": [
                "2014-05-29",
                "2014-05-30",
                "2014-05-31",
                "2014-06-01"
            ],
            "boundary": {
                "center_longitude": -117.80515,
                "spacing_latitude": 6.0,
                "projection": "LCC",
                "height_latitude": 15.8494,
                "center_latitude": 36.6706,
                "spacing_longitude": 6.0,
                "width_longitude": 21.3125
            }
        }
    }




## GET /api/v1/domains/<domain_id>/available-dates/

This API returns the dates for which a specific d has ARL data

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v1/domains/<domain_id>/available-dates
 - method: GET

### Response

    {
        "dates": [
           <date>,
           ...
        ]
    }


### Example

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/domains/DRI6km/available-dates" | python -m json.tool
    {
        "dates": [
            "2014-05-29",
            "2014-05-30",
            "2014-05-31",
            "2014-06-01"
        ]
    }






## GET /api/v1/available-dates/

This API returns the dates, by domain, for which there exist ARL data

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v1/available-dates/
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

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/available-dates" | python -m json.tool
    {
        "dates": {
            "DRI2km": [
                "2014-05-29",
                "2014-05-30",
                "2014-05-31",
                "2014-06-01"
            ],
            "DRI6km": [
                "2014-05-29",
                "2014-05-30",
                "2014-05-31",
                "2014-06-01"
            ],
            "NAM84": [
                "2014-05-31",
                "2014-06-01"
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

 - url: $BLUESKY_API_ROOT_URL/api/v1/run/fuelbeds/
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

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/run/fuelbeds/" -H 'Content-Type: application/json' -d '
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

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/run/fuelbeds/" -H 'Content-Type: application/json' -d '
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
                ]
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

 - url: $BLUESKY_API_ROOT_URL/api/v1/run/emissions/
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

    $ echo '{
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
    }' > dev/data/emissions-input.json

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/run/emissions/" \
        -H 'Content-Type: application/json' \
        -d @dev/data/emissions-input.json | python -m json.tool | less


Another exmaple, this time running only the consumption
modules, and with fire location data specified as lat + lng + size.

    $ echo '{
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
    }' > dev/data/consumption-input.json

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/run/emissions/" \
        -H 'Content-Type: application/json' \
        -d @dev/data/consumption-input.json | python -m json.tool | less





## POST /api/v1/run/plumerise/<met_domain>/

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

    $ echo '{
        "fire_information": [
            {
                "growth": [
                    {
                        "start": "2014-05-29T17:00:00",
                        "end": "2014-05-30T17:00:00",
                        "location": {
                            "area": 10000,
                            "ecoregion": "western",
                            "latitude": 37.909644,
                            "longitude": -119.7615805,
                            "utc_offset": "-07:00"
                        }
                    }
                ]
            }
        ]
    }' > dev/data/plumerise-input.json

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/run/plumerise/DRI6km/" \
        -H 'Content-Type: application/json' \
        -d @dev/data/plumerise-input.json | python -m json.tool





## POST /api/v1/run/dispersion/<met_domain>/

This API takes consumption, emissions, and plumerise data and runs
bluesky through dispersion and visualization.  It's the dispersion
API to be used for met-dependent dispersion models (e.g. hysplit,
which is currently the only such model supported).

Like with the emissions API, This API requires posted JSON with three
possible top level keys - 'fire_information', 'config', and 'modules.
The 'fire_information' key is required, and must contain
growth time windows with consumption, emissions, and plumerise data
for each fire. The 'config' key is also
required, to specify, at the very least, dispersion start time
and num_hours.  The 'modules' key is optional.

Bluesky will be run asynchronously, and the
API response will include a guid to identify the run in subsequent
status and output API requests (described below).

    {
        run_id: <guid>
    }

### Examples

The following is a simple example that runs dispersion for only
one hour.

    $  echo '{
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
                        "start": "2014-05-29T17:00:00",
                        "end": "2014-05-30T17:00:00",
                        "location": {
                            "area": 10000,
                            "ecoregion": "western",
                            "latitude": 37.909644,
                            "longitude": -119.7615805,
                            "utc_offset": "-07:00"
                        },
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
                            "summary": {
                                "smoldering": [21712.600892425173],
                                "flaming": [40988.711969791053],
                                "residual": [13823.389194227209]
                            }
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
                        "plumerise": {
                            "2014-05-29T17:00:00": {
                                "percentile_015": 204.81921283270026,
                                "percentile_005": 187.008846499422,
                                "percentile_050": 267.15549499917427,
                                "percentile_025": 222.62957916597856,
                                "percentile_030": 231.5347623326177,
                                "percentile_070": 302.77622766573086,
                                "percentile_095": 347.3021434989265,
                                "percentile_085": 329.4917771656483,
                                "percentile_055": 276.06067816581344,
                                "percentile_060": 284.96586133245256,
                                "percentile_040": 249.34512866589597,
                                "percentile_045": 258.2503118325351,
                                "percentile_020": 213.7243959993394,
                                "percentile_090": 338.3969603322874,
                                "smolder_fraction": 0.0,
                                "percentile_075": 311.68141083237,
                                "percentile_065": 293.8710444990917,
                                "percentile_035": 240.43994549925685,
                                "percentile_000": 178.10366333278284,
                                "percentile_080": 320.5865939990091,
                                "percentile_100": 356.2073266655657,
                                "percentile_010": 195.91402966606114
                            }
                        }
                    }
                ]
            }
        ],
        "config": {
            "dispersion": {
                "start": "2014-05-30T00:00:00",
                "num_hours": 1
            }
        }
    }' > dev/data/dispersion-hysplit-input.json

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/run/dispersion/DRI6km/" \
        -H 'Content-Type: application/json' \
        -d @dev/data/dispersion-hysplit-input.json | python -m json.tool


The fact that the emissions data is in an array is because the
consumption module (more specifically, the underlying 'consume'
module) outputs arrays. The length of each array equals the
number of fuelbeds passed into consume. Since consume is called
on each fuelbed separately, the arrays of consumption
and emissions data will all be of length 1.

Note that the growth start and end timestamps are local time, whereas the
dispersion start time is in UTC.




## POST /api/v1/run/all/<met_domain>/

This API is very similar to the met-dependent dispersion API,
described above, except that it starts off with the
'ingestion' module rather than with 'findmetdata', and so doesn't
require emissions data.

### Example

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/run/all/DRI6km/" -H 'Content-Type: application/json' -d '
    {
        "config": {
            "emissions": {
                "species": [
                    "PM25"
                ]
            },
            "dispersion": {
                "num_hours": 24,
                "start": "2014-05-30T00:00:00"
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
                        "start": "2014-05-29T17:00:00",
                        "end": "2014-05-30T17:00:00",
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
and plumerise data and runs bluesky through dispersion and
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

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/run/dispersion/" -H 'Content-Type: application/json' -d '
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
                        "start": "2014-05-29T17:00:00",
                        "end": "2014-05-30T17:00:00",
                        "pct": 100.0
                    }
                ]
            }
        ],
        "config": {
            "dispersion": {
                "start": "2014-05-30T00:00:00",
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

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/run/all/" -H 'Content-Type: application/json' -d '
    {
        "config": {
            "emissions": {
                "species": [
                    "PM25"
                ]
            },
            "dispersion": {
                "num_hours": 24,
                "start": " 2014-05-30T00:00:00",
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
                        "start": "2014-05-29T17:00:00",
                        "end": "2014-05-30T17:00:00",
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





## GET /api/v1/runs/<guid>

This API returns the status of a specific dispersion run

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v1/runs/<guid> (/api/v1/run/<guid>/status is also supported for backwards compatibility)
 - method: GET

### Response

    {
        ....TODO: fill in...
    }

### Example:

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/runs/abc123"

    {
        ....TODO: fill in...
    }

or

    {
        ....TODO: fill in...
    }





## GET /api/v1/runs/<guid>/output

This API returns the output location for a specific run

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v1/runs/<guid>/output (/api/v1/run/<guid>/output is also supported for backwards compatibility)
 - method: GET

### Response

    ... ADD SPEC ...

### Examples:

#### Plumerise run output

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/runs/abc123/output"

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

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/runs/abc123/output"

There are currently two ways the visualization images will be
specified in the results json object.  If you specify
'image_results_version=v2' in the output request, you'll get
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




## GET /api/v1/runs/[<status>/]

This API returns meta information about runs

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v1/runs/[<status>/]
 - optional query args: limit, offset
 - method: GET

### Response


    {
        "runs": [
            {
                "enqueued": "<ts>",
                "modules": [
                    ...
                ],
                "status": "<status>",
                "queue": "<queue>",
                "run_id": "<run_id>",
                "server": "<hostname>",
                "dequeued": "<ts>",
                "started": "<ts>",
                "completed": "<ts>",
                ....
            },
            ...
        ]
    }


### Example


    $ curl "$BLUESKY_API_ROOT_URL/api/v1/runs/enqueued/?limit=2&offset=1" |python -m json.tool

    {
        "runs": [
            {
                "enqueued": "2017-07-14T19:17:17Z",
                "modules": [
                    "findmetdata",
                    "localmet",
                    "plumerising"
                ],
                "status": "enqueued",
                "queue": "dri",
                "run_id": "0d39dd48-68c9-11e7-9295-3c15c2c6639e"
            },
            {
                "enqueued": "2017-07-14T19:18:59Z",
                "modules": [
                    "findmetdata",
                    "localmet",
                    "plumerising"
                ],
                "status": "enqueued",
                "queue": "dri",
                "run_id": "49e42864-68c9-11e7-9f5f-3c15c2c6639e"
            }
        ]
    }
