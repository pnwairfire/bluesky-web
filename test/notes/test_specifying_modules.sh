# modules not specified
curl "http://$BLUESKY_API_HOSTNAME/api/v1/run/emissions/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": []}' |python -m json.tool
curl "http://$BLUESKY_API_HOSTNAME/api/v1/run/all/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": []}' |python -m json.tool
curl "http://$BLUESKY_API_HOSTNAME/api/v1/run/dispersion/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": []}' |python -m json.tool
curl "http://$BLUESKY_API_HOSTNAME/api/v1/run/all/DRI2km/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": []}' |python -m json.tool
curl "http://$BLUESKY_API_HOSTNAME/api/v1/run/dispersion/DRI2km/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": []}' |python -m json.tool

# valid modules not specified
curl "http://$BLUESKY_API_HOSTNAME/api/v1/run/emissions/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": [], "modules":["fuelbeds"]}' |python -m json.tool
curl "http://$BLUESKY_API_HOSTNAME/api/v1/run/all/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": [], "modules":["emissions", "dispersion"]}' |python -m json.tool
curl "http://$BLUESKY_API_HOSTNAME/api/v1/run/dispersion/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": [], "modules":["dispersion"]}' |python -m json.tool
curl "http://$BLUESKY_API_HOSTNAME/api/v1/run/all/DRI2km/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": [], "modules":["emissions", "dispersion"]}' |python -m json.tool
curl "http://$BLUESKY_API_HOSTNAME/api/v1/run/dispersion/DRI2km/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": [], "modules":["dispersion"]}' |python -m json.tool

# invalid modules not specified
curl -D - "http://$BLUESKY_API_HOSTNAME/api/v1/run/emissions/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": [], "modules":["dispersion"]}'
curl -D - "http://$BLUESKY_API_HOSTNAME/api/v1/run/all/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": [], "modules":["sdf"]}'
curl -D - "http://$BLUESKY_API_HOSTNAME/api/v1/run/dispersion/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": [], "modules":["fuelbeds"]}'
curl -D - "http://$BLUESKY_API_HOSTNAME/api/v1/run/all/DRI2km/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": [], "modules":["sdf"]}'
curl -D - "http://$BLUESKY_API_HOSTNAME/api/v1/run/dispersion/DRI2km/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": [], "modules":["fuelbeds"]}'


# some other requests
curl -D - "http://$BLUESKY_API_HOSTNAME/api/v1/run/dispersion/DRI2km/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": [], "modules":["timeprofiling"]}'
curl -D - "http://$BLUESKY_API_HOSTNAME/api/v1/run/dispersion/DRI2km/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": [], "modules":["consumption", "sdfsdf", "timeprofiling"]}'
