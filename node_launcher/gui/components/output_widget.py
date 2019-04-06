from PySide2.QtCore import QByteArray, QProcess
from PySide2.QtWidgets import QGridLayout, QTextEdit, QWidget

from node_launcher.node_set import NodeSet


class OutputWidget(QWidget):
    node_set: NodeSet
    process: QProcess

    def __init__(self):
        super().__init__()
        self.layout = QGridLayout()
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.acceptRichText = True
        self.output.document().setMaximumBlockCount(1000)
        self.layout.addWidget(self.output)
        self.setLayout(self.layout)

    def handle_output(self):
        while self.process.canReadLine():
            line_bytes: QByteArray = self.process.readLine()
            line_str = line_bytes.data().decode('utf-8').strip()
            self.output.append(line_str)
            self.process_output_line(line_str)

    def handle_error(self):
        output: QByteArray = self.process.readAllStandardError()
        message = output.data().decode('utf-8').strip()
        self.output.append(message)
