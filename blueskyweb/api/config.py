
import blueskyconfig
from . import RequestHandlerBase

##
## Domains
##

KM_PER_DEG_LAT = 111

class ConfigDefaults(RequestHandlerBase):

    def get(self, api_version):
        self.write(blueskyconfig.ConfigManagerSingleton().config)
