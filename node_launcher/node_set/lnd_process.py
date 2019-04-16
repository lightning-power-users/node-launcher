from datetime import datetime

import humanize
from PySide2.QtCore import QTimer, Signal
from PySide2.QtWidgets import QSystemTrayIcon

from node_launcher.node_set.managed_process import ManagedProcess


class LndProcess(ManagedProcess):
    ready_to_unlock = Signal(bool)
    set_icon_color = Signal(str)

    def __init__(self, binary: str, args):
        super().__init__(binary, args)

        self.old_height = None
        self.old_timestamp = None

    def process_output_line(self, line: str):
        if 'Active chain: Bitcoin' in line:
            self.status_update.emit('LND starting')
        elif 'Waiting for wallet encryption password' in line:
            self.status_update.emit('LND unlocking wallet')
            self.ready_to_unlock.emit(True)
        elif 'Waiting for chain backend to finish sync' in line:
            self.status_update.emit('Chain backend syncing')
        elif 'Unable to synchronize wallet to chain' in line:
            self.terminate()
            self.restart_process()
        elif 'Unable to complete chain rescan' in line:
            self.terminate()
            self.restart_process()
        elif 'Starting HTLC Switch' in line:
            self.set_icon_color.emit('green')
            self.status_update.emit('LND synced')
            self.notification.emit(
                'LND is ready',
                'Open Joule or Zap',
                QSystemTrayIcon.Information
            )
        elif 'Caught up to height' in line:
            new_height = int(line.split(' ')[-1])
            timestamp = line.split('[INF]')[0].strip()
            new_timestamp = datetime.strptime(
                timestamp,
                '%Y-%m-%d %H:%M:%S.%f'
            )
            if self.old_height is not None:
                change = new_height - self.old_height
                if change:
                    timestamp_change = new_timestamp - self.old_timestamp
                    total_left = 600000 - new_height
                    time_left = (total_left / change) * timestamp_change
                    humanized = humanize.naturaltime(-time_left)
                    self.status_update.emit(
                        f'ETA: {humanized}, caught up to height {new_height}'
                    )

            self.old_height = new_height
            self.old_timestamp = new_timestamp

    def restart_process(self):
        QTimer.singleShot(3000, self.start)
