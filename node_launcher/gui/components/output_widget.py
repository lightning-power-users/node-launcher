from PySide2.QtWidgets import QGridLayout, QTextEdit, QWidget


class OutputWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.output_text_edit = QTextEdit()
        self.output_text_edit.setReadOnly(True)
        self.output_text_edit.acceptRichText = True
        self.output_text_edit.document().setMaximumBlockCount(5000)

        self.layout = QGridLayout()
        self.layout.addWidget(self.output_text_edit)
        self.setLayout(self.layout)

    def append(self, source, line):
        self.output_text_edit.append(f'[{source}] {line}')
