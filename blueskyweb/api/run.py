"""blueskyweb.api.run"""

__author__ = "Joel Dubowy"
__copyright__ = "Copyright 2015, AirFire, PNW, USFS"

import datetime
import json
import logging

from fastapi import APIRouter, HTTPException, Request

from blueskymongo.client import RunStatuses
from blueskyweb.lib.runs.execute import BlueSkyRunExecutor, ExecuteMode
from blueskyweb.lib.runs.output import BlueSkyRunOutput
from . import (
    get_boolean_arg, get_datetime_arg,
    make_json_response, DataCollector
)

logger = logging.getLogger(__name__)
router = APIRouter()

__all__ = ['router']

###
### Run execution
###


@router.post("/api/v{api_version}/run/{mode}/{archive_id}")
@router.post("/api/v{api_version}/run/{mode}/{archive_id}/")
@router.post("/api/v{api_version}/run/{mode}")
@router.post("/api/v{api_version}/run/{mode}/")
async def run_execute(api_version: str, mode: str, request: Request,
        archive_id: str = None):
    body = await request.body()
    if not body:
        raise HTTPException(status_code=400, detail='empty post data')

    request_body = body.decode()
    logger.debug("Execute API request data: %s", request_body[:100])
    try:
        data = json.loads(request_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail='Invalid JSON post data')

    settings = request.app.state.settings

    hysplit_query_params = {
        'dispersion_speed': request.query_params.get('dispersion_speed'),
        'grid_resolution': request.query_params.get('grid_resolution'),
        'number_of_particles': request.query_params.get('number_of_particles'),
        'grid_size': _get_float_param(request, 'grid_size')
    }
    fuelbeds_query_params = {
        'fccs_resolution': request.query_params.get('fccs_resolution'),
    }

    collector = DataCollector()

    def handle_error(status: int, msg: str, exception=None):
        if exception:
            logger.error('Exception: %s', exception)
        raise HTTPException(status_code=status, detail=msg)

    executor = BlueSkyRunExecutor(api_version, mode, archive_id,
        handle_error, collector, settings, hysplit_query_params,
        fuelbeds_query_params)

    scheduleFor = get_datetime_arg(request, 'schedule_for', None)
    logger.info("schedule_for: %s", scheduleFor)

    execute_mode = (ExecuteMode.ASYNC if (
        request.query_params.get('_a') is not None or scheduleFor) else None)

    await executor.execute(data, execute_mode=execute_mode, scheduleFor=scheduleFor)

    data = collector.data
    logger.debug("Execute API response data: %s", data)

    status_code = 400 if (isinstance(data, dict) and 'error' in data) else 200
    verbose = get_boolean_arg(request, 'verbose')
    return make_json_response(data, verbose=verbose, status_code=status_code)


def _get_float_param(request: Request, key: str):
    val = request.query_params.get(key)
    if val is not None:
        try:
            return float(val)
        except ValueError:
            raise HTTPException(status_code=400,
                detail=f"Invalid float value '{val}' for query arg {key}")
    return None


###
### Run status helpers
###

RUN_STATUS_VERBOSE_FIELDS = ('output_dir', 'modules', 'server', 'export', 'fires')
AVERAGE_RUN_TIME_IN_SECONDS = 360


async def _process_run(run, mongo_db, raw=False):
    if not raw:
        if 'queue' in run:
            position = await mongo_db.get_queue_position(run)
            run['queue'] = {
                'name': run['queue'],
                'position': position
            }

        run['status'] = sorted(run.pop('history'), key=lambda e: e['ts'])[-1]
        run['complete'] = (run['status']['status']
            in (RunStatuses.Completed, RunStatuses.Failed))

        if 'percent' not in run:
            if (run['status']['status'] in
                    (RunStatuses.Enqueued, RunStatuses.Dequeued)):
                run['percent'] = 0
            elif (run['status']['status'] in
                    (RunStatuses.Completed, RunStatuses.Failed)):
                run['percent'] = 100
            elif run['status']['status'] == RunStatuses.ProcessingOutput:
                run['percent'] = 99  # HACK
            else:  # RunStatuses.Running
                _estimate_percent_for_running(run)

        for k in RUN_STATUS_VERBOSE_FIELDS:
            run.pop(k, None)

    return run


def _estimate_percent_for_running(run):
    try:
        i = datetime.datetime.strptime(run['initiated_at'], "%Y-%m-%dT%H:%M:%SZ")
        n = datetime.datetime.utcnow()
        p = int(100 * ((n - i).seconds / AVERAGE_RUN_TIME_IN_SECONDS))
        run['percent'] = min(98, max(1, p))
    except:
        run['percent'] = 50  # HACK


###
### Run status routes
###

@router.get("/api/v{api_version}/runs/stats/monthly")
@router.get("/api/v{api_version}/runs/stats/monthly/")
async def run_stats_monthly(api_version: str, request: Request):
    settings = request.app.state.settings
    run_id = request.query_params.get('run_id')
    monthly = await settings['mongo_db'].run_counts_by_month(run_id=run_id)
    verbose = get_boolean_arg(request, 'verbose')
    return make_json_response({'monthly': monthly}, verbose=verbose)


@router.get("/api/v{api_version}/runs/stats/daily")
@router.get("/api/v{api_version}/runs/stats/daily/")
async def run_stats_daily(api_version: str, request: Request):
    settings = request.app.state.settings
    run_id = request.query_params.get('run_id')
    daily = await settings['mongo_db'].run_counts_by_day(run_id=run_id)
    verbose = get_boolean_arg(request, 'verbose')
    return make_json_response({'daily': daily}, verbose=verbose)


@router.get("/api/v{api_version}/runs")
@router.get("/api/v{api_version}/runs/")
async def runs_info(api_version: str, request: Request):
    settings = request.app.state.settings
    limit = min(int(request.query_params.get('limit', 10)), 25)
    offset = int(request.query_params.get('offset', 0))
    run_id = request.query_params.get('run_id')
    queue = request.query_params.get('queue')
    raw = get_boolean_arg(request, 'raw')
    verbose = get_boolean_arg(request, 'verbose')

    runs, total_count = await settings['mongo_db'].find_runs(
        status=None, limit=limit, offset=offset, run_id=run_id, queue=queue)
    for run in runs:
        await _process_run(run, settings['mongo_db'], raw=raw)

    return make_json_response({
        "runs": runs,
        "count": len(runs),
        "limit": limit,
        "offset": offset,
        "total": total_count
    }, verbose=verbose)


@router.get("/api/v{api_version}/runs/{run_id}/output")
@router.get("/api/v{api_version}/runs/{run_id}/output/")
@router.get("/api/v{api_version}/run/{run_id}/output")
@router.get("/api/v{api_version}/run/{run_id}/output/")
async def run_output(api_version: str, run_id: str, request: Request):
    settings = request.app.state.settings
    collector = DataCollector()

    def handle_error(status: int, msg: str, exception=None):
        if exception:
            logger.error('Exception: %s', exception)
        raise HTTPException(status_code=status, detail=msg)

    await BlueSkyRunOutput(api_version, settings['mongo_db'],
        handle_error, collector).process(run_id)

    verbose = get_boolean_arg(request, 'verbose')
    return make_json_response(collector.data, verbose=verbose)


@router.get("/api/v{api_version}/run/{run_id}/status")
@router.get("/api/v{api_version}/run/{run_id}/status/")
async def run_status_compat(api_version: str, run_id: str, request: Request):
    """Backwards-compatible endpoint: /run/{run_id}/status"""
    return await _get_run_status(api_version, run_id, request)


@router.get("/api/v{api_version}/runs/{identifier}")
@router.get("/api/v{api_version}/runs/{identifier}/")
async def runs_by_identifier(api_version: str, identifier: str, request: Request):
    """Handles both /runs/{status} (list by status) and /runs/{run_id} (single run)."""
    if identifier in RunStatuses.statuses:
        return await _list_runs_by_status(api_version, identifier, request)
    else:
        return await _get_run_status(api_version, identifier, request)


async def _list_runs_by_status(api_version: str, status: str, request: Request):
    settings = request.app.state.settings
    limit = min(int(request.query_params.get('limit', 10)), 25)
    offset = int(request.query_params.get('offset', 0))
    run_id = request.query_params.get('run_id')
    queue = request.query_params.get('queue')
    raw = get_boolean_arg(request, 'raw')
    verbose = get_boolean_arg(request, 'verbose')

    runs, total_count = await settings['mongo_db'].find_runs(
        status=status, limit=limit, offset=offset, run_id=run_id, queue=queue)
    for run in runs:
        await _process_run(run, settings['mongo_db'], raw=raw)

    return make_json_response({
        "runs": runs,
        "count": len(runs),
        "limit": limit,
        "offset": offset,
        "total": total_count
    }, verbose=verbose)


async def _get_run_status(api_version: str, run_id: str, request: Request):
    settings = request.app.state.settings
    run = await settings['mongo_db'].find_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run doesn't exist")
    raw = get_boolean_arg(request, 'raw')
    await _process_run(run, settings['mongo_db'], raw=raw)
    verbose = get_boolean_arg(request, 'verbose')
    return make_json_response(run, verbose=verbose)
