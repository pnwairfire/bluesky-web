"""blueskyweb.api.v1"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import tornado.web

class RequestHandlerBase(tornado.web.RequestHandler):

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
                raise tornado.web.HTTPError(status_code=400,
                    log_message="Invalid boolean value '{}' "
                    "for query arg {}".format(orig_val, key))
        return val
