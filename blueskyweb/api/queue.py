import tornado.web
import tornado.log

from blueskyworker.tasks import app

from . import RequestHandlerBase


class QueueInfo(RequestHandlerBase):

    @tornado.web.asynchronous
    async def get(self, api_version, status=None):
        # See https://docs.celeryq.dev/en/latest/userguide/workers.html#inspecting-workers

        i = app.control.inspect()

        self.write({
            #"registered": i.registered(),
            "in_queue": prune_worker_set(i.reserved()),
            "executing": prune_worker_set(i.active()),
            "scheduled": prune_worker_set(i.scheduled()),
        })


def prune_worker_set(r):
    return {w: [prune_task(t) for t in r[w]] for w in r}


def prune_task(task):
    request_args = eval(task["request"]["args"])
    t = {
        "priority": task["priority"],
        "api_version": request_args[1],
        "run_id": request_args[0]['run_id'],
        "modules": request_args[0]['modules']
    }
    if task.get('eta'):
        t['schedule_for'] = task['eta']
    return t
