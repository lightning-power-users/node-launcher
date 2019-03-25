import os

from PySide2.QtCore import QByteArray, QProcess, QThreadPool
from PySide2.QtWidgets import QDialog, QTextEdit

from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.node_set import NodeSet


class BitcoindOutputWidget(QDialog):
    node_set: NodeSet
    process: QProcess

    def __init__(self, node_set: NodeSet):
        super().__init__()
        self.node_set = node_set
        self.process = node_set.bitcoin.process
        self.setWindowTitle('Bitcoind Output')
        self.layout = QGridLayout()

        self.threadpool = QThreadPool()

        self.output = QTextEdit()
        self.output.acceptRichText = True

        self.layout.addWidget(self.output)
        self.setLayout(self.layout)

    def handle_error(self):
        output: QByteArray = self.process.readAllStandardError()
        message = output.data().decode('utf-8').strip()
        self.output.append(message)

    def handle_output(self):
        output: QByteArray = self.process.readAllStandardOutput()
        message = output.data().decode('utf-8').strip()
        lines = message.split(os.linesep)
        for line in lines:
            self.output.append(line)

    def show(self):
        self.showMaximized()
