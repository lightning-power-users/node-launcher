from PySide2.QtCore import QByteArray, QProcess
from PySide2.QtWidgets import QDialog

from node_launcher.node_set import NodeSet


class OutputWidget(QDialog):
    node_set: NodeSet
    process: QProcess

    def __init__(self):
        super().__init__()

    def handle_output(self):
        while self.process.canReadLine():
            line_bytes: QByteArray = self.process.readLine()
            line_str = line_bytes.data().decode('utf-8').strip()
            self.process_output_line(line_str)
