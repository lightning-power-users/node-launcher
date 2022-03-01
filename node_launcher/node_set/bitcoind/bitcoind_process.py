import re
from datetime import datetime, timedelta
from decimal import Decimal

import humanize

from node_launcher.gui.qt import QSystemTrayIcon
from node_launcher.node_set.lib.managed_process import ManagedProcess
from node_launcher.node_set.lib.node_status import NodeStatus


class BitcoindProcess(ManagedProcess):
    def __init__(self, binary, args):
        super().__init__(binary, args)
        self.old_progress = None
        self.old_timestamp = None

        self.timestamp_changes = []

    def process_output_line(self, line: str):
        if 'Bitcoin Core version' in line:
            self.update_status(NodeStatus.PROCESS_STARTED)
        elif 'Shutdown: done' in line:
            if self.expecting_shutdown:
                return
            self.update_status(NodeStatus.RUNTIME_ERROR)
            self.notification.emit(
                'Bitcoin Error',
                'Please check Bitcoin Output',
                QSystemTrayIcon.Critical
            )
        elif 'Bitcoin Core is probably already running' in line:
            self.update_status(NodeStatus.RUNTIME_ERROR)
            self.notification.emit(
                'Bitcoin Error',
                'Bitcoin Core is already running',
                QSystemTrayIcon.Critical
            )

        match = re.search(r'progress=\d.\d\d\d\d\d\d', line)
        if not match:
            return
        self.update_status(NodeStatus.PROCESS_STARTED)
        line_segments = line.split(' ')
        timestamp_string = line_segments[0]
        parsed_timestamp = datetime.strptime(
            timestamp_string,
            '%Y-%m-%dT%H:%M:%SZ'
        )
        new_progress = Decimal(match.group().split('=')[-1])
        if new_progress > Decimal('0.99'):
            self.update_status(NodeStatus.SYNCED)
            return
        if not self.old_progress or new_progress == self.old_progress:
            self.old_progress = new_progress
            self.old_timestamp = parsed_timestamp
            return
        change = new_progress - self.old_progress
        timestamp_change = parsed_timestamp - self.old_timestamp
        if not change or not timestamp_change:
            return
        total_left = 1 - new_progress
        remaining_time = ((total_left / change) * timestamp_change.seconds)
        self.timestamp_changes.append(remaining_time)
        if len(self.timestamp_changes) > 10:
            self.timestamp_changes.pop(0)
        average_remaining_time = sum(self.timestamp_changes) / len(self.timestamp_changes)
        humanized_remaining_time = humanize.naturaltime(-timedelta(seconds=int(average_remaining_time)))
        self.remaining_time_signal.emit(humanized_remaining_time)
        percentage_progress = int(new_progress*100)
        self.percentage_progress_signal.emit(percentage_progress)
        self.old_progress = new_progress
        self.old_timestamp = parsed_timestamp