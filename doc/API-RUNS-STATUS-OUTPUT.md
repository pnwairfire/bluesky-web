
## GET /api/v1/runs/<guid>

This API returns the status of a specific dispersion run

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v1/runs/<guid> (/api/v1/run/<guid>/status is also supported for backwards compatibility)
 - method: GET

### Response

    {
        "percent": <float>,
        "queue": {
            "name": "<queue_name>",
            "position": <int>
        },
        "initiated_at": "<ts>",
        "complete": <boolean>,
        "status": {
            "ts": "<ts>",
            "status": "<str>",
            "stdout": "<last_line_in_stdout>",
            "log": "<last_line_in_log_file>"
        },
        "run_id": "<run_id>"
    }

Note:
 - the 'queue' field will only be in the response if the run is currently enqueued
 - the 'stdout' and 'log' fields, under 'status', will only be in the response if they're available

### Example:

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/runs/abc123"

An enqueued run:

    {
        "percent": 0,
        "queue": {
            "name": "dri",
            "position": 2
        },
        "initiated_at": "2017-08-02T18:09:27Z",
        "complete": false,
        "status": {
            "ts": "2017-08-02T18:09:27Z",
            "status": "enqueued"
        },
        "run_id": "e239a018-77ac-11e7-92f9-3c15c2c6639e"
    }

A run in progress:

    {
        "percent": 50,
        "initiated_at": "2017-08-02T18:05:22Z",
        "complete": false,
        "status": {
            "ts": "2017-08-02T18:05:45Z",
            "stdout": "Warning 1: No UNIDATA NC_GLOBAL:Conventions attribute\n",
            "status": "running",
            "log": "2017-08-02 18:05:44,923 DEBUG: Creating three hour (RedColorBar) concentration plot 23 of 24 \n"
        },
        "run_id": "271b36a6-77ad-11e7-807e-3c15c2c6639e"
    }

A completed run:
    {
        "percent": 100,
        "initiated_at": "2017-08-02T16:57:04Z",
        "status": {
            "ts": "2017-08-02T16:57:46Z",
            "status": "completed"
        },
        "run_id": "9c3ca370-77a3-11e7-adb5-3c15c2c6639e",
        "output_url": "http://localhost:8886/bluesky-web-output/9c3ca370-77a3-11e7-adb5-3c15c2c6639e",
        "complete": true
    }





## GET /api/v1/runs/[<status>/]

This API returns the status of multiple runs

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v1/runs/[<status>/]
 - optional query args:
  - limit (int)
  - offset (int)
  - raw (bool) -- return raw data from db
 - method: GET

### Response

    {
        "runs": [
            {
                "percent": <float>,
                "queue": {
                    "name": "<queue_name>",
                    "position": <int>
                },
                "initiated_at": "<ts>",
                "complete": <boolean>,
                "status": {
                    "ts": "<ts>",
                    "status": "<str>",
                    "stdout": "<last_line_in_stdout>",
                    "log": "<last_line_in_log_file>"
                },
                "run_id": "<run_id>"
            },
            ...
        ]
    }

See notes under status API response, above

### Examples

All statuses, with limit and offset

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/runs/?limit=3&offset=1" |python -m json.tool

    {
        "runs": [
            {
                "percent": 0,
                "queue": {
                    "name": "dri",
                    "position": 2
                },
                "initiated_at": "2017-08-02T18:09:27Z",
                "complete": false,
                "status": {
                    "ts": "2017-08-02T18:09:27Z",
                    "status": "enqueued"
                },
                "run_id": "e239a018-77ac-11e7-92f9-3c15c2c6639e"
            },
            {
                "percent": 50,
                "initiated_at": "2017-08-02T18:05:22Z",
                "complete": false,
                "status": {
                    "ts": "2017-08-02T18:05:45Z",
                    "stdout": "Warning 1: No UNIDATA NC_GLOBAL:Conventions attribute\n",
                    "status": "running",
                    "log": "2017-08-02 18:05:44,923 DEBUG: Creating three hour (RedColorBar) concentration plot 23 of 24 \n"
                },
                "run_id": "271b36a6-77ad-11e7-807e-3c15c2c6639e"
            },
            {
                "percent": 100,
                "initiated_at": "2017-08-02T16:57:04Z",
                "status": {
                    "ts": "2017-08-02T16:57:46Z",
                    "status": "completed"
                },
                "run_id": "9c3ca370-77a3-11e7-adb5-3c15c2c6639e",
                "output_url": "http://localhost:8886/bluesky-web-output/9c3ca370-77a3-11e7-adb5-3c15c2c6639e",
                "complete": true
            }
        ]
    }

Only enqueued runs

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/runs/enqueued" |python -m json.tool

    {
        "runs": [
            {
                "percent": 0,
                "queue": {
                    "name": "dri",
                    "position": 2
                },
                "initiated_at": "2017-08-02T18:09:27Z",
                "complete": false,
                "status": {
                    "ts": "2017-08-02T18:09:27Z",
                    "status": "enqueued"
                },
                "run_id": "e239a018-77ac-11e7-92f9-3c15c2c6639e"
            }
        ]
    }






## GET /api/v1/runs/<guid>/output

This API returns the output location for a specific run

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v1/runs/<guid>/output (/api/v1/run/<guid>/output is also supported for backwards compatibility)
 - method: GET

### Response

Varies based on type of run - plumerise, hsyplit dispersion, or vsmoke

### Examples:

#### Plumerise run output

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/runs/abc123/output"

    {
      "run_id": "9617845e-6c10-11e7-ace3-3c15c2c6639e",
      "fire_information": [
        {
          "id": "96de73a2",
          "growth": [
            {
              "start": "2014-05-29T17:00:00",
              "plumerise": {
                "2014-05-29T17:00:00": {
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
                },
                ...
                "2014-05-30T16:00:00": {
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
              },
              "location": {
                "longitude": -119.7615805,
                "utc_offset": "-07:00",
                "area": 10000,
                "latitude": 37.909644,
                "ecoregion": "western"
              },
              "end": "2014-05-30T17:00:00"
            }
          ],
          "fuel_type": "natural",
          "type": "wildfire"
        }
      ]
    }


#### Dispersion run output

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/runs/abc123/output"

As mentioned above, there are currently two ways the visualization
images may be specified in the results json object.  If you specified
'image_results_version=v2' in the request to initiate the dispersion
run, you'll get something like the following:

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
        "root_url": "http://localhost:8888/bluesky-web-output/abc123"
    }

Otherwise, if you set 'image_results_version=v1' or if you didn't
set it at all, you'll get something like the following:

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
        "root_url": "http://localhost:8888/bluesky-web-output/812ee94a-cb78-11e5-9d7c-0242ac110003-image-format-v1"
    }
