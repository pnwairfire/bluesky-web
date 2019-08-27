import os
import subprocess
import time
import threading

import tornado.log

from blueskymongo.client import RunStatuses

class HysplitMonitor(threading.Thread):
    """Monitor thread that scrapes hysplit MESSAGE files to determine
    how many hours are complete
    """
    def __init__(self, m, fires_manager, record_run_func):
        super(HysplitMonitor, self).__init__()
        self.m = m
        self.fires_manager = fires_manager
        self.start_hour = self.fires_manager.get_config_value(
            'dispersion', 'start')
        self.num_hours = self.fires_manager.get_config_value(
            'dispersion', 'num_hours')

        self.record_run_func = record_run_func
        self.terminate = False
        self._message_file_name = None

    @property
    def message_file_name(self):
        if self._message_file_name is None:
            # this code will run again if no message files are found
            working_dir = self.fires_manager.get_config_value(
                'dispersion', 'working_dir')
            mp1 = os.path.join(working_dir, 'MESSAGE')
            if os.path.exists(mp1):
                self._message_file_name = mp1
            else:
                mpN = os.path.join(working_dir, 'MESSAGE.001')
                if os.path.exists(mpN):
                    self._message_file_name = mpN

        return self._message_file_name

    def run(self):
        while not self.terminate:
            self.check_progress()
            time.sleep(5)

    def check_progress(self):
        percent_complete = 2
        if self.message_file_name:
            try:
                # estimate percent complete based on slowest of
                # all hysplit processes
                current_hour = self.get_current_hour()
                # we want percent_complete to be between 3 and 90
                percent_complete = int((90 * (current_hour / self.num_hours)) + 2)
            except Exception as e:
                tornado.log.gen_log.info("Failed to check progress: %s", e)

        # else, leave at 2
        tornado.log.gen_log.info("Run %s hysplit %d complete",
            self.fires_manager.run_id, percent_complete)

        self.record_run_func(RunStatuses.RunningModule, module=self.m,
            percent_complete=percent_complete)

    def get_current_hour(self):
        output_lines = [l for l in subprocess.check_output(
            ["grep", "output", self.message_file_name]).decode().split('\n') if l]
        return len(output_lines)


class monitor_run(object):

    def __init__(self, m, fires_manager, record_run_func):
        tornado.log.gen_log.info("Constructing monitor_run context manager")
        self.m = m
        self.fires_manager = fires_manager
        self.record_run_func = record_run_func
        self.thread = None

    def __enter__(self):
        tornado.log.gen_log.info("Entering monitor_run context manager")
        if self._is_hysplit():
            tornado.log.gen_log.info("Starting thread to monitor hysplit")
            self.thread = HysplitMonitor(self.m, self.fires_manager, self.record_run_func)
            self.thread.start()

    def __exit__(self, e_type, value, tb):
        if self.thread:
            self.thread.terminate = True
            tornado.log.gen_log.info("joining hysplit monitoring thread")
            self.thread.join()

    def _is_hysplit(self):
        if self.m =='dispersion':
            model = self.fires_manager.get_config_value(
                'dispersion', 'model', default='hysplit')
            return model == 'hysplit'
        return False
