## Met Domains (all)

This API returns information about all domains with ARL data

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v1/met/domains/
 - method: GET

### Response

    [
        {
            "id": <domain_id>",
            "boundary": {
                "ne": {
                    "lat": <lat>,
                    "lng": <lng>,
                "sw": {
                    "lat": <lat>,
                    "lng": <lng>
                }
            },
            "resolution_km": <km>
        },
        ...
    ]

### Example

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/met/domains/" | python -m json.tool
    ...




## Met Domain (single)

This API returns information about a specific domain with ARL data

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v1/met/domains/<domain_id>/
 - method: GET

### Response

    {
        "id": <domain_id>",
        "boundary": {
            "ne": {
                "lat": <lat>,
                "lng": <lng>,
            "sw": {
                "lat": <lat>,
                "lng": <lng>
            }
        },
        "resolution_km": <km>
    }

### Example

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/met/domains/DRI6km/" | python -m json.tool
    ...




## Met Archives (all)

This API returns the dates for which a specific domain has ARL data

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v1/met/archives/[<archive_type>/]
 - method: GET

### Response

    ...

### Example

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/met/archives/" | python -m json.tool
    ...

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/met/archives/standard/" | python -m json.tool
    ...




## Met Archive (single)

This API returns the dates for which a specific domain has ARL data

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v1/met/archives/<archive_id>
 - method: GET

### Response

    ...

### Example

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/met/archives/national_12-km/" | python -m json.tool
    ...




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

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/met/archives/national_12-km/2014-05-30/" | python -m json.tool
    {
        "alternatives": [
            "2014-05-29",
            "2014-05-31",
            "2014-06-01"
        ],
        "available": true
    }

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/met/archives/national_12-km/2014-05-30/?date_range=1" | python -m json.tool
    {
        "alternatives": [
            "2014-05-29",
            "2014-05-31"
        ],
        "available": true
    }

#### Date not available, with alternatives

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/met/archives/national_12-km/2014-05-30/" | python -m json.tool
    {
        "alternatives": [
            "2014-05-29",
            "2014-05-30"
        ],
        "available": false
    }

#### Date not available, no alternatives

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/met/archives/national_12-km/2014-05-30/" | python -m json.tool
    {
        "alternatives": [],
        "available": false
    }
