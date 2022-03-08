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

        # __init__ will be called each time __new__ is called. So, we need to
        # keep track of initialization to abort subsequent reinitialization
        if not hasattr(self, '_initialized'):
            self._data = thread_local_data
            self._initialized = True

    # this should never be used, but could if 'cache_ttl_minutes' is
    # accidentally deleted from the config defaults
    _DEFAULT_TTL = 60

    def _load_config_from_file(self):
        with open(self._config_json_file) as f:
            self._data.config = json.loads(f.read())
            self._data.expire_at = datetime.datetime.now() + datetime.timedelta(
                minutes=self._data.config.get('cache_ttl_minutes')
                    or self._DEFAULT_TTL)


    @property
    def config(self):
        """Loads config data from json file and caches in thread local,
        with expiration
        """
        if not hasattr(self._data, 'config'):
            tornado.log.gen_log.debug("Initial load of config from file")
            self._load_config_from_file()
        elif self._data.expire_at > datetime.datetime.now():
            tornado.log.gen_log.debug("Cache expired - reloading from file")
            self._load_config_from_file()

        return self._data.config

def apply_overrides(overrides):
    if overrides:
        # merges in-place
        afconfig.merge_configs(ConfigManagerSingleton().config, overrides)

def get(*args):
    return copy.deepcopy(afconfig.get_config_value(
        ConfigManagerSingleton().config, *args))
