"""blueskyweb.api"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import datetime
import json

import tornado.web

class RequestHandlerBase(tornado.web.RequestHandler):

    VERBOSE_FIELDS = (
        # The following list excludes "fires", "summary",
        # "run_id", and "bluesky_versoin"
        "counts", "processing", "run_config",
        "runtime", "today", "version_info",
    )

    def write(self, val):
        """Overrides super's write in order to sort keys
        """
        if hasattr(val, 'keys'):
            if not self.get_boolean_arg('verbose'):
                for k in self.VERBOSE_FIELDS:
                    val.pop(k, None)
            val = json.dumps(val, sort_keys=True)
            # we need to explicitly set content type to application/json,
            # because calling super's write with a string value will result
            # in it being set to text
            self.set_header('Content-Type', 'application/json')
        super().write(val)

    ##
    ## Query Arg parsing
    ##

    def get_boolean_arg(self, key):
        val = self.get_query_argument(key, None)
        if val is not None:
            orig_val = val # for error message
            val = val.lower()
            if val in ('true', 'yes', 'y', '1'):
                val = True
            elif val in ('false', 'no', 'n', '0'):
                val = False
            else:
                self._raise_error(400, "Invalid boolean value '{}' "
                    "for query arg {}".format(orig_val, key))
        return val

    def _get_numerical_arg(self, key, default, value_type):
        val = self.get_query_argument(key, None)
        if val is not None:
            try:
                return value_type(val)
            except ValueError as e:
                raise self._raise_error(400,
                    "Invalid {} value '{}' for query arg {}".format(
                    'integer' if value_type is int else 'float', val, key))
        return default


    def get_integer_arg(self, key, default=None):
        return self._get_numerical_arg(key, default, int)

    def get_float_arg(self, key, default=None):
        return self._get_numerical_arg(key, default, float)


    DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

    def get_datetime_arg(self, key, default=None):
        val = self.get_query_argument(key, None)
        tornado.log.gen_log.error('%s: %s', key, val)
        if val is not None:
            try:
                # parse the datetime and convert to UTC
                d = datetime.datetime.strptime(val, self.DATETIME_FORMAT)
                t = d.utctimetuple()[0:6]
                return datetime.datetime(*t)
            except ValueError as e:
                self._raise_error(400, "Invalid datetime value '{}' "
                    "for query arg {}. Use format {}".format(
                        val, key, self.DATETIME_FORMAT))
        return val


    ##
    ## Errors
    ##

    def _raise_error(self, status, msg, exception=None):
        self.set_status(status, msg)
        self.write({"error": {"message": msg}})
        if exception:
            tornado.log.gen_log.error('Exception: %s', exception)
        raise tornado.web.Finish()
