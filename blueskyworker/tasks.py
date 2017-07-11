import getpass
import json
import logging
import re
import os
import subprocess
import uuid
from urllib.parse import urlparse

import tornado.log
from celery import Celery

MONGODB_URL = os.environ.get('MONGODB_URL') or 'mongodb://localhost:27018/blueskyweb'
app = Celery('blueskyworker.tasks', broker=MONGODB_URL)

parse_object = urlparse(MONGODB_URL)
app.conf.update(
    result_backend='mongodb',
    mongodb_backend_settings={
        "host": parse_object.hostname,
        "port": parse_object.port or 27017,
        "user": parse_object.username,
        "password": parse_object.password,
        "database": parse_object.path.strip('/'),
        "taskmeta_collection": "stock_taskmeta_collection"
    }
)

DEFAULT_BSP_VERSION = "v2.4.3"

##
## Public Job Interface
##

@app.task
def run_bluesky(data, capture_output=False,
        bsp_version=DEFAULT_BSP_VERSION):
    tornado.log.gen_log.INFO("Running %s from queue %s", data['run_id'], queue_name)

    # load input_data if it's json (and 'cache' json string to dump to file
    #   in call to bsp, below)
    input_data_json = None
    if hasattr(input_data, 'lower'):
        input_data_json = input_data
        input_data = json.loads(input_data)

    # TODO:
    #   - store server info in mongodb (under run_id key)
    #   - stores status (start, finish, anything else) in mongodb (also under
    #      run_id key)
    #      (maybe run each module separately, so that more granular status
    #       can be saved in mongodb; or have this method parse logs as bsp
    #       is running

    return _run_bluesky(input_data, input_data_json=input_data_json,
        bsp_version=bsp_version)


##
## Launching process
##


def _run_bluesky(input_data, input_data_json=None, capture_output=False,
        bsp_version=DEFAULT_BSP_VERSION):
    """
    kwargs:
     - input_data_json -- already dumped json string, to avoid repeated dump; not
        necessarily set by outside clients of this code
     - capture_output -- whether or not to capture the stdout and stderr; only
        set to True by outside clients of this code
     - bsp_version -- alternate version of bluesky package to use

    Note: bsp_version is a kwarg to both `launch_bsf` and `_run_bluesky_bsf`
      because `_run_bluesky_bsf` is called directly by blueskyweb when run in process
    """
    run_id = input_data.get('run_id') or str(uuid.uuid1()).replace('-','')
    docker_name = 'bsp-{}'.format(run_id)
    bsp_docker_cmd = [
        'docker', 'run', '--rm', '-i', # '-i' lets us pipe input
        '--name', docker_name
    ]

    _add_mount_dirs(input_data, bsp_docker_cmd)

    bsp_docker_cmd.extend([
        'pnwairfire/bluesky:{}'.format(
            # Just in case `bsp_version` was explicitly
            # set to `None` in call to this function
            bsp_version or DEFAULT_BSP_VERSION), 'bsp'
    ])

    input_data_json = input_data_json or json.dumps(input_data)
    stdout_data, stderr_data = _execute(
        input_data_json, bsp_docker_cmd, capture_output)
    # _clean_up(docker_name)
    return stdout_data, stderr_data

def _execute(input_data_json, bsp_docker_cmd, capture_output):
    tornado.log.gen_log.info("bsp docker command (as user %s): %s",
        getpass.getuser(), ' '.join(bsp_docker_cmd))
    kwargs = dict(stdin=subprocess.PIPE)
    if capture_output:
        kwargs.update(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # else, p.communicate will simply return None for stdout and stderr
    p = subprocess.Popen(bsp_docker_cmd, **kwargs)
    return p.communicate(input=input_data_json.encode())

##
## Cleaning up
##

# def _clean_up(docker_name):
#     subprocess.call(['docker', 'stop', docker_name])

##
## Mounting dirs
##

TRAILING_RUN_ID_RE = re.compile('/{run_id}/?$')
def _add_mount_dirs(input_data, bsp_docker_cmd):
    """ Only mount the host os dirs that are needed
    """
    dirs_to_mount =  (
        _get_load_dirs(input_data) +
        _get_met_dirs(input_data) +
        _get_output_and_working_dirs(input_data)
    )
    dirs_to_mount = list(set([m for m in dirs_to_mount if m]))
    if dirs_to_mount:
        for d in dirs_to_mount:
            # remove trailing '/{run_id}' from mount point
            d = TRAILING_RUN_ID_RE.sub('/', d)
            # try to make dir if it doesn't exist
            if not os.path.exists(d):
                try:
                    os.makedirs(d)
                except OSError: # 'Permission denied'
                    # this doesn't necessarily mean the run
                    # will fail, so swallow exception
                    pass

            # TODO: create dir?
            bsp_docker_cmd.extend([
                '-v', "{d}:{d}".format(d=d)
            ])

def _get_load_dirs(input_data):
    load_dirs = []
    sources = _get_val(input_data, "config", "load", "sources")
    if sources:
        for s in sources:
            for f in ('file', 'events_file'):
                if s.get(f):
                    load_dirs.append(os.path.split(s[f])[0])
    return load_dirs

def _get_met_dirs(input_data):
    # met dirs
    met_dirs = [
        _get_val(input_data, 'config', 'findmetdata', "met_root_dir"),
    ]
    # TODO: look in input_data > met > files, in case findmetdata was bypassed
    #   and met files were specified manually
    return met_dirs

def _get_output_and_working_dirs(input_data):
    # distination dirs
    dest_dirs = [
        _get_val(input_data, "config", "dispersion", "output_dir"),
        _get_val(input_data, "config", "dispersion", "working_dir"),
        _get_val(input_data, 'config', 'visualization',  'hysplit', 'output_dir'),
        _get_val(input_data, "config", "export", "localsave", "dest_dir")
    ]
    return dest_dirs

def _get_val(input_data, *args):
    if isinstance(input_data, dict):
        v = input_data.get(args[0])
        if len(args) == 1:
            return v
        return _get_val(v, *args[1:])
