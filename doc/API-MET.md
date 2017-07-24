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

This API returns the dates for which a specific domain has ARL data

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



## GET /api/v1/domains/<domain_id>/available-dates/<date>/

This API checks availability of a given date for a specific domain.
If not available, it returns alternative dates, if there are any.
(For altertermatives, it considers any dates within 3 days of
requested Date.)

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v1/domains/<domain_id>/available-dates/<date>/
 - method: GET

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

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/domains/DRI6km/available-dates/2014-05-30/" | python -m json.tool
    {
        "alternatives": [
            "2014-05-29",
            "2014-05-31",
            "2014-06-01"
        ],
        "available": true
    }

#### Date not available, with alternatives

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/domains/DRI6km/available-dates/2014-05-27/" | python -m json.tool
    {
        "alternatives": [
            "2014-05-29",
            "2014-05-30"
        ],
        "available": false
    }

#### Date not available, no alternatives

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/domains/DRI6km/available-dates/2014-05-24/" | python -m json.tool
    {
        "alternatives": [],
        "available": false
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