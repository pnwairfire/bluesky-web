"""blueskyweb.api"""

__author__ = "Joel Dubowy"
__copyright__ = "Copyright 2015, AirFire, PNW, USFS"

import datetime
import json
import logging

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

VERBOSE_FIELDS = (
    # The following list excludes "fires", "summary",
    # "run_id", and "bluesky_version"
    "counts", "processing", "run_config",
    "runtime", "today", "version_info",
)

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def get_boolean_arg(request: Request, key: str):
    val = request.query_params.get(key)
    if val is not None:
        orig_val = val
        val = val.lower()
        if val in ('true', 'yes', 'y', '1'):
            return True
        elif val in ('false', 'no', 'n', '0'):
            return False
        else:
            raise HTTPException(status_code=400,
                detail=f"Invalid boolean value '{orig_val}' for query arg {key}")
    return val


def _get_numerical_arg(request: Request, key: str, default, value_type):
    val = request.query_params.get(key)
    if val is not None:
        try:
            return value_type(val)
        except ValueError:
            type_name = 'integer' if value_type is int else 'float'
            raise HTTPException(status_code=400,
                detail=f"Invalid {type_name} value '{val}' for query arg {key}")
    return default


def get_integer_arg(request: Request, key: str, default=None):
    return _get_numerical_arg(request, key, default, int)


def get_float_arg(request: Request, key: str, default=None):
    return _get_numerical_arg(request, key, default, float)


def get_datetime_arg(request: Request, key: str, default=None):
    val = request.query_params.get(key)
    if val is not None:
        try:
            d = datetime.datetime.strptime(val, DATETIME_FORMAT)
            t = d.utctimetuple()[0:6]
            return datetime.datetime(*t)
        except ValueError:
            raise HTTPException(status_code=400,
                detail=f"Invalid datetime value '{val}' for query arg {key}. Use format {DATETIME_FORMAT}")
    return default


def raise_error(status: int, msg: str, exception=None):
    if exception:
        logger.error('Exception: %s', exception)
    raise HTTPException(status_code=status, detail=msg)


def make_json_response(val, verbose=False, status_code=200):
    """Create a sorted JSON response, optionally stripping verbose fields."""
    if hasattr(val, 'keys'):
        if not verbose:
            for k in VERBOSE_FIELDS:
                val.pop(k, None)
        content = json.loads(json.dumps(val, sort_keys=True))
        return JSONResponse(content=content, status_code=status_code)
    return val


class DataCollector:
    """Collects data written to it via write(), to be returned as API response."""

    def __init__(self):
        self.data = None
        self.status_code = 200

    def write(self, val):
        if isinstance(val, dict) and 'error' in val:
            self.status_code = 400
        self.data = val
