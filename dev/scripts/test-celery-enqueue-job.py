#! /usr/bin/env python3

"""Run with:
    docker run --rm -ti -v $PWD:$PWD -w $PWD \
        -v $HOME/code/celery/:/usr/src/celery/ \
        -e PYTHONPATH=/usr/src/blueskyweb/:/usr/src/celery/ \
        bluesky-web \
        ./dev/scripts/test-celery-enqueue-job.py

    docker exec -ti bluesky-web-1 \
        /usr/src/blueskyweb/dev/scripts/test-celery-enqueue-job.py
"""

__author__ = "Joel Dubowy"
__copyright__ = "Copyright 2018, AirFire, PNW, USFS"

import datetime
import logging
import os
import ssl
from urllib.parse import urlparse

from celery import Celery

BROKER_URL = 'amqp://blueskywebadmin:blueskywebrabbitpassword@rabbit:5671'
app = Celery('test.tasks', backend='amqp', broker=BROKER_URL)

parse_object = urlparse(BROKER_URL)
app.conf.update(
    broker_use_ssl={
        #'ssl': True,
        'keyfile': '/etc/ssl/bluesky-web-client-cert.key',
        'certfile': '/etc/ssl/bluesky-web-client-cert.crt',
        'ca_certs': '/etc/ssl/bluesky-web-client.pem',
        'cert_reqs': ssl.CERT_NONE
    }
)
@app.task
def go(output_filename):
    logging.debug("generating output file: %s", output_filename)
    print("SDFSDFSDF")
    with open(output_filename, 'w') as f:
        f.write('went ' + datetime.datetime.utcnow().isoformat())

def main():
    logging.basicConfig(level=logging.DEBUG)
    output_filename = '/usr/src/blueskyweb/go-foo.txt'
    logging.debug("output file: %s", output_filename)
    go.apply_async(args=[output_filename], queue='no-met')


if __name__ == "__main__":
    main()
