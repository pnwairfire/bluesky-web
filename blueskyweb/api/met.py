"""blueskyweb.api.met

Notes:
 - API version is ignored by the met APIs
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import datetime
import json
import re

import tornado.web

import blueskyconfig
from blueskyweb.lib import met
from . import RequestHandlerBase

##
## Domains
##

KM_PER_DEG_LAT = 111

class DomainInfo(RequestHandlerBase):

    def _marshall(self, domain_id):
        grid_config = met.db.DOMAINS[domain_id]['grid']
        r = {
            "id": domain_id,
            "boundary": grid_config['boundary'],
            "grid_size_options": grid_config['grid_size_options']
        }
        r['resolution_km'] = grid_config['spacing']
        if grid_config['projection'] == 'LatLon':
            # This uses N/S resolution, which will be different E/W resolution
            # TODO: Is this appropriate
            r['resolution_km'] *= KM_PER_DEG_LAT
        return r

    def get(self, api_version, domain_id=None):
        if domain_id:
            if domain_id not in met.db.DOMAINS:
                self._raise_error(404, "Domain does not exist")
            else:
                self.write({'domain': self._marshall(domain_id)})
        else:
            self.write({'domains': [self._marshall(d) for d in met.db.DOMAINS]})


##
## Archives
##

ARCHIVES = blueskyconfig.get('archives')

class MetArchiveBaseHander(RequestHandlerBase):

    def __init__(self, *args, **kwargs):
        super(MetArchiveBaseHander, self).__init__(*args, **kwargs)
        self.met_archives_db = met.db.MetArchiveDB(self.settings['mongodb_url'])

class MetArchivesInfo(MetArchiveBaseHander):

    async def _marshall(self, archive_group, archive_id):
        r = dict(ARCHIVES[archive_group][archive_id], id=archive_id,
            group=archive_group)
        availability = await self.met_archives_db.get_availability(archive_id)
        r.update(availability)
        return r


    def write_archives(self, archives):
        available = self.get_boolean_arg('available')
        if available is not None:
            if available:
                archives = [a for a in archives if a['begin'] and a['end']]
            else:
                archives = [a for a in archives if not a['begin'] or not a['end']]
        self.write({"archives": archives})

    async def get(self, api_version, identifier=None):
        if not identifier:
            # Note: 'await' expressions in comprehensions are not supported
            archives = []
            for archive_group in ARCHIVES:
                for archive_id in ARCHIVES[archive_group]:
                    archives.append(await self._marshall(archive_group, archive_id))
            self.write_archives(archives)

        elif identifier in ARCHIVES:
            archives = []
            for archive_id in ARCHIVES[identifier]:
                archives.append(await self._marshall(identifier, archive_id))
            self.write_archives(archives)

        else:
            for archive_group in ARCHIVES:
                if identifier in ARCHIVES[archive_group]:
                    self.write({"archive": await self._marshall(archive_group, identifier)})
                    break
            else:
                self._raise_error(404, "Archive does not exist")


class MetArchiveAvailability(MetArchiveBaseHander):

    DATE_MATCHER = re.compile(
        '^(?P<year>[0-9]{4})-?(?P<month>[0-9]{2})-?(?P<day>[0-9]{2})$')

    async def get(self, api_version, archive_id=None, date_str=None):
        # archive_id and date will always be defined
        m = self.DATE_MATCHER.match(date_str)
        if not m:
            self._raise_error(400, "Invalid date: {}".format(date_str))
        date_obj = datetime.date(int(m.group('year')), int(m.group('month')),
            int(m.group('day')))

        try:
            data = await self.met_archives_db.check_availability(
                archive_id, date_obj, self.get_date_range())
            self.write(data)
        except met.db.InvalidArchiveError:
            self._raise_error(404, "Archive does not exist")

    DEFAUL_DATE_RANGE = 3

    def get_date_range(self):
        try:
            date_range = self.get_argument('date_range',
                self.DEFAUL_DATE_RANGE)
            date_range = int(date_range)
        except ValueError as e:
            msg = "Invalid value for date_range: '{}'".format(date_range)
            self._raise_error(400, msg)

        if date_range < 1:
            msg = "date_range must be greater than or equal to 1"
            self._raise_error(400, msg)

        return date_range
