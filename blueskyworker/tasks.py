import getpass
import json
import logging
import re
import os
import tarfile
import time
import uuid
from io import BytesIO
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

##
## Public Job Interface
##

class BlueSkyJobError(RuntimeError):
    pass

@app.task
def run_bluesky(data, bluesky_docker_image, capture_output=False):
    tornado.log.gen_log.INFO("Running %s from queue %s",
        data['run_id'], queue_name)

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

    return _run_bluesky(input_data, bluesky_docker_image,
        input_data_json=input_data_json)


##
## Launching process
##


def _run_bluesky(input_data, bluesky_docker_image, input_data_json=None,
        capture_output=False):
    """
    kwargs:
     - input_data_json -- already dumped json string, to avoid repeated dump;
        not necessarily set by outside clients of this code
     - capture_output -- whether or not to capture the stdout and stderr; only
        set to True by outside clients of this code
    """
    run_id = input_data.get('run_id') or str(uuid.uuid1()).replace('-','')
    input_data['run_id'] = run_id # in case it was just generated
    container_name = 'bsp-playground-{}'.format(run_id)
    bsp_cmd = 'bsp -i /tmp/fires.json -o /tmp/output.json'
    volumes_dict = _get_volumes_dict(input_data)
    input_data_json = input_data_json or json.dumps(input_data)
    tornado.log.gen_log.info("bsp docker command (as user %s): %s",
        getpass.getuser(), ' '.join(bsp_docker_cmd))

    client = docker.from_env()
    container = client.containers.create(bluesky_docker_image, bsp_cmd,
        name=container_name, volumes=volumes_dict)
    try:
        # TODO: if not capturing output,
        #     - write logs to file, in dispersion output dir or where
        #       dispersioj ouput would be if dispersion run
        #     - write to files next to log file.
        #   else:
        #     - write logs to dev null?
        #     - capture and return output json

        # return client.containers.run(bluesky_docker_image, bsp_cmd,
        #     remove=True, name=container_name, volumes=volumes_dict,
        #     tty=True)
        _create_input_file(input_data_json, container)
        container.start()
        docker.APIClient().wait(container.id)
        if capture_output:
            return _get_output

    except Exception as e:
        raise BlueSkyJobError(str(e))

    finally:
        container.remove()

def _create_input_file(input_data_json, container):
    tar_stream = BytesIO()
    tar_file = tarfile.TarFile(fileobj=tar_stream, mode='w')
    tar_file_data = input_data_json.encode('utf8')
    tar_info = tarfile.TarInfo(name='fires.json')
    tar_info.size = len(tar_file_data)
    tar_info.mtime = time.time()
    #tar_info.mode = 0600
    tar_file.addfile(tar_info, BytesIO(tar_file_data))
    tar_file.close()
    tar_stream.seek(0)
    container.put_archive(path='/tmp', data=pw_tarstream)

def _get_output():
    # TODO: figure out how to extract output from tar stream,
    #    to avoid having to write to file first
    response = container.get_archive('/tmp/output.json')[0]
    tarfilename = '/tmp/' + str(uuid.uuid1()) + '.tar'
    with open(tarfilename, 'wb') as f:
        #f.write(response.read())
        for chunk in response.read_chunked():
            f.write(chunk)

    output = None
    with tarfile.open(tarfilename) as t:
        output = t.extractfile('output.json').read()

    # TODO: remove tarfile

    return output


##
## Mounting dirs
##

TRAILING_RUN_ID_RE = re.compile('/{run_id}/?$')
def _get_volumes_dict(input_data):
    """ Only mount the host os dirs that are needed
    """
    dirs_to_mount =  (
        _get_load_dirs(input_data) +
        _get_met_dirs(input_data) +
        _get_output_and_working_dirs(input_data)
    )
    dirs_to_mount = list(set([m for m in dirs_to_mount if m]))
    volumes_dict = {}
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

            volumes_dict[d] = {
                'bind': d,
                'mode': 'rw'
            }
    return volumes_dict

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
    # TODO: look in input_data > met > files, in case findmetdata
    #   was bypassed and met files were specified manually
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
