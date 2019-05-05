from datetime import datetime, timedelta

import humanize
from PySide2.QtWidgets import QSystemTrayIcon

from node_launcher.node_set.lib.managed_process import ManagedProcess
from node_launcher.node_set.lib.node_status import NodeStatus


class BitcoindProcess(ManagedProcess):
    def __init__(self, binary, args):
        super().__init__(binary, args)
        self.old_progress = None
        self.old_timestamp = None

        self.timestamp_changes = []

    def process_output_line(self, line: str):
        if 'mapBlockIndex.size() = ' in line:
            self.update_status(NodeStatus.SYNCING)
        elif 'Leaving InitialBlockDownload' in line:
            self.update_status(NodeStatus.SYNCED)
        elif 'progress=1.000000' in line:
            self.update_status(NodeStatus.SYNCED)
        elif 'Shutdown: done' in line:
            if self.expecting_shutdown:
                return
            self.update_status(NodeStatus.RUNTIME_ERROR)
            self.notification.emit(
                'Bitcoin Error',
                'Please check Bitcoin Output',
                QSystemTrayIcon.Critical
            )
        elif 'UpdateTip' in line:
            line_segments = line.split(' ')
            timestamp = line_segments[0]
            for line_segment in line_segments:
                if 'progress' in line_segment:
                    new_progress = round(float(line_segment.split('=')[-1]), 4)
                    new_timestamp = datetime.strptime(
                        timestamp,
                        '%Y-%m-%dT%H:%M:%SZ'
                    )
                    if new_progress != self.old_progress:
                        if self.old_progress is not None:
                            change = new_progress - self.old_progress
                            if change:
                                timestamp_change = new_timestamp - self.old_timestamp
                                total_left = 1 - new_progress
                                time_left = ((total_left / change)*timestamp_change).seconds
                                self.timestamp_changes.append(time_left)
                                if len(self.timestamp_changes) > 100:
                                    self.timestamp_changes.pop(0)
                                average_time_left = sum(self.timestamp_changes)/len(self.timestamp_changes)
                                humanized = humanize.naturaltime(-timedelta(seconds=average_time_left))
                                self.status.emit(f'{new_progress * 100:.2f}% synced, ETA: {humanized}')
                        else:
                            if round(new_progress*100) == 100:
                                continue
                            self.status.emit(f'{new_progress*100:.2f}% synced')
                        self.old_progress = new_progress
                        self.old_timestamp = new_timestamp
        elif 'Bitcoin Core is probably already running' in line:
            self.update_status(NodeStatus.RUNTIME_ERROR)
            self.notification.emit(
                'Bitcoin Error',
                'Bitcoin Core is already running',
                QSystemTrayIcon.Critical
            )
