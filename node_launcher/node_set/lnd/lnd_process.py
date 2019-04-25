from datetime import datetime

import humanize
from PySide2.QtCore import QTimer, Signal
from PySide2.QtWidgets import QSystemTrayIcon

from node_launcher.node_set.lib.managed_process import ManagedProcess
from node_launcher.node_set.lib.node_status import NodeStatus


class LndProcess(ManagedProcess):
    set_icon_color = Signal(str)

    def __init__(self, binary: str, args):
        super().__init__(binary, args)

        self.old_height = None
        self.old_timestamp = None

    def process_output_line(self, line: str):
        if 'Waiting for wallet encryption password' in line:
            self.update_status(NodeStatus.UNLOCK_READY)
        elif 'Waiting for chain backend to finish sync' in line:
            self.set_icon_color.emit('blue')
            self.update_status(NodeStatus.SYNCING)
        elif 'Unable to synchronize wallet to chain' in line:
            self.terminate()
            self.restart_process()
        elif 'Unable to complete chain rescan' in line:
            self.terminate()
            self.restart_process()
        elif 'Starting HTLC Switch' in line:
            self.set_icon_color.emit('green')
            self.update_status(NodeStatus.SYNCED)
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
                    self.sync_progress.emit(
                        f'ETA: {humanized}, caught up to height {new_height}'
                    )

            self.old_height = new_height
            self.old_timestamp = new_timestamp

    def restart_process(self):
        QTimer.singleShot(3000, self.start)
