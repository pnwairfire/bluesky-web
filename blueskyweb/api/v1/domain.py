"""blueskyweb.api.v1.domain"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import datetime
import json

import tornado.web

from blueskyweb.lib import domains

class DomainBaseHander(tornado.web.RequestHandler):

    def __init__(self, *args, **kwargs):
        super(DomainBaseHander, self).__init__(*args, **kwargs)
        self.domains_db = domains.DomainDB(self.settings['mongodb_url'])

class DomainInfo(DomainBaseHander):

    async def get(self, domain_id=None):
        data = await self.domains_db.find(domain_id=domain_id)

        if domain_id:
            if not data:
                self.set_status(404, "Domain does not exist")
            else:
                self.write(data)
        else:
            self.write({"domains": data})

class DomainAvailableDates(DomainBaseHander):

    async def get(self, domain_id=None):
        data = await self.domains_db.find(domain_id=domain_id)

        if domain_id:
            if not data:
                self.set_status(404, "Domain does not exist")
            else:
                self.write({"dates":data[domain_id]["dates"]})
        else:
            self.write({
                "dates": {d: data[d]['dates'] for d in data}
            })
