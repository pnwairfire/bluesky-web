#!/usr/bin/env bash

if [ $# -lt 2 ] || [ $# -gt 5 ]
  then
    echo "Usage: $0 <root_url> <domain> <archive> <date> [response output file]"
    echo "Examples:"
    echo "  $0 http://localhost:8887/bluesky-web/ NAM84 national_12-km 2015-08-05 ./tmp/web-regression-out-dev.log"
    echo "  $0 https://www.blueskywebhost.com/bluesky-web-test/ DRI1.33km ca-nv_1.33-km \`date "+%Y-%m-%d"\` ./tmp/web-regression-out-test.log"
    echo "  $0 https://www.blueskywebhost.com/bluesky-web/ DRI1.33km ca-nv_1.33-km \`date "+%Y-%m-%d"\` ./tmp/web-regression-out-prod.log"
    echo ""
    exit 1
fi

# trim trailing slash from root url
ROOT_URL=$(echo $1 | sed 's:/*$::')
DOMAIN=$2
ARCHIVE=$3
DATE=$4
if [ $# -eq 5 ]
  then
    OUTPUT_FILE=$5
else
    OUTPUT_FILE=/dev/null
fi

echo "Testing $ROOT_URL"
echo "Domain: $DOMAIN"
echo "Archive: $ARCHIVE"
echo "Date: $DATE"
echo "Outputing to $OUTPUT_FILE"

echo -n "" > $OUTPUT_FILE


RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color
print_response() {
    response=$1
    if [ ${response:0:3} = 200 ]; then
        printf "${GREEN}${response}${NC}\n"
    else
        printf "${RED}${response}${NC}\n"
    fi
}


# Note: this test does not include dispersion related apis, i.e.
#   - /api/v[1|4.1]/run/dispersion/
#   - /api/v[1|4.1]/run/all/
#   - /api/v[1|4.1]/run/RUN_ID/status/
#   - /api/v[1|4.1]/run/RUN_ID/output/

GET_URLS=(
    $ROOT_URL/api/ping
    $ROOT_URL/api/ping/
    $ROOT_URL/api/v1/met/domains
    $ROOT_URL/api/v1/met/domains/
    $ROOT_URL/api/v1/met/domains/$DOMAIN
    $ROOT_URL/api/v1/met/domains/$DOMAIN/
    $ROOT_URL/api/v1/met/archives
    $ROOT_URL/api/v1/met/archives/
    $ROOT_URL/api/v1/met/archives/standard
    $ROOT_URL/api/v1/met/archives/standard/
    $ROOT_URL/api/v1/met/archives/special
    $ROOT_URL/api/v1/met/archives/special/
    $ROOT_URL/api/v1/met/archives/fast
    $ROOT_URL/api/v1/met/archives/fast/
    $ROOT_URL/api/v1/met/archives/$ARCHIVE
    $ROOT_URL/api/v1/met/archives/$ARCHIVE/
    $ROOT_URL/api/v1/met/archives/$ARCHIVE/$DATE
    $ROOT_URL/api/v1/met/archives/$ARCHIVE/$DATE/
    $ROOT_URL/api/v4_1/met/archives/$ARCHIVE
    $ROOT_URL/api/v4_1/met/archives/$ARCHIVE/
    $ROOT_URL/api/v4_1/met/archives/$ARCHIVE/$DATE
    $ROOT_URL/api/v4_1/met/archives/$ARCHIVE/$DATE/
)
WRITE_OUT_PATTERN="%{http_code} (%{time_total}s)"
for i in "${GET_URLS[@]}"
  do
    echo -n "Testing $i ... "
    echo -n "$i - " >> $OUTPUT_FILE
    response=$(curl "$i" --write-out "$WRITE_OUT_PATTERN" --silent -o "$OUTPUT_FILE-t")
    cat $OUTPUT_FILE-t >> $OUTPUT_FILE
    echo "" >> $OUTPUT_FILE
    print_response $response
    rm $OUTPUT_FILE-t
done


##
## V1 fuelbeds & emissions
##

echo -n "Testing $ROOT_URL/api/v1/run/fuelbeds/ ... "
echo -n "$ROOT_URL/api/v1/run/fuelbeds/ - " >> $OUTPUT_FILE
response=$(curl "$ROOT_URL/api/v1/run/fuelbeds/" --write-out "$WRITE_OUT_PATTERN" --silent  -H "Content-Type: application/json" -d '{
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
                            "ecoregion": "southern",
                            "utc_offset": "-09:00"
                        }
                    }
                ]
            }
        ],
        "config": {
            "emissions":{
                "efs": "feps",
                "species": ["PM2.5"]
            }
        }
    }' -o "$OUTPUT_FILE-t")
cat $OUTPUT_FILE-t >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
print_response $response
#next_request=$(cat $OUTPUT_FILE-t)
#echo $next_request
rm $OUTPUT_FILE-t


echo -n "Testing $ROOT_URL/api/v1/run/emissions/ ... "
echo -n "$ROOT_URL/api/v1/run/emissions/ - " >> $OUTPUT_FILE
# TODO: figure out how to feed next_response back tino
#cmd='curl "$ROOT_URL/api/v1/run/emissions/" --write-out "$WRITE_OUT_PATTERN" --silent  -H "Content-Type: application/json" -d '"'"'$next_request'"'"' -o "$OUTPUT_FILE-t"'
#response=$(eval "$cmd")
response=$(curl "$ROOT_URL/api/v1/run/emissions/" --write-out "$WRITE_OUT_PATTERN" --silent  -H "Content-Type: application/json" -d '{
        "config": {
            "emissions": {
                "efs": "feps",
                "species": ["PM2.5"]
            }
        },
        "fire_information": [
            {
                "event_of": {
                    "name": "Natural Fire near Snoqualmie Pass, WA",
                    "id": "SF11E826544"
                },
                "growth": [
                    {
                        "fuelbeds": [
                            {
                                "fccs_id": "9",
                                "pct": 100.0
                            }
                        ],
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
    }' -o "$OUTPUT_FILE-t")
cat $OUTPUT_FILE-t >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
print_response $response
rm $OUTPUT_FILE-t


##
## V4.1 Fuelbeds & emissions
##

echo -n "Testing $ROOT_URL/api/v4.1/run/fuelbeds/ ... "
echo -n "$ROOT_URL/api/v4.1/run/fuelbeds/ - " >> $OUTPUT_FILE
response=$(curl "$ROOT_URL/api/v4.1/run/fuelbeds/" --write-out "$WRITE_OUT_PATTERN" --silent  -H "Content-Type: application/json" -d '{
        "fires": [
            {
                "id": "SF11C14225236095807750",
                "event_id": "SF11E826544",
                "name": "Natural Fire near Snoqualmie Pass, WA",
                "activity": [
                    {
                        "active_areas": [
                            {
                                "perimeter": {
                                    "polygon": [
                                        [-121.4522115, 47.4316976],
                                        [-121.3990506, 47.4316976],
                                        [-121.3990506, 47.4099293],
                                        [-121.4522115, 47.4099293],
                                        [-121.4522115, 47.4316976]
                                    ]
                                },
                                "ecoregion": "southern",
                                "utc_offset": "-09:00"
                            }
                        ]
                    }
                ]
            }
        ]
    }' -o "$OUTPUT_FILE-t")
cat $OUTPUT_FILE-t >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
print_response $response
#next_request=$(cat $OUTPUT_FILE-t)
#echo $next_request
rm $OUTPUT_FILE-t


echo -n "Testing $ROOT_URL/api/v4.1/run/emissions/ ... "
echo -n "$ROOT_URL/api/v4.1/run/emissions/ - " >> $OUTPUT_FILE
# TODO: figure out how to feed next_response back tino
#cmd='curl "$ROOT_URL/api/v4.1/run/emissions/" --write-out "$WRITE_OUT_PATTERN" --silent  -H "Content-Type: application/json" -d '"'"'$next_request'"'"' -o "$OUTPUT_FILE-t"'
#response=$(eval "$cmd")
response=$(curl "$ROOT_URL/api/v4.1/run/emissions/" --write-out "$WRITE_OUT_PATTERN" --silent  -H "Content-Type: application/json" -d '{
        "config": {
            "emissions": {
                "efs": "feps",
                "species": ["PM2.5"]
            }
        },
        "fires": [
            {
                "id": "SF11C14225236095807750",
                "event_id": "SF11E826544",
                "name": "Natural Fire near Snoqualmie Pass, WA",
                "activity": [
                    {
                        "active_areas": [
                            {
                                "perimeter": {
                                    "polygon": [
                                        [-121.4522115, 47.4316976],
                                        [-121.3990506, 47.4316976],
                                        [-121.3990506, 47.4099293],
                                        [-121.4522115, 47.4099293],
                                        [-121.4522115, 47.4316976]
                                    ],
                                    "fuelbeds": [
                                        {
                                            "fccs_id": "9",
                                            "pct": 100.0
                                        }
                                    ],
                                    "area": 2398.94477979842
                                },
                                "ecoregion": "southern",
                                "utc_offset": "-09:00"
                            }
                        ]
                    }
                ]
            }
        ]
    }' -o "$OUTPUT_FILE-t")
cat $OUTPUT_FILE-t >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
print_response $response
rm $OUTPUT_FILE-t


# to post data in a file
# curl -D - "$ROOT_URL/api/v1/run/" \
#     -H "Content-Type: application/json" \
#     -X POST -d @/path/to/fires.json
