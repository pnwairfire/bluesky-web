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
                            "2014-05-29T17:00:00": {
                                "TEMP": [18.9,18.0,17.1,15.9,14.4,12.8,11.0,9.4,7.1,4.0,0.34,-5.0,-11.8,-18.0,-23.8,-29.5,-35.1,-41.3,-48.0,-53.6,-57.0,-57.6,-57.0,-57.1,-58.5,-60.2,-61.2,-61.7,-61.8,-61.8,-61.2],
                                "RELH": [20.118608669639134,20.455560242267424,20.707708096204268,22.03241602522676,22.999619573138613,24.06106447989768,24.41728102957821,16.03683400197446,11.099793025043102,9.236240428993268,8.886336621064157,11.372462088617617,21.152632300624326,31.24327262763656,40.14354990264358,52.37954255073795,55.305642491056254,51.56344891488525,38.385086906506345,24.129373559853594,14.93578385517181,13.3344176585832,5.162987011664329,4.19664135432114,3.945912123639419,3.744828827069603,1.264857160782035,0.4795238439421066,0.16176666191454495,0.08897166405299972,0.09034694005585964],
                                "sunrise_hour": 6.0,
                                "SHGT": 1472.0,
                                "HPBL": 100.0,
                                "PBLH": 770.0,
                                "HGTS": [1359.3566495827665,1426.9898045331631,1524.4027918914464,1642.5578286940072,1802.2954601443178,1995.3622802185055,2234.2041165813416,2565.534551837579,2987.574123779814,3416.915748023283,3878.781296757666,4549.6073666928905,5432.7746075781115,6328.970662440699,7234.854726013943,8145.368040180117,9075.405854211265,10022.305476071488,10981.449306410641,11945.31079168034,12975.402503889687,14044.394573313946,15101.72267790848,16292.89241561934,17458.301486042972,18712.940611562906,20077.39600222122,21581.33380820919,23270.279977561968,25534.516727442915,28825.25346629527],
                                "PRSS": 852.0,
                                "TPP6": null,
                                "VWND": [1.1,1.4,1.5,1.7,2.2,2.7,3.6,5.4,5.4,4.7,4.3,5.9,8.8,11.8,13.6,14.3,15.1,17.1,19.3,19.5,17.9,16.0,14.7,13.2,11.7,9.8,9.7,10.4,9.8,8.0,5.7],
                                "WWND": [-57.0,-44.0,-17.3,8.8,8.2,0.0,-15.5,-28.9,-28.6,-14.4,-14.6,-15.8,-17.1,0.0,0.0,11.3,11.5,18.9,17.6,10.6,0.0,-5.5,-7.1,-5.5,-4.0,-1.6,0.24,-0.13,-0.93,-1.7,278.0],
                                "U10M": 3.9,
                                "pressure_at_surface": 0.0,
                                "dew_point": [-4.701260686930368,-5.238182820022018,-5.836130169464127,-6.026178810980127,-6.736434548425223,-7.514023090387241,-8.875396496680423,-15.603041893258137,-21.950586393736444,-26.559533401537493,-29.890467901995123,-31.448765921634873,-30.306448434913193,-31.46608789877405,-34.0154309054422,-36.49860426269589,-41.237377381247285,-47.79534678598489,-56.75535831782929,-65.74952140451904,-72.47745437920801,-73.84363597922572,-80.19557390774395,-81.71103522123744,-83.22872422606838,-84.90896912833261,-92.58411425355243,-96.70406899255195,-96.77368668652971,-96.77368668652971,-96.35614420062694],
                                "WDIR": [253.4,250.4,249.9,247.8,240.9,226.1,198.3,177.1,164.1,155.4,155.7,182.2,208.2,212.9,216.8,223.9,228.4,227.5,222.0,217.4,219.0,226.1,231.6,230.7,227.0,223.4,211.0,196.6,183.5,167.9,142.0],
                                "TPP3": null,
                                "WSPD": [3.8,4.2,4.4,4.4,4.4,3.9,3.8,5.4,5.7,5.2,4.8,5.9,9.9,13.9,16.9,19.6,22.5,25.1,25.8,24.4,22.9,22.8,23.3,20.6,17.0,13.3,11.2,10.8,9.8,8.2,7.3],
                                "pressure": [849.0,842.0,832.0,820.0,804.0,785.0,762.0,731.0,693.0,656.0,618.0,566.0,503.0,445.0,392.0,344.0,300.0,260.0,224.0,192.0,162.0,135.0,112.0,90.0,72.0,56.0,42.0,30.0,20.0,11.0,4.0],
                                "lng": -119.7615805,
                                "T02M": 19.9,
                                "TO2M": null,
                                "sunset_hour": -4.0,
                                "TPOT": [306.1,305.9,305.8,305.9,306.0,306.2,306.6,308.4,310.2,311.4,312.1,313.1,314.7,317.2,319.8,323.1,326.3,328.8,330.8,334.2,341.4,353.5,368.6,383.2,396.0,408.4,422.5,437.8,454.3,471.4,490.1],
                                "V10M": 2.4,
                                "UWND": [3.6,3.9,4.1,4.0,3.8,2.8,1.2,-0.33,-1.6,-2.2,-2.0,0.16,4.6,7.4,10.0,13.5,16.7,18.3,17.0,14.6,14.2,16.2,18.1,15.8,12.3,9.0,5.7,3.0,0.5,-1.8,-4.5],
                                "TPPA": 0.0,
                                "lat": 37.909644,
                                "SPHU": [3.2,3.1,3.0,3.0,2.9,2.8,2.6,1.6,1.0,0.71,0.56,0.53,0.66,0.67,0.6,0.54,0.39,0.23,0.1,0.04,0.02,0.02,0.01,0.01,0.01,0.01,0.004,0.002,0.001,0.001,0.003],
                                "PRES": [849.0,842.0,833.0,821.0,805.0,787.0,766.0,737.0,702.0,666.0,630.0,582.0,522.0,468.0,419.0,373.0,332.0,295.0,261.0,230.0,202.0,177.0,155.0,135.0,118.0,103.0,89.6,78.4,68.8,60.5,53.3],
                                "RH2M": null
                            }
                        },
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
        },
        "met": {
            "files": [
                {
                    "file": "/data/Met/CANSAC/6km/ARL/wrfout_d2.20140530.f00-11_12hr01.arl",
                    "first_hour": "2014-05-30T00:00:00",
                    "last_hour": "2014-05-30T11:00:00"
                },
                {
                    "file": "/data/Met/CANSAC/6km/ARL/wrfout_d2.20140530.f00-11_12hr01.arl",
                    "first_hour": "2014-05-30T12:00:00",
                    "last_hour": "2014-05-30T23:00:00"
                }
            ]
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



#### Localmet and plumerise not yet run

NOTE: passing data in without plumerise and localmet data may
not be supported. It's TBD

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/run/dispersion/DRI6km/" -H 'Content-Type: application/json' -d '
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
