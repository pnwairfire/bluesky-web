#!/usr/bin/env python

import docker
import time
import traceback

client = docker.from_env()
cmd = 'bash -c "for i in `seq 1 10`; do echo $i >> /tmp/foo.txt && sleep 1; done"'
container = client.containers.create(
    'bluesky', cmd, name="foo")
try:
    container.start()
    api_client = docker.APIClient()
    while True:
        print('status: {}'.format(container.status))
        try:
            api_client.top(container.id)
        except docker.errors.APIError as e:
            print("no longer running")
            break

        e = api_client.exec_create(container.id, 'tail -1 /tmp/foo.txt')
        r = api_client.exec_start(e['Id'])
        print(r)
        time.sleep(2)
    # for l in api_client.logs(container.id, stream=True):
    #     print(l)
    #api_client.wait(container.id)


except Exception as e:
    print("Failed: {}".format(e))
    print(traceback.format_exc())

finally:
    print("stopping container")
    container.stop()
    print("removing container")
    container.remove()

