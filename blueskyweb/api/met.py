"""blueskyweb.api.met

Notes:
 - API version is ignored by the met APIs
"""

__author__ = "Joel Dubowy"
__copyright__ = "Copyright 2015, AirFire, PNW, USFS"

import datetime
import re

from fastapi import APIRouter, HTTPException, Request

import blueskyconfig
from blueskyweb.lib import met
from . import get_boolean_arg, make_json_response

router = APIRouter()

__all__ = ['router']

##
## Domains
##

KM_PER_DEG_LAT = 111


def _marshall_domain(domain_id, domains):
    grid_config = domains[domain_id]['grid']
    r = {
        "id": domain_id,
        "boundary": grid_config['boundary'],
        "grid_size_options": {
            k: f"xy(km): {grid_config['grid_size_options'][k]['x']} x {grid_config['grid_size_options'][k]['y']}"
                for k in grid_config['grid_size_options']
        },
        "grid_size_options_numeric": grid_config['grid_size_options']
    }
    r['resolution_km'] = grid_config['spacing']
    if grid_config['projection'] == 'LatLon':
        r['resolution_km'] *= KM_PER_DEG_LAT
    return r


@router.get("/api/v{api_version}/met/domains")
async def domain_info(api_version: str, request: Request):
    domains = blueskyconfig.get('domains')
    verbose = get_boolean_arg(request, 'verbose')
    return make_json_response({'domains': [_marshall_domain(d, domains) for d in domains]},
        verbose=verbose)


@router.get("/api/v{api_version}/met/domains/{domain_id}")
async def domain_info_by_id(api_version: str, domain_id: str, request: Request):
    domains = blueskyconfig.get('domains')
    if domain_id not in domains:
        raise HTTPException(status_code=404, detail="Domain does not exist")
    verbose = get_boolean_arg(request, 'verbose')
    return make_json_response({'domain': _marshall_domain(domain_id, domains)}, verbose=verbose)


##
## Archives
##


async def _marshall_archive(archive_group, archive_id, archives, met_archives_db):
    r = dict(archives[archive_group][archive_id], id=archive_id, group=archive_group)
    availability = await met_archives_db.get_availability(archive_id)
    r.update(availability)
    return r


def _filter_by_available(archives, available):
    if available is None:
        return archives
    if available:
        return [a for a in archives if a['begin'] and a['end']]
    else:
        return [a for a in archives if not a['begin'] or not a['end']]


@router.get("/api/v{api_version}/met/archives")
async def met_archives_info(api_version: str, request: Request):
    mongodb_url = request.app.state.settings['mongodb_url']
    met_archives_db = met.db.MetArchiveDB(mongodb_url)
    archives = blueskyconfig.get('archives')

    result = []
    for archive_group in archives:
        for archive_id in archives[archive_group]:
            result.append(await _marshall_archive(archive_group, archive_id, archives, met_archives_db))

    available = get_boolean_arg(request, 'available')
    result = _filter_by_available(result, available)

    verbose = get_boolean_arg(request, 'verbose')
    return make_json_response({"archives": result}, verbose=verbose)


@router.get("/api/v{api_version}/met/archives/{identifier}")
async def met_archive_info_by_identifier(api_version: str, identifier: str, request: Request):
    mongodb_url = request.app.state.settings['mongodb_url']
    met_archives_db = met.db.MetArchiveDB(mongodb_url)
    archives = blueskyconfig.get('archives')
    available = get_boolean_arg(request, 'available')
    verbose = get_boolean_arg(request, 'verbose')

    if identifier in archives:
        # It's an archive group
        result = []
        for archive_id in archives[identifier]:
            result.append(await _marshall_archive(identifier, archive_id, archives, met_archives_db))
        result = _filter_by_available(result, available)
        return make_json_response({"archives": result}, verbose=verbose)

    else:
        # Look for a specific archive_id across all groups
        for archive_group in archives:
            if identifier in archives[archive_group]:
                result = await _marshall_archive(archive_group, identifier, archives, met_archives_db)
                return make_json_response({"archive": result}, verbose=verbose)

        raise HTTPException(status_code=404, detail="Archive does not exist")


DATE_MATCHER = re.compile(
    r'^(?P<year>[0-9]{4})-?(?P<month>[0-9]{2})-?(?P<day>[0-9]{2})$')
DEFAULT_DATE_RANGE = 3


@router.get("/api/v{api_version}/met/archives/{archive_id}/{date_str}")
async def met_archive_availability(api_version: str, archive_id: str, date_str: str,
        request: Request):
    mongodb_url = request.app.state.settings['mongodb_url']
    met_archives_db = met.db.MetArchiveDB(mongodb_url)

    m = DATE_MATCHER.match(date_str)
    if not m:
        raise HTTPException(status_code=400, detail=f"Invalid date: {date_str}")
    date_obj = datetime.date(int(m.group('year')), int(m.group('month')),
        int(m.group('day')))

    date_range_str = request.query_params.get('date_range', str(DEFAULT_DATE_RANGE))
    try:
        date_range = int(date_range_str)
    except ValueError:
        raise HTTPException(status_code=400,
            detail=f"Invalid value for date_range: '{date_range_str}'")
    if date_range < 1:
        raise HTTPException(status_code=400,
            detail="date_range must be greater than or equal to 1")

    try:
        data = await met_archives_db.check_availability(archive_id, date_obj, date_range)
        verbose = get_boolean_arg(request, 'verbose')
        return make_json_response(data, verbose=verbose)
    except met.db.InvalidArchiveError:
        raise HTTPException(status_code=404, detail="Archive does not exist")
