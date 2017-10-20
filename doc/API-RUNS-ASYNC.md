## POST /api/v1/run/plumerise/<met_domain>/

This API runs bluesky timeprofiling and plumerise modules.  (The
bluesky web service runs FEPS plumerise which, unlike SEV plumerise,
requires timeprofiling data.)

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

There are currently two ways the visualization images can be
listed in the output to be retrieved later (see output API spec
below), but you need to specify which way when initializing
the dispersion run. Set 'image_results_version' to 'v1' or 'v2', or
don't set it at all to get 'v1'. The output API spec, below,
lists the two output formats.

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
                            "summary": {
                                "total": 3901187352927.508,
                                "residual": 1312164844326.5745,
                                "flaming": 1395852418045.9065,
                                "smoldering": 1193170090555.0266
                            }
                        },
                        "consumption": {
                            "summary": {
                                "smoldering": 21712.600892425173,
                                "flaming": 40988.711969791053,
                                "residual": 13823.389194227209
                            }
                        },
                        "fuelbeds": [
                            {
                                "fccs_id": "49",
                                "pct": 50.0,
                                "emissions": {
                                    "flaming": {
                                        "PM2.5": [3002.3815120047017005]
                                    },
                                    "residual": {
                                        "PM2.5": [4002.621500211796271]
                                    },
                                    "smoldering": {
                                        "PM2.5": [623.424985839975172]
                                    }
                                }
                            }
                        ],
                        "plumerise": {
                            "2014-05-29T23:00:00": {
                                "heights": [
                                    33.01197995675946,
                                    34.662578954597436,
                                    36.31317795243541,
                                    37.963776950273385,
                                    39.61437594811135,
                                    41.26497494594933,
                                    42.9155739437873,
                                    44.566172941625275,
                                    46.21677193946324,
                                    47.86737093730122,
                                    49.51796993513919,
                                    51.168568932977166,
                                    52.81916793081514,
                                    54.469766928653115,
                                    56.12036592649109,
                                    57.77096492432906,
                                    59.42156392216703,
                                    61.072162920005006,
                                    62.72276191784297,
                                    64.37336091568095,
                                    66.02395991351892
                                ],
                                "emission_fractions": [
                                    0.05, 0.05, 0.05, 0.05, 0.05,
                                    0.05, 0.05, 0.05, 0.05, 0.05,
                                    0.05, 0.05, 0.05, 0.05, 0.05,
                                    0.05, 0.05, 0.05, 0.05, 0.05
                                ],
                                "smolder_fraction": 0.0
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

The fact that the consumption and emissions data are in arrays is
because the consumption module (more specifically, the underlying
'consume' module) outputs arrays. The length of each array equals the
number of fuelbeds passed into consume. Since consume is called
on each fuelbed separately, the arrays of consumption
and emissions data will all be of length 1.

Note that the growth start and end timestamps are local time, whereas the
dispersion start time is in UTC.


### Extra hysplit parameters

If you don't specify any dispersion configuration beyond 'start'
and 'num_hours', hysplit will be configured with a set of default
parameters, and will be run over the entire met domain.  You may,
however, override any of these.  For example:


    $  echo '{
        "fire_information": [
            .... same as previous example ....
        ],
        "config": {
            "dispersion": {
                "start": "2014-05-30T00:00:00",
                "num_hours": 1,
                "hysplit": {
                    "grid": {
                        "spacing": 6.0,
                        "boundary": {
                            "ne": {
                                "lat": 40.0,
                                "lng": -115.0
                            },
                            "sw": {
                                "lat": 35.00,
                                "lng": -125.0
                            }
                        }
                    },
                    "NUMPAR": 3000,
                    "MAXPAR": 1000000000,
                    "VERTICAL_EMISLEVELS_REDUCTION_FACTOR": 10,
                    "VERTICAL_LEVELS": [100],
                    "INITD": 0,
                    "NINIT": 0,
                    "DELT": 0.0,
                    "KHMAX": 72
                }
            }
        }
    }' > dev/data/dispersion-hysplit-input.json

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/run/dispersion/DRI6km/" \
        -H 'Content-Type: application/json' \
        -d @dev/data/dispersion-hysplit-input.json | python -m json.tool





## POST /api/v1/run/all/<met_domain>/

This API is very similar to the met-dependent dispersion API,
described above, except that it starts off with the
'ingestion' module rather than with 'findmetdata', and so doesn't
require emissions data.

### Example

    $ echo '{
        "config": {
            "emissions": {
                "species": [
                    "PM2.5"
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
    }' > dev/data/all-input.json

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/run/all/DRI6km/" \
        -H 'Content-Type: application/json' \
        -d @dev/data/all-input.json | python -m json.tool





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

    $ echo '{
        "fire_information": [
            {
                "meta": {
                    "vsmoke": {
                        "wd": 232,
                        "ws": 12
                    }
                },
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
                            "summary": {
                                "total": 3901187352927.508,
                                "residual": 1312164844326.5745,
                                "flaming": 1395852418045.9065,
                                "smoldering": 1193170090555.0266
                            }
                        },
                        "consumption": {
                            "summary": {
                                "smoldering": 21712.600892425173,
                                "flaming": 40988.711969791053,
                                "residual": 13823.389194227209
                            }
                        },
                        "fuelbeds": [
                            {
                                "fccs_id": "49",
                                "pct": 50.0,
                                "emissions": {
                                    "flaming": {
                                        "PM2.5": [3000.3815120047017005]
                                    },
                                    "residual": {
                                        "PM2.5": [4200.621500211796271]
                                    },
                                    "smoldering": {
                                        "PM2.5": [634.424985839975172]
                                    }
                                }
                            }
                        ]
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
    }'  > dev/data/dispersion-vsmoke-input.json

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/run/dispersion/" \
        -H 'Content-Type: application/json' \
        -d @dev/data/dispersion-vsmoke-input.json | python -m json.tool

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
                    "PM2.5"
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
