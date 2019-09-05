## Fuelbeds

This API runs bluesky through ingestion and fuelbeds.
It requires posted JSON with three possible top level keys -
'fires', and 'config', and 'modules'. The
'fires' key is required, and it lists the one or
more fires to process. The 'config' key is
optional, and it specifies configuration data and other control
parameters.  The 'modules' is also optional, and is used to
specify a subset of the modules normally run by this API.

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v4.1/run/fuelbeds/
 - method: POST
 - post data:

    {
        "fires": [ ... ],
        "config": { ... },
        "modules": [ ... ]
    }

See [BlueSky Pipeline](https://github.com/pnwairfire/bluesky/blob/v2.7.2/README.md)
for more information about required and optional post data

### Response

In handling this request, blueskyweb will run bluesky in realtime, and the
bluesky results will be in the API response.  The response data will be the
modified version of the request data.  It will include the
"fires" key, the "config" key (if specified), a "processing"
key that includes information from the modules that processed the data, and
a "summary" key.

    {
        "config": { ... },
        "fires": [ ... ],
        "modules": [ ... ],
        "processing": [ ... ],
        "run_id": "<RUN_ID>",
        "summary": { ... }
    }

### Examples

An example with fire location data specified as a geojson

    $ curl "$BLUESKY_API_ROOT_URL/api/v4.1/run/fuelbeds/" -H 'Content-Type: application/json' -d '{
        "fires": [
            {
                "id": "SF11C14225236095807750",
                "event_id": "SF11E826544",
                "name": "Natural Fire near Snoqualmie Pass, WA",
                "activity": [
                    {
                        "active_areas": [
                            {
                                "perimeter": {
                                    "polygon": [
                                        [-121.4522115, 47.4316976],
                                        [-121.3990506, 47.4316976],
                                        [-121.3990506, 47.4099293],
                                        [-121.4522115, 47.4099293],
                                        [-121.4522115, 47.4316976]
                                    ],
                                    "area": 200
                                },
                                "ecoregion": "southern",
                                "utc_offset": "-09:00"
                            }
                        ]
                    }
                ]
            }
        ]
    }' | python -m json.tool | less

Another exmaple, this time running only the fuelbeds
modules, and with fire location data specified as lat + lng + size.

    $ curl "$BLUESKY_API_ROOT_URL/api/v4.1/run/fuelbeds/" -H 'Content-Type: application/json' -d '{
        "modules": ["fuelbeds"],
        "fires": [
            {
                "id": "SF11C14225236095807750",
                "event_of": {
                    "id": "SF11E826544",
                    "name": "Natural Fire near Snoqualmie Pass, WA"
                },
                "activity": [
                    {
                        "active_areas": [
                            {
                                "specified_points": [
                                    {
                                        "lat": 47.4316976,
                                        "lng": -121.3990506,
                                        "area": 200
                                    }
                                ],
                                "utc_offset": "-09:00",
                                "ecoregion": "southern"
                            }
                        ]
                    }
                ]
            }
        ]
    }' | python -m json.tool | less





## Emissions

This API runs bluesky through consumption and emissions.
It requires posted JSON with three possible top level keys -
'fires', and 'config', and 'modules'. The
'fires' key is required, and it lists the one or
more fires to process. The 'config' key is
optional, and it specifies configuration data and other control
parameters.  The 'modules' key is also optional, and is used to
specify a subset of the modules normally run by this API.

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v4.1/run/emissions/
 - method: POST
 - post data:

        {
            "fires": [ ... ],
            "config": { ... },
            "modules": [ ... ]
        }

See [BlueSky Pipeline](https://github.com/pnwairfire/bluesky/blob/v2.7.2/README.md)
for more information about required and optional post data

### Response

In handling this request, blueskyweb will run bluesky in realtime, and the
bluesky results will be in the API response.  The response data will be the
modified version of the request data.  It will include the
"fires" key, the "config" key (if specified), a "processing"
key that includes information from the modules that processed the data, and
a "summary" key.

    {
        "config": { ... },
        "fires": [ ... ],
        "modules": [ ... ],
        "processing": [ ... ],
        "run_id": "<RUN_ID>",
        "summary": { ... }
    }

### Examples

An example with fire location data specified as geojson

    $ echo '{
        "fires": [
            {
                "id": "SF11C14225236095807750",
                "event_id": "SF11E826544",
                "name": "Natural Fire near Snoqualmie Pass, WA",
                "activity": [
                    {
                        "active_areas": [
                            {
                                "start": "2019-08-24T17:00:00",
                                "end": "2010-08-25T17:00:00",
                                "perimeter": {
                                    "polygon": [
                                        [-121.4522115, 47.4316976],
                                        [-121.3990506, 47.4316976],
                                        [-121.3990506, 47.4099293],
                                        [-121.4522115, 47.4099293],
                                        [-121.4522115, 47.4316976]
                                    ],
                                    "area": 200,
                                    "fuelbeds": [
                                        {
                                            "fccs_id": "9",
                                            "pct": 100.0
                                        }
                                    ]
                                },
                                "ecoregion": "southern",
                                "utc_offset": "-09:00"
                            }
                        ]
                    }
                ]
            }
        ]
    }' > dev/data/emissions-input.json

    $ curl "$BLUESKY_API_ROOT_URL/api/v4.1/run/emissions/" \
        -H 'Content-Type: application/json' \
        -d @dev/data/emissions-input.json | python -m json.tool | less


Another exmaple, this time running only the consumption
modules, and with fire location data specified as lat + lng + size.

    $ echo '{
        "modules": ["consumption"],
        "fires": [
            {
                "id": "SF11C14225236095807750",
                "event_of": {
                    "id": "SF11E826544",
                    "name": "Natural Fire near Snoqualmie Pass, WA"
                },
                "activity": [
                    {
                        "active_areas": [
                            {
                                "start": "2019-08-24T17:00:00",
                                "end": "2010-08-25T17:00:00",
                                "specified_points": [
                                    {
                                        "lat": 47.4316976,
                                        "lng": -121.3990506,
                                        "area": 200,
                                        "fuelbeds": [
                                            {
                                                "fccs_id": "9",
                                                "pct": 100.0
                                            }
                                        ]
                                    }
                                ],
                                "utc_offset": "-09:00",
                                "ecoregion": "southern"
                            }
                        ]
                    }
                ]
            }
        ]
    }' > dev/data/consumption-input.json

    $ curl "$BLUESKY_API_ROOT_URL/api/v4.1/run/emissions/" \
        -H 'Content-Type: application/json' \
        -d @dev/data/consumption-input.json | python -m json.tool | less
