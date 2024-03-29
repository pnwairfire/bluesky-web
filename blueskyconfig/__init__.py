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
    def __init__(self, config_json_file=DEFAULT_CONFIG_JSON_FILE):
        self._config_json_file = config_json_file

        # store overrides
        self._overrides = None

        # __init__ will be called each time __new__ is called. So, we need to
        # keep track of initialization to abort subsequent reinitialization
        if not hasattr(self, '_initialized'):
            self._data = thread_local_data
            self._initialized = True

    # this should never be used, but could if 'cache_ttl_minutes' is
    # accidentally deleted from the config defaults
    _DEFAULT_TTL_SECONDS = 60

    @property
    def overrides(self):
        return self._overrides

    @overrides.setter
    def overrides(self, overrides):
        self._overrides = overrides

    @property
    def ttl_minutes(self):
        if hasattr(self._data, 'config'):
            ttl = self._data.config.get('cache_ttl_minutes')
            if ttl is not None:
                return ttl * 60

            ttl = self._data.config.get('cache_ttl_seconds')
            if ttl is not None:
                return ttl

        return self._DEFAULT_TTL_SECONDS

    def _load_config_from_file(self):
        with open(self._config_json_file) as f:
            config = json.loads(f.read())
            if self.overrides:
                # merges in-place
                afconfig.merge_configs(config, self.overrides)

            self._data.config = config

            ttl = self._data.config.get('cache_ttl_minutes')
            self._data.expire_at = datetime.datetime.now() + datetime.timedelta(
                seconds=self.ttl_minutes)

    @property
    def config(self):
        """Loads config data from json file and caches in thread local,
        with expiration
        """
        if not hasattr(self._data, 'config'):
            tornado.log.gen_log.debug("Initial load of config from file")
            self._load_config_from_file()
        elif self._data.expire_at < datetime.datetime.now():
            tornado.log.gen_log.debug(f"Cache expired ({self._data.expire_at} vs. {datetime.datetime.now()}) - reloading from file")
            self._load_config_from_file()

        return self._data.config

def apply_overrides(overrides):
    if overrides:
        ConfigManagerSingleton.overrides = overrides

def get(*args):
    return copy.deepcopy(afconfig.get_config_value(
        ConfigManagerSingleton().config, *args))
