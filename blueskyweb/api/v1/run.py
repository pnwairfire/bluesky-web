"""blueskyweb.api.v1.run"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import tornado.web

from bluesky.marshal import Blueskyv4_0To4_1

from blueskyweb.lib.api.run import (
    RunExecuteBase, RunStatus, RunOutput, RunsInfo
)

class RunExecute(RunExecuteBase):
    @tornado.web.asynchronous
    async def post(self, mode=None, archive_id=None):
        super().post(mode=mode, archive_id=archive_id)

    @property
    def fires_key(self):
        return "fire_information"

    def _pre_process(self, data):
        fires = data.pop('fire_information')
        data['fires'] = Blueskyv4_0To4_1().marshal(fires)
