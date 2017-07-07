"""blueskyweb.app"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import logging

import afscripting
import tornado.ioloop
#import tornado.log
import tornado.web

# TODO: use path args for version and api module. ex:
#  routes = [
#    ('/api/<api_version:[^/]+>/<api_module:[^/]+>/'), Dispatcher
#  ]
# and have dispatcher try to dynamically import and run the
# appropriate hander, returning 404 if not implemented
from .api.ping import Ping
from .api.v1.domain import (
    DomainInfo as DomainInfoV1,
    DomainAvailableDates as DomainAvailableDatesV1
)
from .api.v1.run import (
    RunExecuter as RunExecuterV1,
    RunStatus as RunStatusV1,
    RunOutput as RunOutputV1,
    EXPORT_MODE,
    EXPORT_CONFIGURATION
)

DEFAULT_LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s %(filename)s#%(funcName)s: %(message)s"
def configure_logging(log_level, log_file, log_format):
    log_level = log_level or logging.WARNING
    log_format = log_format or DEFAULT_LOG_FORMAT

    # mock the argsparse args object to pass into log config function
    class Args(object):
        def __init__(self, **kwargs):
            [setattr(self, k, v) for k,v in kwargs.items()]

    afscripting.args.configure_tornado_logging_from_args(
        Args(log_message_format=log_format, log_level=log_level, log_file=log_file))

DEFAULT_SETTINGS = {
    'port': 8888,
    'mongodb_url': "mongodb://localhost/blueskyweb",
    'log_file': '/var/log/blueskyweb/blueskyweb.log'
}

def get_routes(path_prefix):
    routes = [
        # TODO: update all patterns to allow optional trailing slash
        (r"/api/ping/?", Ping),
        (r"/api/v1/domains/?", DomainInfoV1),
        (r"/api/v1/domains/([^/]+)/?", DomainInfoV1),
        (r"/api/v1/domains/([^/]+)/available-dates/?", DomainAvailableDatesV1),
        (r"/api/v1/available-dates/?", DomainAvailableDatesV1),
        (r"/api/v1/run/(fuelbeds|emissions|dispersion|all)/?", RunExecuterV1),
        (r"/api/v1/run/(dispersion|all)/([^/]+)/?", RunExecuterV1),
        (r"/api/v1/run/([^/]+)/status/?", RunStatusV1),
        (r"/api/v1/run/([^/]+)/output/?", RunOutputV1)
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
    configure_logging(settings['log_level'], settings['log_file'],
        settings.get('log_format'))

    settings = dict(DEFAULT_SETTINGS, **settings)
    for k in settings:
        tornado.log.gen_log.info(' * %s: %s', k, settings[k])

    if settings.get('path_prefix'):
        settings['path_prefix'] = '/' + settings['path_prefix'].lstrip('/')

    os.environ["MONGODB_URL"] = settings['mongodb_url']

    routes = get_routes(settings.get('path_prefix'))
    application = tornado.web.Application(routes, **settings)
    application.listen(settings['port'])
    tornado.ioloop.IOLoop.current().start()
