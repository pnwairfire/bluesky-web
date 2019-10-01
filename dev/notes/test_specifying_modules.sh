# modules not specified
curl "$BLUESKY_API_ROOT_URL/api/v1/run/emissions/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": []}' |python -m json.tool
curl "$BLUESKY_API_ROOT_URL/api/v1/run/all/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": []}' |python -m json.tool
curl "$BLUESKY_API_ROOT_URL/api/v1/run/dispersion/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": []}' |python -m json.tool
curl "$BLUESKY_API_ROOT_URL/api/v1/run/all/DRI2km/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": []}' |python -m json.tool
curl "$BLUESKY_API_ROOT_URL/api/v1/run/dispersion/DRI2km/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": []}' |python -m json.tool

# valid modules not specified
curl "$BLUESKY_API_ROOT_URL/api/v1/run/emissions/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": [], "modules":["fuelbeds"]}' |python -m json.tool
curl "$BLUESKY_API_ROOT_URL/api/v1/run/all/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": [], "modules":["emissions", "dispersion"]}' |python -m json.tool
curl "$BLUESKY_API_ROOT_URL/api/v1/run/dispersion/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": [], "modules":["dispersion"]}' |python -m json.tool
curl "$BLUESKY_API_ROOT_URL/api/v1/run/all/DRI2km/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": [], "modules":["emissions", "dispersion"]}' |python -m json.tool
curl "$BLUESKY_API_ROOT_URL/api/v1/run/dispersion/DRI2km/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": [], "modules":["dispersion"]}' |python -m json.tool

# invalid modules not specified
curl -D - "$BLUESKY_API_ROOT_URL/api/v1/run/emissions/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": [], "modules":["dispersion"]}'
curl -D - "$BLUESKY_API_ROOT_URL/api/v1/run/all/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": [], "modules":["sdf"]}'
curl -D - "$BLUESKY_API_ROOT_URL/api/v1/run/dispersion/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": [], "modules":["fuelbeds"]}'
curl -D - "$BLUESKY_API_ROOT_URL/api/v1/run/all/DRI2km/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": [], "modules":["sdf"]}'
curl -D - "$BLUESKY_API_ROOT_URL/api/v1/run/dispersion/DRI2km/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": [], "modules":["fuelbeds"]}'


# some other requests
curl -D - "$BLUESKY_API_ROOT_URL/api/v1/run/dispersion/DRI2km/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": [], "modules":["timeprofiling"]}'
curl -D - "$BLUESKY_API_ROOT_URL/api/v1/run/dispersion/DRI2km/?_m=fuelbeds" -H 'Content-Type: application/json' -d ' { "fire_information": [], "modules":["consumption", "sdfsdf", "timeprofiling"]}'



##
## TODO: Add v4.1 requests
##
