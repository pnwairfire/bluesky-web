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

### Setup

    git clone git@github.com:pnwairfire/bluesky-web.git
    cd airfire-bluesky-web
    pip install --trusted-host pypi.smoke.airfire.org \
        -r requirements-dev.txt
    docker build -t bluesky-web .
    docker build -t bluesky-web-nginx -f Dockerfile-nginx .
    mkdir -p ./docker-logs/mongodb/ ./docker-logs/web/ \
        ./docker-logs/worker/dri ./docker-logs/worker/nam \
        ./docker-logs/worker/no-met ./docker-data/mongodb/db \
        ./docker-data/output

### Run

    docker-compose -f dev/docker-compose.yml up

When using docker, arlindex will automatically be updated every
15 minutes using the mcuadros/ofelia docker image.
If you don't want to wait for it to run, manually run it with:

    docker exec bluesky-web-worker-dri \
        arlindexer -d DRI6km -r $HOME/DRI_6km \
        -m mongodb://mongo/blueskywe
    docker exec bluesky-web-worker-nam \
        arlindexer -d NAM84 -r $HOME/NAM84 \
        -p NAM84_ARL_index.csv \
        -m mongodb://localhost:27018/blueskyweb

### Tail logs

    cd /path/to/airfire-bluesky-web
    find ./docker-logs/ -name *.log -exec tail -f "$file" {} +





## Tests

### Unit Tests

    pip install -r requirements-test.txt
    py.test

## Ad Hoc tests

These can be run outside of docker. See the helpstrings for
the following two scripts for examples

    ./dev/scripts/web-regression-test.sh
    ./dev/scripts/test-asynch-request.py -h





## Fabric

To see list tasks:

    fab -l

To see documentation for a specific task, use the '-d' option. E.g.:

    fab -d deploy

### Test Environment

First time:

    FABRIC_USER=$USER BLUESKY_WEB_ENV=test fab -A deploy
    FABRIC_USER=$USER BLUESKY_WEB_ENV=test fab -A start
    FABRIC_USER=$USER BLUESKY_WEB_ENV=test fab -A configure_web_apache_proxy
    FABRIC_USER=$USER BLUESKY_WEB_ENV=test fab -A configure_output_web_apache_proxy

Subsequent deployments:

    FABRIC_USER=$USER BLUESKY_WEB_ENV=test fab -A deploy
    FABRIC_USER=$USER BLUESKY_WEB_ENV=test fab -A restart

Check status

    FABRIC_USER=$USER BLUESKY_WEB_ENV=test fab -A check_status

### Production Environment

Same as test env, but substitude 'production' for 'test' in each
command




## Manually checking deployment

Check processes and look at files installed on web service server,
e.g. haze

    ssh server1 docker ps -a |grep bluesky-web-test
    ssh server1 cat /etc/docker-compose/bluesky-web-test/docker-compose.yml
    ssh server1 cat /etc/bluesky-web/test/config.json

And on worker servers, e.g. judy

    ssh server2 docker ps -a |grep bluesky-web-test
    ssh server2 cat /etc/docker-compose/bluesky-web-test/docker-compose.yml
    ssh server2 cat /etc/bluesky-web/test/config.json
    ssh server2 cat /etc/bluesky-web/test/ofelia/config.ini




## APIs

See [APIs](doc/API.md)
