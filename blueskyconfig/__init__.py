import json
import os

from .defaults import DEFAULTS as config

# Note: afconfig is installed via afscripting
import afconfig

def apply_overrides(overrides):
    if overrides:
        # merges in-place
        afconfig.merge_configs(config, overrides)

def get(*args):
    return afconfig.get_config_value(config, *args)
