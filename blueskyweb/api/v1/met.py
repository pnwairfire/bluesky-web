"""blueskyweb.api.v1.domain"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import datetime
import json
import re

import tornado.web

import blueskyconfig
from blueskyweb.lib import domains

##
## Static Domain data
##

KM_PER_DEG_LAT = 111
DEG_LAT_PER_KM = 1.0 / KM_PER_DEG_LAT
RADIANS_PER_DEG = math.pi / 180.0
KM_PER_DEG_LNG_AT_EQUATOR = 111.32


class DomainInfo(tornado.web.RequestHandler):

    def _marshall(self, domain_id):
        grid_config = domains.DOMAINS[domain_id]['grid']
        r = {
            id: domain_id,
            boundary: grid_config['boundary']
        }
        r['resolution_km'] = grid_config['spacing']
        if grid_config['projection'] == 'LatLon':
            r['resolution_km'] *=


    def get(self, domain_id=None):
        if domain_id:
            if domains_id not in domains.DOMAINS:
                self.set_status(404, "Domain does not exist")
            else:
                self.write({"domain_id": self._marshall(domain_id)})
        else:
            self.write({
                "domains": {
                    d: self._marshall(d) for d in domains.DOMAINS
                }
            })

##
## DB-based Domain data
##

class ArchiveBaseHander(tornado.web.RequestHandler):

    def __init__(self, *args, **kwargs):
        super(ArchiveBaseHander, self).__init__(*args, **kwargs)
        self.domains_db = domains.DomainDB(self.settings['mongodb_url'])

class ArchivesInfo(ArchiveBaseHander):

    async def

    async def get(self, identifier):
        if identifier in blueskyconfig.get('archives'):
            for


class DomainAvailableDates(ArchiveBaseHander):

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

class DomainAvailableDate(ArchiveBaseHander):

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
            data = await self.domains_db.get_availability(
                domain_id, date_obj, self.get_date_range())
            self.write(data)
        except domains.InvalidDomainError:
            raise tornado.web.HTTPError(status_code=404,
                log_message="Domain does not exist")

    DEFAUL_DATE_RANGE = 3

    def get_date_range(self):
        try:
            date_range = self.get_argument('date_range',
                self.DEFAUL_DATE_RANGE)
            date_range = int(date_range)
        except ValueError as e:
            msg = "Invalid value for date_range: '{}'".format(date_range)
            raise tornado.web.HTTPError(status_code=400, log_message=msg)

        if date_range < 1:
            msg = "date_range must be greater than or equal to 1"
            raise tornado.web.HTTPError(status_code=400, log_message=msg)

        return date_range
