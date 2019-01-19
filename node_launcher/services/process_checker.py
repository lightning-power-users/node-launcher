import subprocess
from typing import List
from sys import platform

from time import sleep
from threading import Thread
from psutil import Process, process_iter


class ProcessChecker(Thread):

    def __init__(self):
        super(ProcessChecker, self).__init__()

        self._relevant_process_names = ['bitcoin', 'lnd']
        self._task_list = {}

    # Private methods

    def _refresh_task_list(self):
        new_task_list = {}
        if platform == 'win32':
            # In Windows it's faster to just take the output of tasklist.exe and do some string parsing
            task_list_output = subprocess.check_output('tasklist')
            for line in task_list_output.splitlines():
                line_str = line.decode('utf-8')
                for rpn in self._relevant_process_names:
                    if rpn in line_str:
                        line_components = line_str.split(' ')
                        # line_components[0] will hold the process name
                        # the next non empty string will hold the process id
                        for line_component in line_components[1:]:
                            if line_component != '':
                                new_task_list[line_components[0]] = int(line_component)
                                break
        else:
            for process in process_iter():
                # noinspection PyBroadException
                try:
                    process_name = process.name()
                    pid = process.pid()
                except Exception:
                    continue

                for rpn in self._relevant_process_names:
                    if rpn in process_name:
                        new_task_list[process_name] = int(pid)

        self._task_list = new_task_list

    def run(self):
        while True:
            self._refresh_task_list()
            sleep(2)

    # Public methods

    def get_processes_by_name(self, process_name) -> List[Process]:
        processes = []
        for pn, pid in self._task_list.items():
            if process_name in pn:
                # noinspection PyBroadException
                try:
                    process = Process(pid)
                except Exception as e:
                    print('Exception: ' + str(e))
                    continue

                processes.append(process)

        return processes


process_checker = ProcessChecker()
process_checker.start()
