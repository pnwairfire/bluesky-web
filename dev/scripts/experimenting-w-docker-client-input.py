#!/usr/bin/env python
"""
Links:
 - http://docker-py.readthedocs.io/en/stable/api.html
 - see: https://jpetazzo.github.io/2015/09/03/do-not-use-docker-in-docker-for-ci/
 - see: https://github.com/docker/docker-py/issues/983
"""

import docker
import sys
import tarfile
import time
import uuid
from io import BytesIO

FIRES_JSON = '{"modules": ["ingestion", "fuelbeds","consumption","emissions"], "today": "2017-07-12", "runtime": {"total": "0.0h 0.0m 0s", "end": "2017-07-12T18:27:05Z", "start": "2017-07-12T18:27:05Z"}, "fire_information": [{"type": "wildfire", "growth": [{"end": "2015-01-21T17:00:00", "location": {"geojson": {"type": "MultiPolygon", "coordinates": [[[[-121.4522115, 47.4316976], [-121.3990506, 47.4316976], [-121.3990506, 47.4099293], [-121.4522115, 47.4099293], [-121.4522115, 47.4316976]]]]}, "ecoregion": "southern", "utc_offset": "-09:00"}, "start": "2015-01-20T17:00:00"}], "fuel_type": "natural", "event_of": {"id": "SF11E826544", "name": "Natural Fire near Snoqualmie Pass, WA"}, "id": "SF11C14225236095807750"}], "config": {}, "counts": {"fires": 1}}'

client = docker.from_env()



def run_no_input():
    output = client.containers.run('bluesky', 'bsp -h', tty=True,
        remove=True)
    return output


## using socket
def run_socket_io():

    container = client.containers.create('bluesky', tty=True, stdin_open=True)
    container.start()
    container.exec_run('bsp -o /tmp/output.json', stdout=True, stderr=True, stdin=True, tty=True)
    socket = container.attach_socket()
    os.write(socket.fileno(), FIRES_JSON.encode())

    #READ FROM SOCKET

    # container.stop()
    container.remove()

    #container.exec_run('ls /usr/bin/', stdout=True, stderr=True, stdin=True, tty=True)


## using put_archive/get_archive

def run_file_io():

    fires_input = FIRES_JSON

    pw_tarstream = BytesIO()
    pw_tar = tarfile.TarFile(fileobj=pw_tarstream, mode='w')
    file_data = fires_input.encode('utf8')
    tarinfo = tarfile.TarInfo(name='fires.json')
    tarinfo.size = len(file_data)
    tarinfo.mtime = time.time()
    #tarinfo.mode = 0600
    pw_tar.addfile(tarinfo, BytesIO(file_data))
    pw_tar.close()

    container = client.containers.create('bluesky', 'bsp -i /tmp/fires.json -o /tmp/output.json')
    pw_tarstream.seek(0)
    pr = container.put_archive(path='/tmp', data=pw_tarstream)
    container.start()
    container.status
    docker.APIClient().wait(container.id)
    response = container.get_archive('/tmp/output.json')[0]
    tarfilename = str(uuid.uuid1()) + '.tar'
    with open(tarfilename, 'wb') as f:
        #f.write(response.read())
        for chunk in response.read_chunked():
            f.write(chunk)

    output = None
    with tarfile.open(tarfilename) as t:
        output = t.extractfile('output.json').read()
    #output = response.read()
    # with open('/tmp/output.tar', 'w') as f:
    #     f.write(output)

    # with tarfile.open()


    # with BytesIO() as f:
    #     f.write(response.read())
    #     t = tarfile.open(fileobj=f)

    container.remove()
    return output


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage:\n  {} <function>".format(sys.argv[0]))
        sys.exit(1)

    try:
        f = getattr(sys.modules[__name__], sys.argv[1])
    except AttributeError:
        print("** Error: Invalid function **")
        sys.exit(1)

    print(f())
