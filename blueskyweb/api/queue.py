"""blueskyweb.api.queue"""

import logging

from fastapi import APIRouter, Request

from . import get_boolean_arg, make_json_response

logger = logging.getLogger(__name__)
router = APIRouter()

__all__ = ['router']


@router.get("/api/v{api_version}/queue")
async def queue_info(api_version: str, request: Request):
    # See https://docs.celeryq.dev/en/latest/userguide/workers.html#inspecting-workers
    # Import here to ensure RABBITMQ_URL env var is set before tasks module is imported
    from blueskyworker.tasks import app

    i = app.control.inspect()

    result = {
        "in_queue": prune_worker_set(i.reserved(), prune_enqueud_or_active),
        "executing": prune_worker_set(i.active(), prune_enqueud_or_active),
        "scheduled": prune_worker_set(i.scheduled(), prune_scheduled),
    }
    verbose = get_boolean_arg(request, 'verbose')
    return make_json_response(result, verbose=verbose)


def prune_worker_set(r, prune_func):
    return {w: [prune_func(t) for t in r[w]] for w in r}


def prune_scheduled(task):
    """Active tasks have the following structure.

        ***Note that 'args' and 'kwargs' are strings, but are
        ***expanded here with newlines and spaces fore readability

        {
            'eta': '2023-02-17T19:04:24+00:00',
            'priority': 6,
            'request': {
                'id': 'f4a75267-b91e-4ef3-bc0e-1ee3af128463',
                'name': 'blueskyworker.tasks.run_bluesky',
                'args': "(
                    {
                        'bluesky_version': '4.3.71',
                        'fires': [{...}, {...}],
                        'run_id': 'abc123',
                        'summary': {'fuelbeds': [...]},
                        'modules': ['ecoregion', 'consumption', 'emissions'],
                        'config': {'fuelbeds': {...}, 'emissions': {...}}
                    },
                    '4.2'
                )",
                'kwargs': "{
                    'port': '80',
                    'mongodb_url': 'mongodb://blueskyweb:blueskywebmongopassword@mongo/blueskyweb',
                    'rabbitmq_url': 'amqps://blueskyweb:blueskywebrabbitpassword@rabbit:5671',
                    'log_file': '/var/log/blueskyweb/bluesky-web.log',
                    'output_url_scheme': 'http',
                    'output_url_port': '8886',
                    'output_url_path_prefix': 'bluesky-web-output',
                    'bluesky_log_level': 'DEBUG',
                    'path_prefix': '/bluesky-web',
                    'debug': True,
                    'output_root_dir': '/data/bluesky/output/',
                    'log_level': 10,
                    'autoreload': True,
                    'compiled_template_cache': False,
                    'static_hash_cache': False,
                    'serve_traceback': True
                }",
                'type': 'blueskyworker.tasks.run_bluesky',
                'hostname': 'celery@bluesky-web-worker',
                'time_start': None,
                'acknowledged': False,
                'delivery_info': {
                    'exchange': '',
                    'routing_key': 'no-met',
                    'priority': None,
                    'redelivered': False
                },
                'worker_pid': None
            }
        }

    """
    logger.debug(f"***TASK***: {task}")
    t = {
        "priority": task["priority"],
        "id": task["request"]["id"],
        "type": task["request"]["type"],
    }

    add_request_args(t, task)

    if task.get('eta'):
        t['schedule_for'] = task['eta']

    return t

def prune_enqueud_or_active(task):
    """Active tasks have the following structure.

        ***Note that 'args' and 'kwargs' are strings, but are
        ***expanded here with newlines and spaces fore readability

        {
            'id': '2743d663-e4b5-459e-82e1-eca365f0309d',
            'name': 'blueskyworker.tasks.run_bluesky',
            'args': "(
                {
                    'config': {'emissions': {...},'dispersion': {...},'visualization': {...},'export': {...},'fuelbeds': {...},'consumption': {...},'plumerise': {...},'findmetdata': {...},'extrafiles': {...}},
                    'fires': [{...}, {...}],
                    'run_id': 'test-asynch-request-dispersion-20230217T180122',
                    'modules': ['fuelbeds', 'ecoregion', 'consumption', 'emissions', 'timeprofile', 'plumerise', 'findmetdata', 'extrafiles', 'dispersion', 'visualization', 'export']
                },
                '4.2'
            )",
            'kwargs': "{
                'port': '80', 'mongodb_url': 'mongodb://blueskyweb:blueskywebmongopassword@mongo/blueskyweb',
                'rabbitmq_url': 'amqps://blueskyweb:blueskywebrabbitpassword@rabbit:5671', 'log_file': '/var/log/blueskyweb/bluesky-web.log',
                'output_url_scheme': 'http',
                'output_url_port': '8886',
                'output_url_path_prefix': 'bluesky-web-output',
                'bluesky_log_level': 'DEBUG',
                'path_prefix': '/bluesky-web',
                'debug': True,
                'output_root_dir': '/data/bluesky/output/',
                'log_level': 10,
                'autoreload': True,
                'compiled_template_cache': False,
                'static_hash_cache': False,
                'serve_traceback': True
            }",
            'type': 'blueskyworker.tasks.run_bluesky',
            'hostname': 'celery@bluesky-web-worker',
            'time_start': 3263068.543072896,
            'acknowledged': True,
            'delivery_info': {
                'exchange': '',
                'routing_key': 'pacific_northwest_4-km',
                'priority': None,
                'redelivered': False
            },
            'worker_pid': 14
        }
    """
    t = {
        "id": task["id"],
        "type": task["type"],
    }

    add_request_args(t, task)

    return t

def add_request_args(t, task):
    request_args = task.get("request", {}).get("args") or task.get("args")
    try:
        if isinstance(request_args, str):
            request_args = eval(request_args)

        logger.debug("  api_version: %s", request_args[1])
        logger.debug("  run_id: %s", request_args[0]['run_id'])
        logger.debug("  modules: %s", request_args[0]['modules'])

        t["api_version"] = request_args[1]
        t["run_id"] = request_args[0]['run_id']
        t["modules"] = request_args[0]['modules']

    except Exception as e:
        logger.warning("Failed to parse request args: %s", e)
