if [ $# -lt 2 ] || [ $# -gt 3 ]
  then
    echo "Usage: $0 <hostname> <domain> [response output file]"
    echo "Ex:  $0 localhost:8887 DRI2km /tmp/web-regression-out"
    echo ""
    exit 1
fi

BLUESKY_API_HOSTNAME=$1
DOMAIN=$2
if [ $# -eq 3 ]
  then
    OUTPUT_FILE=$3
else
    OUTPUT_FILE=/dev/null
fi

echo "Testing $BLUESKY_API_HOSTNAME"
echo "Outputing to $OUTPUT_FILE"

echo -n "" > $OUTPUT_FILE

# Note: this test does not include dispersion related apis, i.e.
#   - /api/v1/run/dispersion/
#   - /api/v1/run/all/
#   - /api/v1/run/RUN_ID/status/
#   - /api/v1/run/RUN_ID/output/

GET_URLS=(
    http://$BLUESKY_API_HOSTNAME/api/ping
    http://$BLUESKY_API_HOSTNAME/api/ping/
    http://$BLUESKY_API_HOSTNAME/api/v1/domains
    http://$BLUESKY_API_HOSTNAME/api/v1/domains/
    http://$BLUESKY_API_HOSTNAME/api/v1/domains/$DOMAIN
    http://$BLUESKY_API_HOSTNAME/api/v1/domains/$DOMAIN/
    http://$BLUESKY_API_HOSTNAME/api/v1/domains/$DOMAIN/available-dates
    http://$BLUESKY_API_HOSTNAME/api/v1/domains/$DOMAIN/available-dates/
    http://$BLUESKY_API_HOSTNAME/api/v1/available-dates
    http://$BLUESKY_API_HOSTNAME/api/v1/available-dates/
)
WRITE_OUT_PATTERN="%{http_code} (%{time_total}s)"
for i in "${GET_URLS[@]}"
  do
    echo -n "Testing $i ... "
    echo -n "$i - " >> $OUTPUT_FILE
    response=$(curl "$i" --write-out "$WRITE_OUT_PATTERN" --silent -o "$OUTPUT_FILE-t")
    cat $OUTPUT_FILE-t >> $OUTPUT_FILE
    echo "" >> $OUTPUT_FILE
    echo $response
    rm $OUTPUT_FILE-t
done

echo -n "Testing http://$BLUESKY_API_HOSTNAME/api/v1/run/fuelbeds/ ... "
echo -n "http://$BLUESKY_API_HOSTNAME/api/v1/run/fuelbeds/ - " >> $OUTPUT_FILE
response=$(curl "http://$BLUESKY_API_HOSTNAME/api/v1/run/fuelbeds/" --write-out "$WRITE_OUT_PATTERN" --silent  -H "Content-Type: application/json" -d '{
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
                "species": ["PM25"]
            }
        }
    }' -o "$OUTPUT_FILE-t")
cat $OUTPUT_FILE-t >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
echo $response
#next_request=$(cat $OUTPUT_FILE-t)
#echo $next_request
rm $OUTPUT_FILE-t


echo -n "Testing http://$BLUESKY_API_HOSTNAME/api/v1/run/emissions/ ... "
echo -n "http://$BLUESKY_API_HOSTNAME/api/v1/run/emissions/ - " >> $OUTPUT_FILE
# TODO: figure out how to feed next_response back tino
#cmd='curl "http://$BLUESKY_API_HOSTNAME/api/v1/run/emissions/" --write-out "$WRITE_OUT_PATTERN" --silent  -H "Content-Type: application/json" -d '"'"'$next_request'"'"' -o "$OUTPUT_FILE-t"'
#response=$(eval "$cmd")
response=$(curl "http://$BLUESKY_API_HOSTNAME/api/v1/run/emissions/" --write-out "$WRITE_OUT_PATTERN" --silent  -H "Content-Type: application/json" -d '{
        "config": {
            "emissions": {
                "efs": "feps",
                "species": ["PM25"]
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
echo $response
rm $OUTPUT_FILE-t



# to post data in a file
# curl -D - "http://$BLUESKY_API_HOSTNAME/api/v1/run/" \
#     -H "Content-Type: application/json" \
#     -X POST -d @/path/to/fires.json
