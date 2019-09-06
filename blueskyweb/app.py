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
#    ('/api/v<api_version:[^/]+>/<api_module:[^/]+>/'), Dispatcher
#  ]
# and have dispatcher try to dynamically import and run the
# appropriate hander, returning 404 if not implemented
from .api.ping import Ping
from .api.met import DomainInfo, MetArchivesInfo, MetArchiveAvailability

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
    'mongodb_url': "mongodb://blueskyweb:blueskywebmongopassword@mongo/blueskyweb",
    'rabbitmq_url': "amqps://blueskyweb:blueskywebrabbitpassword@rabbit:5671",
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
    # We need to import inline so that MONGDB_URL and RABBITMQ_URL env vars
    # are set:
    #    os.environ["MONGODB_URL"] = settings['mongodb_url']
    #    os.environ["RABBITMQ_URL"] = settings['rabbitmq_url']
    # before blueskyworker.tasks is imported in .api.v1.run
    from .api.run import RunExecute, RunStatus, RunOutput, RunsInfo
    from .api.run import RunExecute, RunStatus, RunOutput, RunsInfo
    routes = [
        (r"/api/ping/?", Ping),

        # Getting information about met domains
        (r"/api/v(1|4.1)/met/domains/?", DomainInfo),
        (r"/api/v(1|4.1)/met/domains/([^/]+)/?", DomainInfo),

        # Getting information about all met data archives
        (r"/api/v(1|4.1)/met/archives/?", MetArchivesInfo),
        # Getting information about specific met archive or
        # collection ('standard', 'special', 'fast', etc.)
        (r"/api/v(1|4.1)/met/archives/([^/]+)/?", MetArchivesInfo),
        # Checking specific date avaialbility
        (r"/api/v(1|4.1)/met/archives/([^/]+)/([0-9-]+)/?", MetArchiveAvailability),

        # Initiating runs
        (r"/api/v(1|4.1)/run/(fuelbeds|emissions|dispersion|all)/?", RunExecute),
        (r"/api/v(1|4.1)/run/(plumerise|dispersion|all)/([^/]+)/?", RunExecute),
        # Getting information about runs
        # Note: The following paths are supported for backwards compatibility:
        #       - /api/v(1|4.1)/run/<guid>/status/
        #       - /api/v(1|4.1)/run/<guid>/output/
        #     the current paths are:
        #       - /api/v(1|4.1)/runs/<guid>/
        #       - /api/v(1|4.1)/runs/<guid>/output/
        (r"/api/v(1|4.1)/runs/?", RunsInfo),
        (r"/api/v(1|4.1)/runs/({})/?".format('|'.join(RunStatuses.statuses)),
            RunsInfo),
        (r"/api/v(1|4.1)/runs/([^/]+)/?", RunStatus),
        (r"/api/v(1|4.1)/run/([^/]+)/status/?", RunStatus),
        (r"/api/v(1|4.1)/runs?/([^/]+)/output/?", RunOutput),
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

    os.environ["RABBITMQ_URL"] = settings['rabbitmq_url']

    routes = get_routes(settings.get('path_prefix'))
    application = tornado.web.Application(routes, **settings)
    application.listen(settings['port'])
    tornado.ioloop.IOLoop.current().start()
