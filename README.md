# BlueSky Web

The blueskyweb package contains a tornado web service, wrapping
[bluesky][https://github.com/pnwairfire/bluesky],
that can be started by simply running ```bsp-web```.

## Non-python Dependencies

## Python dependencies to install manually

blueskyweb depends on the
[bluesky scheduler](https://bitbucket.org/fera/airfire-bluesky-scheduler),
another repo in AirFire's private bitbucket account.  Install it with the following:

    git clone git@bitbucket.org:fera/airfire-bluesky-scheduler.git
    cd airfire-bluesky-scheduler
    pip install --trusted-host pypi.smoke.airfire.org -r requirements.txt
    python setup.py install

### mongodb

BlueSky web connects to a mongodb database to query met data availability.
You just need to provide the url of one that is running.

## Development

### Clone Repo

Via ssh:

    git clone git@bitbucket.org:fera/airfire-bluesky-web.git

or http:

    git clone https://jdubowy@bitbucket.org/fera/airfire-bluesky-web.git

### Install Dependencies

First, install pip (with sudo if necessary):

    apt-get install python-pip

Run the following to install python dependencies:

    pip install --trusted-host pypi.smoke.airfire.org -r requirements.txt

Run the following to install packages required for development:

    pip install -r requirements-dev.txt

## Running

Use the help (-h) option to see usage and available config options:

    bsp-web -h

### Fabric

For the convenience of those wishing to run the web service on a remote server,
this repo contains a fabfile defining tasks for setting up,
deploying to, and restarting the service on a remote server.

To see what tasks are available, clone the repo, cd into it, and run

    git clone git@bitbucket.org:fera/airfire-bluesky-web.git
    cd bluesky-web
    BLUESKYWEB_SERVERS=username@hostname fab -l

(The 'BLUESKYWEB_SERVERS=username@hostname' is needed because it's used to set
the role definitions, which are be done at the module scope.)

To see documentation for a specific task, use the '-d' option. E.g.:

    BLUESKYWEB_SERVERS=username@hostname fab -d deploy

#### Examples

##### VM managed by vagrant

    export PYTHON_VERSION=2.7.8
    export VIRTUALENV_NAME=vm-playground
    export BLUESKYWEB_SERVERS=vagrant@127.0.0.1:2222
    export PROXY_VIA_APACHE=
    export EXPORT_MODE=localsave
    fab -A setup
    fab -A provision
    fab -A deploy

Note that the deploy task takes care of restarting.

##### Two remote servers

    export BLUESKYWEB_SERVERS=username-a@hostname-a,username-b@hostname-b
    export EXPORT_MODE=upload
    fab -A setup
    fab -A provision
    fab -A deploy

##### Playground

    export PYTHON_VERSION=2.7.8
    export VIRTUALENV_NAME=playground
    export BLUESKYWEB_SERVERS=user@server1
    export PROXY_VIA_APACHE=
    export EXPORT_MODE=localsave  # TODO: eventaully make it 'upload' if necessary
    fab -A setup
    fab -A provision
    fab -A deploy


#### Old pg.blueskywebhost.com env (*** DELETE THIS SECTION ONCE RETIRED ***)

    export PYTHON_VERSION=2.7.8
    export VIRTUALENV_NAME=playground
    export BLUESKYWEB_SERVERS=user@server2
    export PROXY_VIA_APACHE=
    export EXPORT_MODE=localsave
    fab -A setup
    fab -A provision
    fab -A deploy



## APIs

See [APIs](API.md)

