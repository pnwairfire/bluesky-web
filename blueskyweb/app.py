"""blueskyweb.app"""

__author__ = "Joel Dubowy"
__copyright__ = "Copyright 2015, AirFire, PNW, USFS"

import logging
import logging.handlers
import os

import uvicorn
from fastapi import FastAPI

from blueskymongo.client import BlueSkyWebDB

DEFAULT_LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s %(filename)s#%(funcName)s: %(message)s"


def configure_logging(**settings):
    log_level = settings.get('log_level') or logging.WARNING
    log_format = settings.get('log_format') or DEFAULT_LOG_FORMAT
    log_file = settings.get('log_file')

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    formatter = logging.Formatter(log_format)
    if log_file:
        handler = logging.handlers.TimedRotatingFileHandler(log_file, when="W0")
    else:
        handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)


DEFAULT_SETTINGS = {
    'port': 8887,
    'mongodb_url': "mongodb://blueskyweb:blueskywebmongopassword@mongo/blueskyweb",
    'rabbitmq_url': "amqps://blueskyweb:blueskywebrabbitpassword@rabbit:5671",
    'log_file': '/var/log/blueskyweb/bluesky-web.log',
    # Output url - to access output from the outside world
    'output_url_scheme': 'https',
    'output_url_port': None,  # 80
    'output_url_path_prefix': 'bluesky-web-output',
    # this is supposed to be a string, since it's passed into
    # the bsp docker command
    'bluesky_log_level': "INFO"
}


def create_app(settings: dict) -> FastAPI:
    """Create and configure the FastAPI application."""
    # We need to import routers after MONGODB_URL and RABBITMQ_URL env vars
    # are set, because blueskyworker.tasks (imported transitively) reads them
    # at module level.
    from .api.ping import router as ping_router
    from .api.config import router as config_router
    from .api.met import router as met_router
    from .api.run import router as run_router
    from .api.queue import router as queue_router

    app = FastAPI()

    path_prefix = settings.get('path_prefix', '')

    for r in [ping_router, config_router, met_router, run_router, queue_router]:
        app.include_router(r, prefix=path_prefix)

    app.state.settings = settings
    return app


def main(**settings):
    """Main method for starting bluesky FastAPI web service."""
    logger = logging.getLogger(__name__)

    settings = {k: v for k, v in settings.items() if v}

    configure_logging(**settings)

    settings = dict(DEFAULT_SETTINGS, **settings)
    for k in settings:
        logger.info(' * %s: %s', k, settings[k])

    if settings.get('path_prefix'):
        settings['path_prefix'] = '/' + settings['path_prefix'].lstrip('/')

    os.environ["MONGODB_URL"] = settings['mongodb_url']
    settings['mongo_db'] = BlueSkyWebDB(settings['mongodb_url'])

    os.environ["RABBITMQ_URL"] = settings['rabbitmq_url']

    app = create_app(settings)

    uvicorn.run(app, host="0.0.0.0", port=int(settings['port']))
