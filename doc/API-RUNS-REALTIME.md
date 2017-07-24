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
    }' | python -m json.tool | less

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
    }' | python -m json.tool | less





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

