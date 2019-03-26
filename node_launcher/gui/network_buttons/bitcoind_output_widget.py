import os
from datetime import datetime

from PySide2.QtCore import QByteArray, QProcess, QThreadPool, Qt
from PySide2.QtWidgets import QDialog, QTextEdit

from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.node_set import NodeSet


class BitcoindOutputWidget(QDialog):
    node_set: NodeSet
    process: QProcess

    def __init__(self, node_set: NodeSet, system_tray):
        super().__init__()
        self.node_set = node_set
        self.system_tray = system_tray
        self.process = node_set.bitcoin.process
        self.setWindowTitle('Bitcoind Output')
        self.layout = QGridLayout()

        self.threadpool = QThreadPool()

        self.output = QTextEdit()
        self.output.acceptRichText = True

        self.layout.addWidget(self.output)
        self.setLayout(self.layout)

        self.old_progress = None
        self.old_timestamp = None

    def handle_error(self):
        output: QByteArray = self.process.readAllStandardError()
        message = output.data().decode('utf-8').strip()
        self.output.append(message)

    def handle_output(self):
        output: QByteArray = self.process.readAllStandardOutput()
        message = output.data().decode('utf-8').strip()
        lines = message.split(os.linesep)
        for line in lines:
            if 'UpdateTip' in line:
                line_segments = line.split(' ')
                timestamp = line_segments[0]
                for line_segment in line_segments:
                    if 'progress' in line_segment:
                        new_progress = float(line_segment.split('=')[-1])
                        self.system_tray.menu.bitcoind_status_action.setText(f'{new_progress*100:.4f}%')
                        new_timestamp = datetime.strptime(
                            timestamp,
                            '%Y-%m-%dT%H:%M:%SZ'
                        )
                        if new_progress != self.old_progress:
                            if self.old_progress is not None:
                                change = new_progress - self.old_progress
                                timestamp_change = new_timestamp - self.old_timestamp
                            self.old_progress = new_progress
                            self.old_timestamp = new_timestamp

            self.output.append(line)

    def show(self):
        self.showMaximized()
        self.raise_()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()
