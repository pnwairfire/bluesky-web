## Met Domains (all)

This API returns information about all domains with ARL data

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v1/met/domains/
 - method: GET

### Response

    {
        "domains": [
            {
                "id": "<domain_id>",
                "resolution_km": <km>,
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

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/met/domains/" | python -m json.tool
    {
        "domains": [
            {
                "id": "NAM3km",
                "resolution_km": 3,
                "boundary": {
                    "ne": {
                        "lat": 48,
                        "lng": -61
                    },
                    "sw": {
                        "lat": 21,
                        "lng": -122.7
                    }
                }
            },
            ...,
            {
                "id": "NWS-06Z-1km-2018-CA-NV",
                "resolution_km": 1,
                "boundary": {
                    "ne": {
                        "lat": 44.4,
                        "lng": -121
                    },
                    "sw": {
                        "lat": 39.5,
                        "lng": -125.3
                    }
                }
            }
        ]
    }




## Met Domain (single)

This API returns information about a specific domain with ARL data

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v1/met/domains/<domain_id>/
 - method: GET

### Response

    {
        "domain": {
            "id": "<domain_id>",
            "resolution_km": <km>,
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

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/met/domains/DRI4km/" | python -m json.tool
    {
        "domain": {
            "id": "DRI4km",
            "resolution_km": 4,
            "boundary": {
                "sw": {
                    "lng": -128.5,
                    "lat": 28.8
                },
                "ne": {
                    "lng": -109.5,
                    "lat": 44.8
                }
            }
        }
    }




## Met Archives (all)

This API returns the dates for which a specific domain has ARL data

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v1/met/archives/[<archive_type>/]
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

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/met/archives/" | python -m json.tool
    {
        "archives": [
            {
                "id": "CA-OR-2018-1km06Z",
                "group": "special",
                "domain_id": "NWS-06Z-1km-2018-CA-NV",
                "begin": null,
                "end": null,
                "title": "NWS 1km 06Z CA/OR"
            },
            {
                "id": "MT-2018-1km00Z",
                "group": "special",
                "domain_id": "NWS-00Z-1km-2018-MT",
                "begin": null,
                "end": null,
                "title": "NWS 1km 00Z Montana"
            },
            {
                "id": "national_3-km",
                "group": "standard",
                "domain_id": "NAM3km",
                "begin": null,
                "end": null,
                "title": "National 3-km"
            },
            {
                "id": "pacific_northwest_1.33-km",
                "group": "standard",
                "domain_id": "PNW1.33km",
                "begin": null,
                "end": null,
                "title": "Pacific Northwest 1.33-km"
            },
            ...
        ]
    }

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/met/archives/special/" | python -m json.tool
    {
        "archives": [
            {
                "id": "CA-OR-2018-1km06Z",
                "group": "special",
                "domain_id": "NWS-06Z-1km-2018-CA-NV",
                "begin": null,
                "end": null,
                "title": "NWS 1km 06Z CA/OR"
            },
            {
                "id": "MT-2018-1km00Z",
                "group": "special",
                "domain_id": "NWS-00Z-1km-2018-MT",
                "begin": null,
                "end": null,
                "title": "NWS 1km 00Z Montana"
            }
        ]
    }




## Met Archive (single)

This API returns the dates for which a specific domain has ARL data

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v1/met/archives/<archive_id>
 - method: GET

### Response


    {
        "archive": {
            "id": "<archive_id>",
            "group": "<special|standard|fast>",
            "domain_id": "<domain_id>",
            "begin": "<YYYY-MM-DD>",
            "end": "<YYYY-MM-DD>",
            "title": "<archive_title>"
        }
    }

### Example

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/met/archives/national_12-km/" | python -m json.tool
    {
        "archive": {
            "id": "national_12-km",
            "group": "standard",
            "domain_id": "NAM84",
            "begin": "2015-08-05",
            "end": "2016-10-05",
            "title": "National 12-km"
        }
    }





## Date Availability check

This API checks availability of a given date for a specific archive.
If not available, it returns alternative dates, if there are any.
For altertermatives, it considers any dates within 3 days of
requested Date.  Use query param 'date_range' to specify a different
date range

### Request

 - url:  $BLUESKY_API_ROOT_URL/api/v1/met/archives/<archive_id>/<date>/
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

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/met/archives/ca-nv_6-km/2014-05-30/" | python -m json.tool
    {
        "alternatives": [
            "2014-05-29",
            "2014-05-31",
            "2014-06-01"
        ],
        "available": true
    }

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/met/archives/ca-nv_6-km/2014-05-30/?date_range=1" | python -m json.tool
    {
        "alternatives": [
            "2014-05-29",
            "2014-05-31"
        ],
        "available": true
    }

#### Date not available, with alternatives

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/met/archives/ca-nv_6-km/2014-05-30/" | python -m json.tool
    {
        "alternatives": [
            "2014-05-29",
            "2014-05-30"
        ],
        "available": false
    }

#### Date not available, no alternatives

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/met/archives/ca-nv_6-km/2014-05-30/" | python -m json.tool
    {
        "alternatives": [],
        "available": false
    }
