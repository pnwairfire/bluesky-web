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

The fact that the consumption and emissions data are in arrays is
because the consumption module (more specifically, the underlying
'consume' module) outputs arrays. The length of each array equals the
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
