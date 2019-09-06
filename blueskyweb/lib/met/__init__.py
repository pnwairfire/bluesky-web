"""blueskyweb.lib.met"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

from . import db

# The above import supports calling met.db after importing the met
# subpackage, but we don't want 'db' to pollute the global
# namespace if * is imported from blueskyweb.lib.met
__all__ = []
