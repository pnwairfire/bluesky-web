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

Use the help (-h) option to see usage and available config options:

    bsp-web -h

### Run in Docker

    docker build -t bluesky-web .

Then run in two separate terminals (or in one, if you use the `-d` option)

    docker-compose -f docker-compose.yml up -d
    docker-compose -f docker-compose-worker.yml up




### Fabric


To see list tasks:

    cd /path/to/airfire-bluesky-web
    fab -l

To see documentation for a specific task, use the '-d' option. E.g.:

    fab -d deploy

#### Playground Environment

    BLUESKYWEB_ENV=production fab -A deploy




## APIs

See [APIs](API.md)

