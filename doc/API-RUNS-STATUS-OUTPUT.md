
## GET /api/v1/runs/<guid>

This API returns the status of a specific dispersion run

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v1/runs/<guid> (/api/v1/run/<guid>/status is also supported for backwards compatibility)
 - method: GET

### Response

    {
        "run": {
            "server": {
                "ip": "<ip address>"
            },
            "modules": [...list of modules...],
            "output_url": "<root output url>",
            "ts": "2017-07-19T22:13:01Z",
            "queue": "dri",
            "run_id": "6e035f30-6ccf-11e7-b85c-3c15c2c6639e",
            "output_dir": "<root output dir>",
            "status": [
                ["<step>", "<ts>"],
                ...
            ]
        }
    }


### Example:

    $ curl "$BLUESKY_API_ROOT_URL/api/v1/runs/abc123"


    {
        "run": {
            "server": {
                "ip": "63.142.207.34"
            },
            "modules": [
                "findmetdata",
                "timeprofiling",
                "dispersion",
                "visualization",
                "export"
            ],
            "output_url": "http://localhost:8886/pgv3-output/6e035f30-6ccf-11e7-b85c-3c15c2c6639e",
            "ts": "2017-07-19T22:13:01Z",
            "queue": "dri",
            "run_id": "6e035f30-6ccf-11e7-b85c-3c15c2c6639e",
            "output_dir": "/Users/jdubowy/code/airfire-bluesky-web/docker-data/output/pgv3-output/6e035f30-6ccf-11e7-b85c-3c15c2c6639e",
            "status": [
                ["enqueued", "2017-07-19T22:13:01Z"],
                ["dequeued","2017-07-19T22:13:02Z"],
                ["running","2017-07-19T22:13:03Z"],
                ["completed","2017-07-19T22:13:07Z"],
                ["output_written","2017-07-19T22:13:07Z"]
            ]
        }
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
        "root_url": "http://localhost:8888/playground-output/abc123"
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
