from datetime import datetime, timedelta

import humanize
from PySide2.QtCore import Signal
from PySide2.QtWidgets import QSystemTrayIcon

from node_launcher.node_set.lib.managed_process import ManagedProcess


class BitcoinProcess(ManagedProcess):
    synced = Signal(bool)

    def __init__(self, binary, args):
        super().__init__(binary, args)
        self.old_progress = None
        self.old_timestamp = None

        self.timestamp_changes = []

        self.expecting_shutdown = False

    def process_output_line(self, line: str):
        if 'Bitcoin Core version' in line:
            self.status_update.emit('Bitcoin starting')
        elif 'Leaving InitialBlockDownload' in line:
            self.status_update.emit('Bitcoin synced')
            self.synced.emit(True)
        elif 'Shutdown: done' in line:
            if self.expecting_shutdown:
                return
            self.status_update.emit('Error: please check Bitcoin Output')
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
                                self.status_update.emit(f'ETA: {humanized}, {new_progress*100:.2f}% done')
                        else:
                            if round(new_progress*100) == 100:
                                continue
                            self.self.status_update.emit(f'{new_progress*100:.2f}%')
                        self.old_progress = new_progress
                        self.old_timestamp = new_timestamp
        elif 'Bitcoin Core is probably already running' in line:
            self.status_update.emit('Error: Bitcoin Core is already running')
            self.notification.emit(
                'Bitcoin Error',
                'Bitcoin Core is already running',
                QSystemTrayIcon.Critical
            )