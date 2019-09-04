## Plumerise

This API runs bluesky timeprofile and plumerise modules.  (The
bluesky web service runs FEPS plumerise which, unlike SEV plumerise,
requires timeprofile data.)

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v1/run/plumerise/<archive_type>/" \
 - method: POST
 - post data:

    {
        "fire_information": [ ... ],
        "config": { ... },
        "modules": [ ... ]
    }

Like the fuelbeds and emissions APIS, the plumerise API requires
posted JSON with three possible top level keys -
'fire_information', and 'config', and 'modules'. The
'fire_information' key is required, and it lists the one or
more fires to process. The 'config' key is
optional, and it specifies configuration data and other control
parameters.  The 'modules' key is also optional, and is used to
specify a subset of the modules normally run by this API.

See [BlueSky Pipeline](https://github.com/pnwairfire/bluesky/blob/v2.7.2/README.md)
for more information about required and optional post data

### Response

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
                        "consumption": {
                            "summary": {
                                "smoldering": 21712.600892425173,
                                "flaming": 40988.711969791053,
                                "residual": 13823.389194227209
                            }
                        },
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

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/run/plumerise/ca-nv_6-km/" \
        -H 'Content-Type: application/json' \
        -d @dev/data/plumerise-input.json | python -m json.tool





## Dispersion (HYSPLIT)

This API takes consumption, emissions, and plumerise data and runs
bluesky through dispersion and visualization.  It's the dispersion
API to be used for met-dependent dispersion models (e.g. hysplit,
which is currently the only such model supported).

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v1/run/dispersion/<archive_type>/" \
 - method: POST
 - post data:

    {
        "fire_information": [ ... ],
        "config": { ... },
        "modules": [ ... ]
    }

Like with the plumerise API, this API requires posted JSON with three
possible top level keys - 'fire_information', 'config', and 'modules.
The 'fire_information' key is required, and must contain
growth time windows with consumption, emissions, and plumerise data
for each fire. The 'config' key is also
required, to specify, at the very least, dispersion start time
and num_hours.  The 'modules' key is optional.

See [BlueSky Pipeline](https://github.com/pnwairfire/bluesky/blob/v2.7.2/README.md)
for more information about required and optional post data

### Response

Bluesky will be run asynchronously, and the
API response will include a guid to identify the run in subsequent
status and output API requests (described below).

    {
        run_id: <guid>
    }

### Examples

The following is a simple example that runs dispersion for only
one hour.

    $ echo '{
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
                        "timeprofile": {
                            "2014-05-29T17:00:00": {
                                "area_fraction": 0.42643923240938175,
                                "flaming": 0.42643923240938175,
                                "residual": 0.42643923240938175,
                                "smoldering": 0.42643923240938175
                            }
                        },
                        "plumerise": {
                            "2014-05-29T17:00:00": {
                                "emission_fractions": [
                                    0.05, 0.05, 0.05, 0.05, 0.05,
                                    0.05, 0.05, 0.05, 0.05, 0.05,
                                    0.05, 0.05, 0.05, 0.05, 0.05,
                                    0.05, 0.05, 0.05, 0.05, 0.05
                                ],
                                "heights": [
                                    3999.906231,
                                    18808.46359175,
                                    33617.0209525,
                                    48425.57831325001,
                                    63234.135674000005,
                                    78042.69303475,
                                    92851.25039550001,
                                    107659.80775625001,
                                    122468.36511700001,
                                    137276.92247775002,
                                    152085.4798385,
                                    166894.03719925001,
                                    181702.59456000003,
                                    196511.15192075,
                                    211319.70928150002,
                                    226128.26664225,
                                    240936.82400300002,
                                    255745.38136375003,
                                    270553.9387245,
                                    285362.49608525,
                                    300171.053446
                                ],
                                "smolder_fraction": 0.05
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

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/run/dispersion/ca-nv_6-km/" \
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

If you don't specify any hysplit configuration beyond dispersion 'start'
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
                    "VERTICAL_LEVELS": [100, 500, 1000],
                    "INITD": 0,
                    "NINIT": 0,
                    "DELT": 0.0,
                    "KHMAX": 72
                }
            },
            "visualization": {
                "hysplit": {
                    "blueskykml_config": {
                        "DispersionGridInput": {
                            "LAYERS": [0, 1, 2]
                        },
                        "DispersionImages": {
                            "DAILY_IMAGES_UTC_OFFSETS": [-7, 0]
                        }
                    }
                }
            }
        }
    }' > dev/data/dispersion-hysplit-input.json

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/run/dispersion/ca-nv_6-km/" \
        -H 'Content-Type: application/json' \
        -d @dev/data/dispersion-hysplit-input.json | python -m json.tool

### Extra hysplit options

In addition to setting hysplit's internal configuration parameters,
there are some meta options that are used to configure hysplit.  The
following lists the options, their possible values, and how they affect
the hysplit configuration

#### dispersion_speed

Possible values, and how they affect the config:

- 'faster'
    - default grid resolution multiplied by 1.5
    - NUMPAR = 1000
- 'balanced'
    - default grid resolution multiplied by 1.0
    - NUMPAR = 2000
- 'slower'
    - default grid resolution multiplied by 0.5
    - NUMPAR = 3000

#### number_of_particles

- 'low'
    - NUMPAR = 1000
- 'medium'
    - NUMPAR = 2000
- 'high'
    - NUMPAR = 3000

#### grid_resolution

- 'low'
    - default grid resolution multiplied by 1.5
- 'medium'
    - default grid resolution multiplied by 1.0
- 'high'
    - default grid resolution multiplied by 0.5

#### grid_size

Grid size can be any value greater than 0.0 and less than or
equal to 1.0.  If less that 1.0, the default dispersion grid
for the met archive is reduced in size accordingly.  The reduced
grid is centered around the fire as much as possible without spilling
outside of the default met.

Note that grid_size is only supported for requests containing a single
fire at a single lat/lng (e.g. not fires with multiple growth windows
at different locations, and not fires with location defined as
a polygon).

### Conflicting options:

Note the following restrictions:

-   'NUMPAR' can not be specified along with
    'dispersion_speed' or 'number_of_particles'.
-   User defined grid configuration (i.e. 'grid', 'USER_DEFINED_GRID' or
    'compute_grid' in the hysplit config) can not be specified
    along with 'dispersion_speed' or 'grid_resolution'.
-   'dispersion_speed' can't be specified along with either
    'grid_resolution' or 'number_of_particles'.
-   You can't specify more than one user-defined grid configuration
    (i.e. 'grid', 'USER_DEFINED_GRID', or 'compute_grid').





## Fuelbeds + Emissions + Plumerise + Dispersion (HYSPLIT)

This API is very similar to the met-dependent dispersion API,
described above, except that it starts off with the
'ingestion' module rather than with 'findmetdata', and so doesn't
require emissions data.

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v1/run/all/<archive_type>/" \
 - method: POST
 - post data:

    {
        "fire_information": [ ... ],
        "config": { ... },
        "modules": [ ... ]
    }

See hysplit dispersion API, above, as well as
[BlueSky Pipeline](https://github.com/pnwairfire/bluesky/blob/v2.7.2/README.md)
for more information about required and optional post data

### Response

Bluesky will be run asynchronously, and the
API response will include a guid to identify the run in subsequent
status and output API requests (described below).

    {
        run_id: <guid>
    }

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

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/run/all/ca-nv_6-km/" \
        -H 'Content-Type: application/json' \
        -d @dev/data/all-input.json | python -m json.tool





## Dispersion (VSMOKE)

Like the met-dependent API described above, this API takes emissions
and plumerise data and runs bluesky through dispersion and
visualization.  This API, however, is to be used for dispersion
models not requiring met data (e.g. vsmoke, which currently is the
only such model supported).


### Request

 - url: $BLUESKY_API_ROOT_URL/api/v1/run/dispersion/" \
 - method: POST
 - post data:

    {
        "fire_information": [ ... ],
        "config": { ... },
        "modules": [ ... ]
    }

Again, this API requires posted JSON with three
possible top level keys - 'fire_information', 'config', and 'modules'.
The 'fire_information' key is required, and must contain emissions data,
consumption data, growth time windows, and vsmoke meta fields (wind
speed and wind direction) for each fire. The 'config' key is also
required, to specify, at the very least, dispersion start time
and num_hours. The 'modules' key is optional.

See [BlueSky Pipeline](https://github.com/pnwairfire/bluesky/blob/v2.7.2/README.md)
for more information about required and optional post data

### Response

Bluesky will be run asynchronously, and the
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
                        ],
                        "timeprofile": {
                            "2014-05-29T17:00:00": {
                                "area_fraction": 0.42643923240938175,
                                "flaming": 0.42643923240938175,
                                "residual": 0.42643923240938175,
                                "smoldering": 0.42643923240938175
                            }
                        }
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




## Fuelbeds + Emissions + Plumerise + Dispersion (VSMOKE)

This API is very similar to met-independent dispersion API, except that
it starts off with the
'ingestion' module rather than with 'findmetdata', and so doesn't require
consumption and emissions data.

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v1/run/all/" \
 - method: POST
 - post data:

    {
        "fire_information": [ ... ],
        "config": { ... },
        "modules": [ ... ]
    }

See VSMOKE dispersion API, above, as well as
[BlueSky Pipeline](https://github.com/pnwairfire/bluesky/blob/v2.7.2/README.md)
for more information about required and optional post data

### Response

Bluesky will be run asynchronously, and the
API response will include a guid to identify the run in subsequent
status and output API requests (described below).

    {
        run_id: <guid>
    }

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
                "start": "2014-05-30T00:00:00",
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
