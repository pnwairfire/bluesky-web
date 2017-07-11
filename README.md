# BlueSky Web

The blueskyweb package contains a tornado web service, wrapping
[bluesky][https://github.com/pnwairfire/bluesky],
that can be started by simply running ```bsp-web```.




## External Dependencies

### mongodb

BlueSky web connects to a mongodb database to query met data availability
and to enqueue background plumerise and dispersion runs.
You just need to provide the url of one that is running.




## Development

### Setup

    git clone git@bitbucket.org:fera/airfire-bluesky-web.git
    cd airfire-bluesky-web
    apt-get install python-pip # if necessary
    pip install --trusted-host pypi.smoke.airfire.org -r requirements.txt
    pip install --trusted-host pypi.smoke.airfire.org -r requirements-dev.txt
    pip install -r requirements-test.txt

### Run

    cd /path/to/airfire-bluesky-web
    mkdir -p ./docker-logs/mongodb/ ./docker-logs/web/ \
        ./docker-logs/worker/dri ./docker-logs/worker/nam \
        ./docker-logs/worker/all-met
    foreman start -f Procfile-dev
    arlindexer -d DRI6km -r /DRI_6km \
        -m mongodb://localhost:27018/blueskyweb
    arlindexer -d DRI2km -r /DRI_2km \
        -m mongodb://localhost:27018/blueskyweb

Or use docker by replacing `foreman start -f Procfile-dev` with:

    docker build -t bluesky-web .
    docker-compose -f docker-compose.yml up

### Tail logs

    cd /path/to/airfire-bluesky-web
    find ./docker-logs/ -name *.log -exec tail -f "$file" {} +



## Fabric

To see list tasks:

    cd /path/to/airfire-bluesky-web
    fab -l

To see documentation for a specific task, use the '-d' option. E.g.:

    fab -d deploy

### Playground Environment

    BLUESKYWEB_ENV=production fab -A deploy




## APIs

See [APIs](API.md)
