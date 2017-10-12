
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
                  "percentile_015": 204.81921283270026,
                  "percentile_070": 302.77622766573086,
                  "percentile_000": 178.10366333278284,
                  "percentile_050": 267.15549499917427,
                  "percentile_060": 284.96586133245256,
                  "percentile_075": 311.68141083237,
                  "percentile_005": 187.008846499422,
                  "percentile_055": 276.06067816581344,
                  "percentile_085": 329.4917771656483,
                  "percentile_080": 320.5865939990091,
                  "percentile_020": 213.7243959993394,
                  "percentile_065": 293.8710444990917,
                  "percentile_010": 195.91402966606114,
                  "percentile_030": 231.5347623326177,
                  "percentile_025": 222.62957916597856,
                  "percentile_100": 356.2073266655657,
                  "percentile_090": 338.3969603322874,
                  "smolder_fraction": 0,
                  "percentile_045": 258.2503118325351,
                  "percentile_095": 347.3021434989265,
                  "percentile_040": 249.34512866589597,
                  "percentile_035": 240.43994549925685
                },
                ...
                "2014-05-30T16:00:00": {
                  "percentile_015": 538.6485338077127,
                  "percentile_070": 796.2630499766187,
                  "percentile_000": 468.39002939801105,
                  "percentile_050": 702.5850440970166,
                  "percentile_060": 749.4240470368177,
                  "percentile_075": 819.6825514465194,
                  "percentile_005": 491.8095308679116,
                  "percentile_055": 726.0045455669172,
                  "percentile_085": 866.5215543863205,
                  "percentile_080": 843.1020529164199,
                  "percentile_020": 562.0680352776133,
                  "percentile_065": 772.8435485067182,
                  "percentile_010": 515.2290323378122,
                  "percentile_030": 608.9070382174143,
                  "percentile_025": 585.4875367475138,
                  "percentile_100": 936.7800587960221,
                  "percentile_090": 889.941055856221,
                  "smolder_fraction": 0,
                  "percentile_045": 679.1655426271161,
                  "percentile_095": 913.3605573261216,
                  "percentile_040": 655.7460411572155,
                  "percentile_035": 632.326539687315
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
