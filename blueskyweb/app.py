"""blueskyweb.app"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import logging
import os

import afscripting
import tornado.ioloop
#import tornado.log
import tornado.web

from blueskymongo.client import BlueSkyWebDB, RunStatuses

# TODO: use path args for version and api module. ex:
#  routes = [
#    ('/api/<api_version:[^/]+>/<api_module:[^/]+>/'), Dispatcher
#  ]
# and have dispatcher try to dynamically import and run the
# appropriate hander, returning 404 if not implemented
from .api.ping import Ping
from .api.v1.met import (
    DomainInfo as DomainInfoV1,
    MetArchivesInfo as MetArchivesInfoV1,
    MetArchiveAvailability as MetArchiveAvailabilityV1
)

DEFAULT_LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s %(filename)s#%(funcName)s: %(message)s"
def configure_logging(**settings):
    log_level = settings.get('log_level') or logging.WARNING
    log_format = settings.get('log_format') or DEFAULT_LOG_FORMAT

    # mock the argsparse args object to pass into log config function
    class Args(object):
        def __init__(self, **kwargs):
            [setattr(self, k, v) for k,v in kwargs.items()]

    afscripting.args.configure_tornado_logging_from_args(
        Args(log_message_format=log_format, log_level=log_level,
            log_file=settings.get('log_file')))

DEFAULT_SETTINGS = {
    'port': 8887,
    'mongodb_url': "mongodb://localhost:27018/blueskyweb",
    'log_file': '/var/log/blueskyweb/bluesky-web.log',
    # Output url - to access output from the outside world
    'output_url_scheme': 'https',
    'output_url_port': None, # 80
    'output_url_path_prefix': 'bluesky-web-output',
    # this is supposed to be a string, since it's passed into
    # the bsp docker command
    'bluesky_log_level': "INFO"
}

def get_routes(path_prefix):
    # We need to import inline so that MONGDB_URL env var is set
    #    os.environ["MONGODB_URL"] = settings['mongodb_url']
    # before blueskyworker.tasks is imported in .api.v1.run
    from .api.v1.run import (
        RunExecuter as RunExecuterV1,
        RunStatus as RunStatusV1,
        RunOutput as RunOutputV1,
        RunsInfo as RunsInfoV1
    )
    routes = [
        (r"/api/ping/?", Ping),
        # Getting information about met domains
        (r"/api/v1/met/domains/?", DomainInfoV1),
        (r"/api/v1/met/domains/([^/]+)/?", DomainInfoV1),

        # Getting information about all met data archives
        (r"/api/v1/met/archives/?", MetArchivesInfoV1),
        # Getting information about specific met archive or
        # collection ('standard', 'special', 'fast', etc.)
        (r"/api/v1/met/archives/([^/]+)/?", MetArchivesInfoV1),
        # Checking specific date avaialbility
        (r"/api/v1/met/archives/([^/]+)/([0-9-]+)/?", MetArchiveAvailabilityV1),

        # Initiating runs
        (r"/api/v1/run/(fuelbeds|emissions|dispersion|all)/?", RunExecuterV1),
        (r"/api/v1/run/(plumerise|dispersion|all)/([^/]+)/?", RunExecuterV1),
        # Getting information about runs
        # Note: The following paths are supported for backwards compatibility:
        #       - /api/v1/run/<guid>/status/
        #       - /api/v1/run/<guid>/output/
        #     the current paths are:
        #       - /api/v1/runs/<guid>/
        #       - /api/v1/runs/<guid>/output/
        (r"/api/v1/runs/?", RunsInfoV1),
        (r"/api/v1/runs/({})/?".format('|'.join(RunStatuses.statuses)),
            RunsInfoV1),
        (r"/api/v1/runs/([^/]+)/?", RunStatusV1),
        (r"/api/v1/run/([^/]+)/status/?", RunStatusV1),
        (r"/api/v1/runs?/([^/]+)/output/?", RunOutputV1)
    ]
    if path_prefix:
        path_prefix = path_prefix.strip('/')
        if path_prefix: # i.e. it wasn't just '/'
            routes = [('/' + path_prefix + e[0], e[1]) for e in routes]

    tornado.log.gen_log.debug('Routes: %s', routes)
    return routes

def main(**settings):
    """Main method for starting bluesky tornado web service
    """
    settings = {k:v for k,v in settings.items() if v}

    configure_logging(**settings)

    settings = dict(DEFAULT_SETTINGS, **settings)
    for k in settings:
        tornado.log.gen_log.info(' * %s: %s', k, settings[k])

    if settings.get('path_prefix'):
        settings['path_prefix'] = '/' + settings['path_prefix'].lstrip('/')

    os.environ["MONGODB_URL"] = settings['mongodb_url']
    settings['mongo_db'] = BlueSkyWebDB(settings['mongodb_url'])

    routes = get_routes(settings.get('path_prefix'))
    application = tornado.web.Application(routes, **settings)
    application.listen(settings['port'])
    tornado.ioloop.IOLoop.current().start()
