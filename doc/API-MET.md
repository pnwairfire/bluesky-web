## Met Domains (all)

This API returns information about all domains with ARL data

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v4.2/met/domains/
 - method: GET

### Response

    {
        "domains": [
            {
                "id": "<domain_id>",
                "resolution_km": <km>,
                "grid_size_options": {
                    "1.0": "xy(km): <dist km> x <dist km>",
                    "0.50": "xy(km): <dist km> x <dist km>",
                    "0.75": "xy(km): <dist km> x <dist km>",
                    "0.25": "xy(km): <dist km> x <dist km>"
                },
                "boundary": {
                    "ne": {
                        "lat": <lat>,
                        "lng": <lng>
                    },
                    "sw": {
                        "lat": <lat>,
                        "lng": <lng>
                    }
                }
            },
            ...,
        ]
    }

### Example

    $ curl "$BLUESKY_API_ROOT_URL/api/v4.2/met/domains/" | python -m json.tool
    {
        "domains": [
            {
                "resolution_km": 1.33,
                "grid_size_options": {
                    "0.75": "xy(km): 1000 x 500",
                    "0.25": "xy(km): 300 x 200",
                    "0.50": "xy(km): 600 x 300",
                    "1.0": "xy(km): 1300 x 600"
                },
                "boundary": {
                    "ne": {
                        "lat": 49.4,
                        "lng": -114.6
                    },
                    "sw": {
                        "lat": 41.5,
                        "lng": -126
                    }
                },
                "id": "PNW1.33km"
            },
            ...
        ]
    }




## Met Domain (single)

This API returns information about a specific domain with ARL data

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v4.2/met/domains/<domain_id>/
 - method: GET

### Response

    {
        "domain": {
            "id": "<domain_id>",
            "resolution_km": <km>,
            "grid_size_options": {
                "1.0": "xy(km): <dist km> x <dist km>",
                "0.50": "xy(km): <dist km> x <dist km>",
                "0.75": "xy(km): <dist km> x <dist km>",
                "0.25": "xy(km): <dist km> x <dist km>"
            },
            "boundary": {
                "ne": {
                    "lat": <lat>,
                    "lng": <lng>
                },
                "sw": {
                    "lat": <lat>,
                    "lng": <lng>
                }
            }
        }
    }

### Example

    $ curl "$BLUESKY_API_ROOT_URL/api/v4.2/met/domains/DRI4km/" | python -m json.tool
    {
        "domain": {
            "id": "DRI4km",
            "resolution_km": 2,
            "grid_size_options": {
                "1.0": "xy(km): 1100 x 800",
                "0.50": "xy(km): 600 x 400",
                "0.75": "xy(km): 900 x 600",
                "0.25": "xy(km): 300 x 200"
            },
            "boundary": {
                "sw": {
                    "lat": 28.8,
                    "lng": -128.5
                },
                "ne": {
                    "lat": 44.8,
                    "lng": -109.5
                }
            }
        }
    }




## Met Archives (all)

This API returns the dates for which a specific domain has ARL data

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v4.2/met/archives/[<archive_type>/]
 - method: GET
 - optional query args:
  - available (bool) -- filter by availability

### Response

    {
        "archives": [
            {
                "id": "<archive_id>",
                "group": "<special|standard|fast>",
                "domain_id": "<domain_id>",
                "begin": "<YYYY-MM-DD>",
                "end": "<YYYY-MM-DD>",
                "title": "<archive_title>"
            },
            {
                "id": <archive_id>",
                "group": "<special|standard|fast>",
                "domain_id": "<domain_id>",
                "begin": "<YYYY-MM-DD>",
                "end": "<YYYY-MM-DD>",
                "title": "<archive_title>"
            },
            {
                "id": "<archive_id>",
                "group": "<special|standard|fast>",
                "domain_id": "<domain_id>",
                "begin": "<YYYY-MM-DD>",
                "end": "<YYYY-MM-DD>",
                "title": "<archive_title>"
            },
            {
                "id": "<archive_id>",
                "group": "<special|standard|fast>",
                "domain_id": "<domain_id>",
                "begin": "<YYYY-MM-DD>",
                "end": "<YYYY-MM-DD>",
                "title": "<archive_title>"
            },
            ...
        ]
    }

### Example

    $ curl "$BLUESKY_API_ROOT_URL/api/v4.2/met/archives/" | python -m json.tool
    {
        "archives": [
            {
                "availability": [
                    {
                        "first_hour": "2018-01-01T00:00:00",
                        "last_hour": "2022-01-25T00:00:00"
                    }
                ],
                "begin": "2018-01-01T00:00:00",
                "domain_id": "NAM84",
                "end": "2022-01-25T00:00:00",
                "group": "standard",
                "id": "national_12-km",
                "latest_forecast": "2022-01-21T12:00:00",
                "title": "National 12-km"
            },
            {
                "begin": null,
                "domain_id": "GFS",
                "end": null,
                "group": "standard",
                "id": "global",
                "title": "Global"
            },
            ...
        ]
    }

    $ curl "$BLUESKY_API_ROOT_URL/api/v4.2/met/archives/special/" | python -m json.tool
    {
        "archives": [
            {
                "availability": [
                    {
                        "first_hour": "2015-09-01T00:00:00",
                        "last_hour": "2015-09-13T11:00:00"
                    }
                ],
                "begin": "2015-09-01T00:00:00",
                "domain_id": "DRI2km",
                "end": "2015-09-13T11:00:00",
                "group": "special",
                "id": "ca-nv_2km-sep-2015",
                "latest_forecast": "2015-09-10T12:00:00",
                "title": "Rough Fire"
            },
            {
                "begin": null,
                "domain_id": "NWS-06Z-1km-2018-CA-NV",
                "end": null,
                "group": "special",
                "id": "CA-OR-2018-1km06Z",
                "title": "NWS 1km 06Z CA/OR"
            },
            ...
        ]
    }




## Met Archive (single)

This API returns the dates for which a specific domain has ARL data

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v4.2/met/archives/<archive_id>
 - method: GET

### Response


    {
        "archive": {
            "id": "<archive_id>",
            "group": "<special|standard|fast>",
            "domain_id": "<domain_id>",
            "begin": "<YYYY-MM-DDTHH:MM:SS>",
            "end": "<YYYY-MM-DDTHH:MM:SS>",
            "title": "<archive_title>",
            "availability": [
                {
                    "first_hour": "<YYYY-MM-DDTHH:MM:SS>",
                    "last_hour": "<YYYY-MM-DDTHH:MM:SS>"
                },
                ...
            ],
            "latest_forecast": "<YYYY-MM-DDTHH:MM:SS>"
        }
    }

### Example

    $ curl "$BLUESKY_API_ROOT_URL/api/v4.2/met/archives/national_12-km/" | python -m json.tool
    {
        "archive": {
            "group": "standard",
            "id": "national_12-km",
            "domain_id": "NAM84",
            "begin": "2015-08-05T00:00:00",
            "end": "2018-11-11T12:00:00",
            "title": "National 12-km",
            "availability": [
                {
                    "first_hour": "2015-08-05T00:00:00",
                    "last_hour": "2015-08-08T12:00:00"
                },
                {
                    "first_hour": "2016-10-03T00:00:00",
                    "last_hour": "2016-10-06T12:00:00"
                },
                {
                    "first_hour": "2018-11-07T00:00:00",
                    "last_hour": "2018-11-11T12:00:00"
                }
            ],
            "latest_forecast": "2018-11-08T00:00:00"
        }
    }




## Date Availability check

This API checks availability of a given date for a specific archive.
If not available, it returns alternative dates, if there are any.
For altertermatives, it considers any dates within 3 days of
requested Date.  Use query param 'date_range' to specify a different
date range

### Request

 - url:  $BLUESKY_API_ROOT_URL/api/v4.2/met/archives/<archive_id>/<date>/
 - method: GET
 - optional query args: 'date_range'

### Response

    {
        "available": <boolean>,
        "alternatives": [
           <date>,
           ...
        ]
    }

### Examples

#### Date available

    $ curl "$BLUESKY_API_ROOT_URL/api/v4.2/met/archives/ca-nv_6-km/2014-05-30/" | python -m json.tool
    {
        "alternatives": [
            "2014-05-29",
            "2014-05-31",
            "2014-06-01"
        ],
        "available": true
    }

    $ curl "$BLUESKY_API_ROOT_URL/api/v4.2/met/archives/ca-nv_6-km/2014-05-30/?date_range=1" | python -m json.tool
    {
        "alternatives": [
            "2014-05-29",
            "2014-05-31"
        ],
        "available": true
    }

#### Date not available, with alternatives

    $ curl "$BLUESKY_API_ROOT_URL/api/v4.2/met/archives/ca-nv_6-km/2014-05-30/" | python -m json.tool
    {
        "alternatives": [
            "2014-05-29",
            "2014-05-30"
        ],
        "available": false
    }

#### Date not available, no alternatives

    $ curl "$BLUESKY_API_ROOT_URL/api/v4.2/met/archives/ca-nv_6-km/2014-05-30/" | python -m json.tool
    {
        "alternatives": [],
        "available": false
    }
