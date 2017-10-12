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

from blueskymongo.client import BlueSkyWebDB, RunStatuses

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

try:
    IP_ADDRESS = ipify.get_ip()
except:
    # this should only happen in dev, if working without internet connection
    IP_ADDRESS = 'localhost'
HOSTNAME = os.environ.get('PUBLIC_HOSTNAME') or IP_ADDRESS

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
    db.record_run(input_data['run_id'], RunStatuses.Dequeued,
        server={"ip": IP_ADDRESS})
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
    return BlueSkyRunner(input_data, input_data_json=input_data_json,
        db=db, **settings).run()


##
## Launching process
##

class BlueSkyRunner(object):

    def __init__(self, input_data, input_data_json=None, db=None, **settings):
        """Constructor
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
        self.input_data = input_data
        self.input_data_json = input_data_json or json.dumps(self.input_data)
        self.db = db
        self.settings = settings

    def run(self):
        self.input_data['run_id'] = (self.input_data.get('run_id')
            or str(uuid.uuid1()).replace('-',''))
        self._set_output_params()
        self._set_bsp_cmd()
        self._set_output_url()

        return self._run_docker()

    ##
    ## Setup
    ##

    def _set_output_params(self):
        self.output_dir = os.path.abspath(os.path.join(
            self.settings['output_root_dir'],
            self.settings['output_url_path_prefix'],
            self.input_data['run_id']))
        os.makedirs(self.output_dir, exist_ok=True) # TODO: is this necessary, or will docker create it?
        tornado.log.gen_log.debug('Output dir: %s', self.output_dir)
        self.input_json_filename = os.path.join(
            self.output_dir, 'fires.json')
        self.output_json_filename = os.path.join(
            self.output_dir, 'output.json')
        self.output_log_filename = os.path.join(
            self.output_dir, 'output.log')

    def _set_bsp_cmd(self):
        self.bsp_cmd = ('bsp -i {} -o {} '
            '--log-file={} --log-level={}'.format(
            self.input_json_filename, self.output_json_filename,
            self.output_log_filename, self.settings['bluesky_log_level']))
        tornado.log.gen_log.info("bsp docker command (as user %s): %s",
            getpass.getuser(), self.bsp_cmd)

    def _set_output_url(self):
        scheme = self.settings.get('output_url_scheme') or 'https'
        port_str = (':' + self.settings['output_url_port']
            if self.settings.get('output_url_port') else '')
        prefix = (self.settings.get('output_url_path_prefix') or '').strip('/')
        self.output_url = "{}://{}{}/{}/{}".format(
            scheme, HOSTNAME, port_str, prefix, self.input_data['run_id'])

    ##
    ## Execution
    ##

    def _run_docker(self):
        client = docker.from_env()
        container_name = 'bluesky-web-bsp-{}'.format(self.input_data['run_id'])
        volumes_dict = self._get_volumes_dict()
        container = client.containers.create(self.settings['bluesky_docker_image'],
            self.bsp_cmd, name=container_name, volumes=volumes_dict)
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
            self._create_input_file(container)
            container.start()
            self._record_run(RunStatuses.Running)
            self._wait(container)
            self._record_run(RunStatuses.ProcessingOutput)
            with open(self.output_json_filename, 'r') as f:
                output = f.read()

            if self.db:
                data = {
                    'output_url': self.output_url,
                    'output_dir': self.output_dir
                }
                try:
                    # check output for error, and if so record status
                    # 'failed' with error message
                    error = json.loads(output).get('error')
                    if error:
                        data['error'] = error

                except Exception as e:
                    tornado.log.gen_log.error('failed to parse error : %s', e)
                    pass

                status = (RunStatuses.Failed if 'error' in data
                    else RunStatuses.Completed)
                self._record_run(status, **data)

            else:
                return output

        except Exception as e:
            #tornado.log.gen_log.debug(traceback.format_exc())
            self._record_run(RunStatuses.Failed,
                error={"message": str(e)})
            raise BlueSkyJobError(str(e))

        finally:
            container.stop()
            container.remove()

    def _wait(self, container):
        #docker.APIClient().wait(container.id)

        # TODO: figure out more elegant way of polling for completion than
        #   calling top until it raises an APIError
        api_client = docker.APIClient()
        while True:
            try:
                api_client.top(container.id)
            except docker.errors.APIError as e:
                # TODO: somehow confirm not failure, e.g. by checking
                #    for presence of output file.  If failure, raise exception
                #    (though, I guess if there's not output file, the)
                return

            try:
                # last entry in log
                e = api_client.exec_create(container.id,
                    'tail -1 {}'.format(self.output_log_filename))
                r = api_client.exec_start(e['Id'])
                # last line in stdout
                s = api_client.logs(container.id, tail=1)
                self._record_run(RunStatuses.Running, log=r.decode(),
                    stdout=s.decode())
            except Exception as e:
                print(e)
                pass

            time.sleep(5)

    ##
    ## DB
    ##

    def _record_run(self, status, log=None, stdout=None, **data):
        if self.db:
            self.db.record_run(self.input_data['run_id'], status, log=log,
                stdout=stdout, **data)

    ##
    ## I/O
    ##

    def _create_input_file(self, container):
        tar_stream = BytesIO()
        tar_file = tarfile.TarFile(fileobj=tar_stream, mode='w')
        tar_file_data = self.input_data_json.encode('utf8')
        tar_info = tarfile.TarInfo(name='fires.json')
        tar_info.size = len(tar_file_data)
        tar_info.mtime = time.time()
        #tar_info.mode = 0600
        tar_file.addfile(tar_info, BytesIO(tar_file_data))
        tar_file.close()
        tar_stream.seek(0)
        container.put_archive(path=self.output_dir, data=tar_stream)

    def _read_file_from_sibling_docker_container(self, container, file_pathname):
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
    def _get_volumes_dict(self):
        """ Only mount the host os dirs that are needed
        """
        dirs_to_mount =  (
            self._get_load_dirs() +
            self._get_met_dirs()
        )
        dirs_to_mount = list(set([m for m in dirs_to_mount if m]))
        volumes_dict = {}
        if dirs_to_mount:
            for d in dirs_to_mount:
                # remove trailing '/{run_id}' from mount point
                d = self.TRAILING_RUN_ID_RE.sub('/', d)
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

        volumes_dict[self.output_dir] = {'bind': self.output_dir, 'mode': 'rw'}

        tornado.log.gen_log.debug('volumes dict: %s', volumes_dict)
        return volumes_dict

    def _get_load_dirs(self):
        load_dirs = []
        sources = self._get_val(self.input_data, "config", "load", "sources")
        if sources:
            for s in sources:
                for f in ('file', 'events_file'):
                    if s.get(f):
                        load_dirs.append(os.path.split(s[f])[0])
        return load_dirs

    def _get_met_dirs(self):
        # met dirs
        met_dirs = [
            self._get_val(self.input_data, 'config', 'findmetdata', "met_root_dir"),
        ]
        met_files = [e['file'] for e in self.input_data.get('met', {}).get('files', [])]
        met_dirs.extend(list(set([os.path.dirname(f) for f in met_files])))

        return met_dirs

    def _get_val(self, data, *args):
        if isinstance(data, dict):
            v = data.get(args[0])
            if len(args) == 1:
                return v
            return self._get_val(v, *args[1:])
