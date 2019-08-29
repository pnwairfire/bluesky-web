"""blueskyweb.api"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import tornado.web

class RequestHandlerBase(tornado.web.RequestHandler):

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

    ##
    ## Errors
    ##

    def _raise_error(self, status, msg, exception=None):
        self.set_status(status, msg)
        self.write({"error": msg})
        if exception:
            tornado.log.gen_log.error('Exception: %s', exception)
        raise tornado.web.Finish()
