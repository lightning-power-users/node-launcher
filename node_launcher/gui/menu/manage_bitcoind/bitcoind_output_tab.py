from datetime import datetime, timedelta

import humanize
from PySide2.QtCore import QProcess, QThreadPool

from node_launcher.gui.components.output_widget import OutputWidget

from node_launcher.node_set.bitcoin import Bitcoin


class BitcoindOutputTab(OutputWidget):
    bitcoin: Bitcoin
    process: QProcess

    def __init__(self, bitcoin: Bitcoin, system_tray):
        super().__init__()
        self.system_tray = system_tray
        self.process = bitcoin.process

        self.process.readyReadStandardError.connect(self.handle_error)
        self.process.readyReadStandardOutput.connect(self.handle_output)

        self.setWindowTitle('Bitcoind Output')

        self.threadpool = QThreadPool()

        self.old_progress = None
        self.old_timestamp = None

        self.timestamp_changes = []

    def process_output_line(self, line: str):
        if 'Bitcoin Core version' in line:
            self.system_tray.menu.bitcoind_status_action.setText(
                'Bitcoin starting'
            )
        elif 'Leaving InitialBlockDownload' in line:
            self.system_tray.menu.bitcoind_status_action.setText(
                'Bitcoin synced'
            )
        elif 'Shutdown: done' in line:
            self.system_tray.menu.bitcoind_status_action.setText(
                'Error, please check Bitcoin Output'
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
                                self.system_tray.menu.bitcoind_status_action.setText(
                                    f'ETA: {humanized}, {new_progress*100:.2f}% done'
                                )
                        else:
                            if round(new_progress*100) == 100:
                                continue
                            self.system_tray.menu.bitcoind_status_action.setText(
                                f'{new_progress*100:.2f}%'
                            )

                        self.old_progress = new_progress
                        self.old_timestamp = new_timestamp
