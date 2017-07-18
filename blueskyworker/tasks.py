import docker
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

import ipify
import tornado.log
from celery import Celery

from blueskymongo.client import BlueSkyWebDB

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

IP_ADDRESS = ipify.get_ip()
HOSTNAME = os.environ.get('PUBLIC_HOSTNAME') or IP_ADDRESS

def form_output_url(run_id, **settings):
    scheme = settings.get('output_url_scheme') or 'https'
    port_str = (':' + settings['output_url_port']
        if settings.get('output_url_port') else '')
    prefix = (settings.get('output_url_path_prefix') or '').strip('/')
    return "{}://{}{}/{}/{}".format(
        scheme, HOSTNAME, port_str, prefix, run_id)

##
## Public Job Interface
##

class BlueSkyJobError(RuntimeError):
    pass

@app.task
def run_bluesky(input_data, **settings):
    """
    args:
     - input_data -- bsp input data
    Settings:
     See `_run_bluesky` helpstring for required settings
    """
    db = BlueSkyWebDB(MONGODB_URL)
    db.record_run(input_data['run_id'], 'dequeued', server={"ip": IP_ADDRESS})
    tornado.log.gen_log.info("Running %s from queue %s",
        input_data['run_id'],  '/') # TODO: get queue from job process

    # load input_data if it's json (and 'cache' json string to dump to file
    #   in call to bsp, below)
    input_data_json = None
    if hasattr(input_data, 'lower'):
        input_data_json = input_data
        input_data = json.loads(input_data)

    # TODO: (maybe run each module separately, so that more granular status
    #       can be saved in mongodb; or have this method parse logs as bsp
    #       is running
    return _run_bluesky(input_data, input_data_json=input_data_json, db=db,
        **settings)


##
## Launching process
##

def _run_bluesky(input_data, input_data_json=None, db=None, **settings):
    """
    args:
     - input_data -- bsp input data
    kwargs:
     - input_data_json -- already dumped json string, to avoid repeated dump;
        not necessarily set by outside clients of this code
     - db -- bsp web mongodb client to record run status
    Settings:
     Always required:
      - bluesky_docker_image -- name of bluesky docker image, with version
     Required if writing to db (i.e. if `db` is defined):
      - output_url_scheme
      - output_url_port
      - output_url_path_prefix

    If this is an asynchronous run (i.e. `db` is defined), then we'll
    mount the output directory to the host machine's output directory;
    otherwise, we'll mount to host machines /tmp/, since we'll just
    read it here and then forget about it.
    """
    run_id = input_data.get('run_id') or str(uuid.uuid1()).replace('-','')
    input_data['run_id'] = run_id # in case it was just generated
    container_name = 'bsp-playground-{}'.format(run_id)
    output_dir = os.path.abspath(os.path.join(settings['output_root_dir'],
        settings['output_url_path_prefix'], input_data['run_id']))
    os.makedirs(output_dir, exist_ok=True) # TODO: is this necessary, or will docker create it?
    tornado.log.gen_log.debug('Output dir: %s', output_dir)
    output_json_filename = os.path.join(output_dir, 'output.json')
    output_log_filename = os.path.join(output_dir, 'output.log')
    bsp_cmd = ('bsp -i /tmp/fires.json -o {} '
        '--log-file={} --log-level={}'.format(
        output_json_filename, output_log_filename,
        settings['bluesky_log_level']))
    tornado.log.gen_log.debug('bsp command: %s', bsp_cmd)
    volumes_dict = _get_volumes_dict(output_dir, input_data)

    input_data_json = input_data_json or json.dumps(input_data)
    tornado.log.gen_log.info("bsp docker command (as user %s): %s",
        getpass.getuser(), bsp_cmd)

    client = docker.from_env()
    container = client.containers.create(settings['bluesky_docker_image'],
        bsp_cmd, name=container_name, volumes=volumes_dict)
    try:
        # TODO: if not capturing output,
        #     - write logs to file, in dispersion output dir or where
        #       dispersion ouput would be if dispersion run
        #     - write to files next to log file.
        #   else:
        #     - write logs to dev null?
        #     - capture and return output json

        # return client.containers.run(bluesky_docker_image, bsp_cmd,
        #     remove=True, name=container_name, volumes=volumes_dict,
        #     tty=True)
        _create_input_file(input_data_json, container)
        container.start()
        db and db.record_run(input_data['run_id'], 'running')
        # TODO: rather than just wait, poll the logs and report status?
        docker.APIClient().wait(container.id)
        db and db.record_run(input_data['run_id'], 'completed')
        with open(output_json_filename, 'r') as f:
            output = f.read()

        if db:
            try:
                # check output for error, and if so record status
                # 'failed' with error message
                error = json.loads(output).get('error')
                if error:
                    db.record_run(input_data['run_id'], 'failed', error=error)

            except Exception as e:
                tornado.log.gen_log.error('failed to parse error : %s', e)
                pass

            output_url = form_output_url(input_data['run_id'], **settings)
            db.record_run(input_data['run_id'], 'output_written',
                output_url=output_url, output_dir=output_dir)

        else:
            return output

    except Exception as e:
        #tornado.log.gen_log.debug(traceback.format_exc())
        db and db.record_run(input_data['run_id'], 'failed',
            error={"message": str(e)})
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
    container.put_archive(path='/tmp', data=tar_stream)

def _read_file_from_sibling_docker_container(container, file_pathname):
    # TODO: figure out how to extract output from tar stream,
    #    to avoid having to write to file first
    response = container.get_archive(file_pathname)[0]
    tarfilename = '/tmp/' + str(uuid.uuid1()) + '.tar'
    with open(tarfilename, 'wb') as f:
        #f.write(response.read())
        for chunk in response.read_chunked():
            f.write(chunk)

    output = None
    with tarfile.open(tarfilename) as t:
        output = t.extractfile(os.path.basename(file_pathname)).read()

    # TODO: remove tarfile

    return output


##
## Mounting dirs
##

TRAILING_RUN_ID_RE = re.compile('/{run_id}/?$')
def _get_volumes_dict(output_dir, input_data):
    """ Only mount the host os dirs that are needed
    """
    dirs_to_mount =  (
        _get_load_dirs(input_data) +
        _get_met_dirs(input_data)
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

    volumes_dict[output_dir] = {'bind': output_dir, 'mode': 'rw'}

    tornado.log.gen_log.debug('volumes dict: %s', volumes_dict)
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
    met_files = [e['file'] for e in input_data.get('met', {}).get('files', [])]
    met_dirs.extend(list(set([os.path.dirname(f) for f in met_files])))

    return met_dirs

def _get_val(input_data, *args):
    if isinstance(input_data, dict):
        v = input_data.get(args[0])
        if len(args) == 1:
            return v
        return _get_val(v, *args[1:])
