# BlueSky Web

The blueskyweb package contains a tornado web service, wrapping
[bluesky][https://github.com/pnwairfire/bluesky],
that can be started by simply running ```bsp-web```.




## External Dependencies

### mongodb

BlueSky web connects to a mongodb database to query met data availability
and to enqueue background plumerise and dispersion runs.
You just need to provide the url of one that is running.

### Docker

Docker is required to run the bluesky web system - mongodb,
api web service, output web service, bsp workers, and ofelia.




## Development

### Setup and Run in Docker

    git clone git@github.com:pnwairfire/bluesky-web.git pnwairfire-bluesky-web
    cd pnwairfire-bluesky-web
    pip install -r requirements-dev.txt
    ./reboot --rebuild

When using docker, arlindex will automatically be updated every
15 minutes using the mcuadros/ofelia docker image.
If you don't want to wait for it to run, manually run it with:

    docker exec bluesky-web-worker \
        arlindexer -d DRI4km -r /data/Met/CANSAC/4km/ARL/ \
        -m mongodb://blueskyweb:blueskywebmongopassword@mongo/blueskyweb \
        --mongo-ssl-ca-certs /etc/ssl/bluesky-web-client.pem
    docker exec bluesky-web-worker \
        arlindexer -d NAM84 -r /data/Met/NAM/12km/ARL/ \
        -p NAM84_ARL_index.csv \
        -m mongodb://blueskyweb:blueskywebmongopassword@mongo/blueskyweb \
        --mongo-ssl-ca-certs /etc/ssl/bluesky-web-client.pem

Check that service is running:

    curl http://localhost:8887/bluesky-web/api/ping

### Tail logs

    cd /path/to/airfire-bluesky-web
    find ./dev/logs/ -name *.log -exec tail -f "$file" {} +

### dockerized ipython session

    docker run --rm -ti -v $PWD:/usr/src/blueskyweb/ bluesky-web ipython




## Tests

### Unit Tests

    docker run --rm -ti -v $PWD:/usr/src/blueskyweb/ bluesky-web py.test test

## Ad Hoc tests

These can be run outside of docker. See the helpstrings for
the following two scripts for examples

    ./dev/scripts/web-regression-test.sh
    ./dev/scripts/test-async-request.py -h




## APIs

See the [API documentation](doc/README.md)




## Manually connecting to mongodb

start session

    docker exec -ti bluesky-web-mongo \
        mongo -u blueskyweb -p blueskywebmongopassword --ssl \
        --sslCAFile /etc/ssl/bluesky-web-mongod.pem \
        --sslAllowInvalidHostnames --sslAllowInvalidCertificates \
        blueskyweb

run query on command line

    docker exec -ti bluesky-web-mongo \
        mongo -u blueskyweb -p blueskywebmongopassword --ssl \
        --sslCAFile /etc/ssl/bluesky-web-mongod.pem \
        --sslAllowInvalidHostnames --sslAllowInvalidCertificates \
        blueskyweb --eval 'db.met_files.findOne()'

Or with db dsn

    docker exec -ti bluesky-web-mongo \
        mongo mongodb://blueskyweb:blueskywebmongopassword@mongo/blueskyweb \
         --ssl --sslCAFile /etc/ssl/bluesky-web-mongod.pem \
        --sslAllowInvalidHostnames --sslAllowInvalidCertificates \
        --eval 'db.met_files.findOne()'

