#!/usr/bin/env bash

show_help=false
ROOT_URL=http://localhost:8887/bluesky-web/
API_VERSION=
MODE=

while [ -n "$1" ]; do # while loop starts
    case "$1" in
    -h) show_help=true && shift ;;
    --help) show_help=true && shift ;;
    -u) ROOT_URL="$2" && shift && shift ;;
    --root-url) ROOT_URL="$2" && shift && shift ;;
    -v) API_VERSION="$2" && shift && shift ;;
    --api-version) API_VERSION="$2" && shift && shift ;;
    -m) MODE="$2" && shift && shift ;;
    --mode) MODE="$2" && shift && shift ;;
    *) echo "Option $1 not recognized" && exit 1 ;;
    esac
done

if [ "$show_help" = true ] ; then
    echo ""
    echo "Options:"
    echo "   -h/--help        - show this help message"
    echo "   -u/--root-url    - root url of "
    echo "   -v/--api-version -  1, 4.1, or 4.2"
    echo "   -m/--mode        - 'fuelbeds', 'emissons', or 'both'"
    echo ""
    echo "Usage:"
    echo "   $0 -v 4.2 -m fuelbeds"
    echo "   $0 -v 1 -m emissions -u http://localhost:8887/bluesky-web/"
    echo ""
    exit 0
fi

if [ ! $API_VERSION ]; then
    echo "ERROR: Specify -v / --api-version"
    exit 1
fi

if [ "$MODE" != "fuelbeds" ] && [ "$MODE" != "emissions" ] && [ "$MODE" != "both" ]; then
    echo "ERROR: Specify -m / --mode as 'fuelbeds', 'emissions', or 'both'"
    exit 1
fi

if [ "$API_VERSION" != "1" ] && [ "$API_VERSION" != "4.1" ] && [ "$API_VERSION" != "4.2" ]; then
    echo "ERROR: Specify -v / --api-version as '1', '4.1', or '4.2'"
    exit 1
fi

API_VERSION=$(echo $API_VERSION | sed 's:^v*::')
ROOT_URL=$(echo $ROOT_URL | sed 's:/*$::')

FUELBEDS_SECTION=
if [ "$MODE" == "emissions" ]; then
    # using a different fccs id that what's actually at the location
    FUELBEDS_SECTION='"fuelbeds": [{"fccs_id": "52","pct": 100.0}],'
fi

MODULES_SECTION=
if [ "$MODE" == "both" ]; then
    # using a different fccs id that what's actually at the location
    MODULES_SECTION='"modules": ["fuelbeds","ecoregion","consumption","emissions"],'
fi

POST_DATA=
if [ $API_VERSION = 1 ]; then
    POST_DATA='{
        "config": {
            "emissions": {
                "efs": "feps",
                "species": ["PM2.5"]
            }
        },
        '"$MODULES_SECTION"'
        "fire_information": [
            {
                "event_of": {
                    "name": "Natural Fire near Snoqualmie Pass, WA",
                    "id": "SF11E826544"
                },
                "growth": [
                    {
                        '"$FUELBEDS_SECTION"'
                        "start": "2019-08-29T00:00:00",
                        "end": "2019-08-30T00:00:00",
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
                            "ecoregion": "southern",
                            "utc_offset": "-09:00",
                            "area": 2398.94477979842
                        }
                    }
                ]
            }
        ]
    }'
elif [ $API_VERSION = 4.1 ] || [ $API_VERSION = 4.2 ] ; then
    POST_DATA='{
        "config": {
            "emissions": {
                "efs": "feps",
                "species": ["PM2.5"]
            }
        },
        '"$MODULES_SECTION"'
        "fires": [
            {
                "id": "SF11C14225236095807750",
                "event_id": "SF11E826544",
                "name": "Natural Fire near Snoqualmie Pass, WA",
                "activity": [
                    {
                        "active_areas": [
                            {
                                "start": "2019-08-29T00:00:00",
                                "end": "2019-08-30T00:00:00",
                                "utc_offset": "-09:00",
                                "perimeter": {
                                    "polygon": [
                                        [-121.4522115, 47.4316976],
                                        [-121.3990506, 47.4316976],
                                        [-121.3990506, 47.4099293],
                                        [-121.4522115, 47.4099293],
                                        [-121.4522115, 47.4316976]
                                    ],
                                    '"$FUELBEDS_SECTION"'
                                    "area": 2398.94477979842
                                },
                                "ecoregion": "southern"
                            }
                        ]
                    }
                ]
            }
        ]
    }'
fi

MODE_PATH_STRING=emissions
if [ "$MODE" == "fuelbeds" ]; then
    # using a different fccs id that what's actually at the location
    MODE_PATH_STRING=fuelbeds
fi

URL="$ROOT_URL/api/v$API_VERSION/run/$MODE_PATH_STRING/"

curl "$URL" --silent  -H "Content-Type: application/json" -d "$POST_DATA"
