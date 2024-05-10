"""blueskyconfig"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import copy
import datetime
import json
import os
import threading

import tornado

# Note: afconfig is installed via afscripting
import afconfig

__all__ = [
    "ConfigManagerSingleton",
    "get"
]


# make config data thread safe by storing in thread local,
# which must be defined once, in main thread.
thread_local_data = threading.local()

class ConfigManagerSingleton():

    def __new__(cls, *args, **kwargs):
        if not hasattr(thread_local_data, 'config_manager'):
            thread_local_data.config_manager = object.__new__(cls)
        return thread_local_data.config_manager

    DEFAULT_CONFIG_JSON_FILE = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'json-config-files/defaults.json'))

    def __init__(self):

        # __init__ will be called each time __new__ is called. So, we need to
        # keep track of initialization to abort subsequent reinitialization
        if not hasattr(self, '_initialized'):
            self._data = thread_local_data
            self._config_json_file = self.DEFAULT_CONFIG_JSON_FILE
            self._overrides_files = []
            self._overrides = {}
            self._initialized = True

    # this should never be used, but could if 'cache_ttl_minutes' is
    # accidentally deleted from the config defaults
    _DEFAULT_TTL_SECONDS = 60

    def add_overrides(self, overrides):
        if overrides:
            afconfig.merge_configs(self._overrides, overrides)

    def add_overrides_file(self, overrides_file):
        self._overrides_files.append(overrides_file)

    @property
    def ttl_seconds(self):
        if hasattr(self._data, 'config'):
            ttl = self._data.config.get('cache_ttl_minutes')
            if ttl is not None:
                return ttl * 60

            ttl = self._data.config.get('cache_ttl_seconds')
            if ttl is not None:
                return ttl

        return self._DEFAULT_TTL_SECONDS

    def _load_config_from_file(self, config, filename):
        tornado.log.gen_log.debug(f"Loading config from {filename}")
        with open(filename) as f:
            try:
                c = json.loads(f.read())
                afconfig.merge_configs(config, c)
            except Exception as e:
                tornado.log.gen_log.warn(f"Failed to config from {filename} - {e}")

    def _load_config(self):
        # note that 'afconfig.merge_configs' merges in-place

        config = {}

        # Load defaults
        self._load_config_from_file(config, self._config_json_file)

        # load any overrides files
        for o in self._overrides_files:
            self._load_config_from_file(config, o)

        # load any overrides loaded when bsp-web was started
        if self._overrides:
            tornado.log.gen_log.debug(f"Loading static overrides")
            afconfig.merge_configs(config, self._overrides)

        self._data.config = config

        self._data.expire_at = datetime.datetime.now() + datetime.timedelta(
            seconds=self.ttl_seconds)

    @property
    def config(self):
        """Loads config data from json file and caches in thread local,
        with expiration
        """
        if not hasattr(self._data, 'config'):
            tornado.log.gen_log.debug("Initial load of config from file")
            self._load_config()

        elif self._data.expire_at < datetime.datetime.now():
            tornado.log.gen_log.debug(f"Cache expired ({self._data.expire_at} vs. {datetime.datetime.now()}) - reloading from file")
            self._load_config()

        return self._data.config

def get(*args):
    return copy.deepcopy(afconfig.get_config_value(
        ConfigManagerSingleton().config, *args))
