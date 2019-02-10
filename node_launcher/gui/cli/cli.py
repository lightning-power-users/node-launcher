import json
from typing import List

from PySide2.QtCore import SIGNAL, QProcess, QByteArray
from PySide2.QtWidgets import QWidget, QTextEdit, QLineEdit
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.data import JsonLexer

from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.logging import log


class CliWidget(QWidget):
    def __init__(self, program: str, args: List[str]):
        super().__init__()

        self.program = program
        self.args = args

        self.layout = QGridLayout()

        self.output = QTextEdit()
        self.output.acceptRichText = True

        self.input = QLineEdit()

        self.process = QProcess()
        self.process.setProgram(self.program)
        self.process.setCurrentReadChannel(0)

        # noinspection PyUnresolvedReferences
        self.process.readyReadStandardError.connect(self.handle_error)
        # noinspection PyUnresolvedReferences
        self.process.readyReadStandardOutput.connect(self.handle_output)

        self.layout.addWidget(self.output)
        self.layout.addWidget(self.input)
        self.setLayout(self.layout)

        self.connect(self.input, SIGNAL("returnPressed(void)"),
                     self.run_command)

    def run_command(self):
        cmd = str(self.input.text())
        log.info(
            'run_command',
            program=self.program,
            args=self.args,
            cmd=cmd
        )
        self.output.append(f'> {cmd}\n')
        self.input.clear()
        self.process.kill()
        args = list(self.args)
        args.append(cmd)
        self.process.setArguments(args)
        self.process.start()

    def handle_error(self):
        output: QByteArray = self.process.readAllStandardError()
        message = output.data().decode('utf-8').strip()
        self.output.append(message)

    def handle_output(self):
        output: QByteArray = self.process.readAllStandardOutput()
        message = output.data().decode('utf-8').strip()
        if message.startswith('{') or message.startswith('['):
            message = json.loads(message)
            message = json.dumps(message, sort_keys=True, indent=4)
            formatter = HtmlFormatter()
            formatter.noclasses = True
            formatter.linenos = False
            formatter.nobackground = True
            message = highlight(message, JsonLexer(), formatter)
            self.output.insertHtml(message)
        else:
            self.output.append(message)
        max_scroll = self.output.verticalScrollBar().maximum()
        self.output.verticalScrollBar().setValue(max_scroll)
