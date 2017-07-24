"""blueskyweb.api.v1.domain"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import datetime
import json
import re

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

class DomainAvailableDate(DomainBaseHander):

    DATE_MATCHER = re.compile(
        '^(?P<year>[0-9]{4})-?(?P<month>[0-9]{2})-?(?P<day>[0-9]{2})$')

    async def get(self, domain_id=None, date_str=None):
        # domain_id and date will always be defined
        m = self.DATE_MATCHER.match(date_str)
        if not m:
            raise tornado.web.HTTPError(status_code=400,
                log_message="Invalid date: {}".format(date_str))
        date_obj = datetime.date(int(m.group('year')), int(m.group('month')),
            int(m.group('day')))

        try:
            data = await self.domains_db.get_availability(domain_id, date_obj)
            self.write(data)
        except domains.InvalidDomainError:
            raise tornado.web.HTTPError(status_code=404,
                log_message="Domain does not exist")
