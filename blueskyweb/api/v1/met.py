"""blueskyweb.api.v1.domain"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import datetime
import json
import re

import tornado.web

import blueskyconfig
from blueskyweb.lib import met

##
## Domains
##

KM_PER_DEG_LAT = 111

class DomainInfo(tornado.web.RequestHandler):

    def _marshall(self, domain_id):
        grid_config = met.DOMAINS[domain_id]['grid']
        r = {
            id: domain_id,
            boundary: grid_config['boundary']
        }
        r['resolution_km'] = grid_config['spacing']
        if grid_config['projection'] == 'LatLon':
            # This uses N/S resolution, which will be different E/W resolution
            # TODO: Is this appropriate
            r['resolution_km'] *= KM_PER_DEG_LAT

    def get(self, domain_id=None):
        if domain_id:
            if domains_id not in met.DOMAINS:
                self.set_status(404, "Domain does not exist")
            else:
                self.write({"domain_id": self._marshall(domain_id)})
        else:
            self.write({
                "domains": {
                    d: self._marshall(d) for d in met.DOMAINS
                }
            })


##
## Archives
##

ARCHIVES = blueskyconfig.get('archives')

class MetArchiveBaseHander(tornado.web.RequestHandler):

    def __init__(self, *args, **kwargs):
        super(MetArchiveBaseHander, self).__init__(*args, **kwargs)
        self.met_archives_db = met.MetArchiveDB(self.settings['mongodb_url'])

class MetArchivesInfo(MetArchiveBaseHander):

    async def _marshall(self, archive_group, archive_id):
        r = dict(ARCHIVES[archive_group][archive_id], id=archive_id,
            group=archive_group)
        availability = await self.met_archives_db.get_availability(archive_id)
        r.update(availability)
        return r

    async def get(self, identifier):
        if not identifier:
            self.write([
                self._marshall(archive_group, archive_id)
                    for archive_group in ARCHIVES
                    for archive_id in ARCHIVES[archive_group]
            ])

        elif identifier in ARCHIVES:
            self.write([
                self._marshall(identifier, archive_id)
                    for archive_id in ARCHIVES[identifier]
            ])

        else:
            for archive_group in archives:
                if archive_id in archives[archive_group]:
                    self.write(self._marshall(archive_group, archive_id))
                    break
            else:
                self.set_status(404, "Archive does not exist")


class MetArchiveAvailability(MetArchiveBaseHander):

    DATE_MATCHER = re.compile(
        '^(?P<year>[0-9]{4})-?(?P<month>[0-9]{2})-?(?P<day>[0-9]{2})$')

    async def get(self, archive_id=None, date_str=None):
        # archive_id and date will always be defined
        m = self.DATE_MATCHER.match(date_str)
        if not m:
            raise tornado.web.HTTPError(status_code=400,
                log_message="Invalid date: {}".format(date_str))
        date_obj = datetime.date(int(m.group('year')), int(m.group('month')),
            int(m.group('day')))


        try:
            data = await self.met_archives_db.check_availability(
                domain_id, date_obj, self.get_date_range())
            self.write(data)
        except met.InvalidDomainError:
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
