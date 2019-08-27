"""blueskyweb.api.v1.run"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

from blueskyweb.lib.api.run import RunExecuterBase

class RunExecuter(RunExecuterBase):
    @tornado.web.asynchronous
    async def post(self, mode=None, archive_id=None):
        super().post(mode=mode, archive_id=archive_id)

    @property
    def fires_key(self):
        return "fire_information"
