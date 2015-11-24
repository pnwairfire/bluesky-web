if [ $# -lt 1 ] || [ $# -gt 2 ]
  then
    echo "Usage: $0 <hostname> [response output file]"
    echo "Ex:  $0 localhost:8888 /tmp/web-regression-out"
    echo ""
    exit 1
fi

BLUESKY_API_HOSTNAME=$1
if [ $# -eq 2 ]
  then
    OUTPUT_FILE=$2
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
    http://$BLUESKY_API_HOSTNAME/api/v1/domains/DRI2km
    http://$BLUESKY_API_HOSTNAME/api/v1/domains/DRI2km/
    http://$BLUESKY_API_HOSTNAME/api/v1/domains/DRI2km/available-dates
    http://$BLUESKY_API_HOSTNAME/api/v1/domains/DRI2km/available-dates/
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

echo -n "Testing http://$BLUESKY_API_HOSTNAME/api/v1/run/emissions/ ... "
echo -n "http://$BLUESKY_API_HOSTNAME/api/v1/run/ - " >> $OUTPUT_FILE
response=$(curl "http://$BLUESKY_API_HOSTNAME/api/v1/run/emissions/" --write-out "$WRITE_OUT_PATTERN" --silent  -H "Content-Type: application/json" -d '{
        "fire_information": [
            {
                "id": "SF11C14225236095807750",
                "event_id": "SF11E826544",
                "name": "Natural Fire near Snoqualmie Pass, WA",
                "location": {
                    "perimeter": {
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
rm $OUTPUT_FILE-t

# to post data in a file
# curl -D - "http://$BLUESKY_API_HOSTNAME/api/v1/run/" \
#     -H "Content-Type: application/json" \
#     -X POST -d @/path/to/fires.json
