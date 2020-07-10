
## GET /api/v4.2/runs/<guid>

This API returns the status of a specific dispersion run

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v4.2/runs/<guid> (/api/v4.2/run/<guid>/status is also supported for backwards compatibility)
 - method: GET

### Response

    {
        "run_id": "<run_id>",
        "initiated_at": "<ts>",
        "percent": <float>,
        "complete": <boolean>,
        "queue": {
            "name": "<queue_name>",
            "position": <int>
        },
        "status": {
            "ts": "<ts>",
            "status": "<str>",
            "stdout": "<last_line_in_stdout>",
            "log": "<last_line_in_log_file>"
        },
        "runtime": {
            "start": "<YYYY-mm-ddTHH:MM:SSZ>",
            "end": "<YYYY-mm-ddTHH:MM:SSZ>"
        },
        "version_info": {
            "bluesky_version": "<bluesky_version",
            "<module_name>": {
                "version": "<module_version>",
                "<dependency_package>": "<package_version>",
                ...
            },
            ...
        },
        "output_url": "<url>"
    }

Note:
 - the 'queue' field will only be in the response if the run is currently enqueued
 - the 'stdout' and 'log' fields, under 'status', will only be in the response if they're available

### Example:

    $ curl "$BLUESKY_API_ROOT_URL/api/v4.2/runs/abc123/"

An enqueued run:

    {
        "run_id": "e239a018-77ac-11e7-92f9-3c15c2c6639e",
        "initiated_at": "2019-09-05T21:15:30Z",
        "percent": 0,
        "complete": false,
        "queue": {
            "name": "ca-nv_6-km",
            "position": 1
        },
        "status": {
            "status": "enqueued",
            "ts": "2019-09-05T21:15:30.834634Z"
        }
    }

A run in progress:

    {
        "run_id": "test-asynch-request-20190905T211135",
        "initiated_at": "2019-09-05T21:11:35Z",
        "percent": 2,
        "complete": false,
        "status": {
            "ts": "2019-09-05T21:11:36.106921Z",
            "status": "starting_module",
            "module": "dispersion"
        },
        "runtime": {
            "start": "2019-09-05T21:11:35Z",
            "end": null
        }
    }

A completed run:

    {
        "run_id": "79216046-d01c-11e9-b4ad-0242c0a8c007",
        "initiated_at": "2019-09-05T20:33:52Z",
        "percent": 100,
        "complete": true,
        "status": {
            "ts": "2019-09-05T20:34:16.425537Z",
            "status": "completed",
            "perc": 100
        },
        "runtime": {
            "start": "2019-09-05T20:33:52Z",
            "end": "2019-09-05T20:34:16Z"
        },
        "version_info": {
            "consumption": {
                "version": "0.1.0",
                "consume_version": "5.0.2"
            },
            "bluesky_version": "4.2.9",
            "dispersion": {
                "version": "0.1.0",
                "vsmoke_version": "0.1.0"
            },
            "emissions": {
                "version": "0.1.0",
                "consume_version": "5.0.2",
                "emitcalc_version": "2.0.1",
                "eflookup_version": "3.1.2"
            },
            "export": {
                "version": "0.1.0"
            },
            "fuelbeds": {
                "version": "0.1.0",
                "fccsmap_version": "2.1.0"
            },
            "timeprofile": {
                "version": "0.1.1",
                "timeprofile_version": "1.0.0"
            }
        },
        "output_url": "http://localhost:8886/bluesky-web-output/79216046-d01c-11e9-b4ad-0242c0a8c007"
    }




## GET /api/v4.2/runs/[<status>/]

This API returns the status of multiple runs

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v4.2/runs/[<status>/]
 - optional query args:
  - limit (int)
  - offset (int)
  - raw (bool) -- return raw data from db
 - method: GET

### Response

    {
        "total": 114,
        "limit": 10,
        "offset": 0,
        "count": 10,
        "runs": [
            {
                "run_id": "<run_id>",
                "initiated_at": "<ts>",
                "percent": <float>,
                "complete": <boolean>,
                "queue": {
                    "name": "<queue_name>",
                    "position": <int>
                },
                "status": {
                    "ts": "<ts>",
                    "status": "<str>",
                    "stdout": "<last_line_in_stdout>",
                    "log": "<last_line_in_log_file>"
                },
                "runtime": {
                    "start": "<YYYY-mm-ddTHH:MM:SSZ>",
                    "end": "<YYYY-mm-ddTHH:MM:SSZ>"
                },
                "version_info": {
                    "bluesky_version": "<bluesky_version",
                    "<module_name>": {
                        "version": "<module_version>",
                        "<dependency_package>": "<package_version>",
                        ...
                    },
                    ...
                },
                "output_url": "<url>"
            },
            ...
        ]
    }

See notes under status API response, above

### Examples

All statuses, with limit and offset

    $ curl "$BLUESKY_API_ROOT_URL/api/v4.2/runs/?limit=2&offset=1" |python -m json.tool


    {
        "limit": 2,
        "count": 2,
        "total": 114,
        "offset": 1,
        "runs": [
            {
                "percent": 100,
                "version_info": {
                    "bluesky_version": "4.2.9",
                    "emissions": {
                        "eflookup_version": "3.1.2",
                        "version": "0.1.0",
                        "consume_version": "5.0.2",
                        "emitcalc_version": "2.0.1"
                    },
                    ...
                },
                "output_url": "http://localhost:8886/bluesky-web-output/test-asynch-request-20190905T211505",
                "initiated_at": "2019-09-05T21:15:05Z",
                "run_id": "test-asynch-request-20190905T211505",
                "complete": true,
                "status": {
                    "status": "completed",
                    "perc": 100,
                    "ts": "2019-09-05T21:20:05.605901Z"
                },
                "runtime": {
                    "start": "2019-09-05T21:15:05Z",
                    "end": "2019-09-05T21:20:05Z"
                }
            },
            {
                "percent": 100,
                "version_info": {
                    ...
                },
                "output_url": "http://localhost:8886/bluesky-web-output/test-asynch-request-20190905T211459",
                "initiated_at": "2019-09-05T21:14:59Z",
                "run_id": "test-asynch-request-20190905T211459",
                "complete": true,
                "status": {
                    "status": "completed",
                    "perc": 100,
                    "ts": "2019-09-05T21:20:03.207871Z"
                },
                "runtime": {
                    "start": "2019-09-05T21:15:00Z",
                    "end": "2019-09-05T21:20:03Z"
                }
            }
        ]
    }


Only enqueued runs

    $ curl "$BLUESKY_API_ROOT_URL/api/v4.2/runs/enqueued" |python -m json.tool

    {
        "total": 1,
        "limit": 10,
        "runs": [
            {
                "run_id": "e239a018-77ac-11e7-92f9-3c15c2c6639e",
                "initiated_at": "2019-09-05T21:15:30Z",
                "percent": 0,
                "complete": false,
                "queue": {
                    "name": "ca-nv_6-km",
                    "position": 1
                },
                "status": {
                    "status": "enqueued",
                    "ts": "2019-09-05T21:15:30.834634Z"
                }
            }
        ],
        "offset": 0,
        "count": 1
    }




## GET /api/v4.2/runs/<guid>/output

This API returns the output location for a specific run

### Request

 - url: $BLUESKY_API_ROOT_URL/api/v4.2/runs/<guid>/output (/api/v4.2/run/<guid>/output is also supported for backwards compatibility)
 - method: GET

### Response

Varies based on type of run - plumerise, hsyplit dispersion, or vsmoke

### Examples:

#### Plumerise run output

    $ curl "$BLUESKY_API_ROOT_URL/api/v4.2/runs/8915adc2-d026-11e9-878c-0242c0a8d006/output"

    ...TODO: Fill in example...



#### Dispersion run output

    $ curl "$BLUESKY_API_ROOT_URL/api/v4.2/runs/test-asynch-request-20190905T211302/output"

    {
        "root_url": "http://localhost:8886/bluesky-web-output/test-asynch-request-20190905T211302",
        "images": {
            "100m": {
                "daily_maximum": {
                    "UTC+0000": {
                        "RedColorBar": {
                            "other_images": [
                                "100m_daily_maximum_20140530_UTC+0000.png"
                            ],
                            "series": [],
                            "directory": "images/100m/daily_maximum/UTC+0000/RedColorBar",
                            "legend": "100m_colorbar_daily_maximum_UTC+0000.png"
                        },
                        ...
                    },
                    ...
                },
                "three_hour": {
                    "RedColorBar": {
                        "other_images": [],
                        "series": [
                            "100m_three_hour_201405300100.png",
                            ...,
                            "100m_three_hour_201405301000.png"
                        ],
                        "directory": "images/100m/three_hour/RedColorBar",
                        "legend": "100m_colorbar_three_hour.png"
                    },
                    ...
                },
                "hourly": {
                    "RedColorBar": {
                        "other_images": [],
                        "series": [
                            "100m_hourly_201405300000.png",
                            ...
                            "100m_hourly_201405301100.png"
                        ],
                        "directory": "images/100m/hourly/RedColorBar",
                        "legend": "100m_colorbar_hourly.png"
                    },
                    ...
                },
                "daily_average": {
                    "UTC+0000": {
                        "RedColorBar": {
                            "other_images": [
                                "100m_daily_average_20140530_UTC+0000.png"
                            ],
                            "series": [],
                            "directory": "images/100m/daily_average/UTC+0000/RedColorBar",
                            "legend": "100m_colorbar_daily_average_UTC+0000.png"
                        },
                        ...
                    },
                    ...
                }
            },
            "500m": {
                ...
            },
            "1000m": {
                ...
            }
        },
        "version_info": {
            "bluesky_version": "4.2.9",
            "fuelbeds": {
                "version": "0.1.0",
                "fccsmap_version": "2.1.0"
            },
            ...
        },
        "kmzs": {
            "fire": "extras-d2d2a91a-d9ef-4ed7-9cec-e3f41fde6507/fire_locations.kmz",
            "smoke": "extras-d2d2a91a-d9ef-4ed7-9cec-e3f41fde6507/smoke_dispersion.kmz"
        },
        "netCDF": "extras-d2d2a91a-d9ef-4ed7-9cec-e3f41fde6507/hysplit_conc.nc",
        "runtime": {
            "start": "2019-09-05T21:13:02Z",
            "end": "2019-09-05T21:17:47Z"
        }
    }
