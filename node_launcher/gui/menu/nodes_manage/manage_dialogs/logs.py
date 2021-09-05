
from node_launcher.gui.qt import QDialog, QGridLayout, QTextEdit


class LogsDialog(QDialog):

    def __init__(self, node):
        super().__init__()

        self.node = node

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.acceptRichText = True
        self.output_area.document().setMaximumBlockCount(5000)

        self.layout.addWidget(self.output_area)

        self.node.process.log_line.connect(
            lambda line: self.output_area.append(line)
        )
