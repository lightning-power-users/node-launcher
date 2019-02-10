from typing import List

from PySide2.QtCore import SIGNAL, QProcess, QByteArray
from PySide2.QtWidgets import QWidget, QTextEdit, QLineEdit

from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.logging import log


class CliWidget(QWidget):
    def __init__(self, program: str, args: List[str]):
        super().__init__()

        self.program = program
        self.args = args

        self.layout = QGridLayout()

        self.output = QTextEdit()
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
        self.output.append(f'> {cmd}')
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
        output: QByteArray = self.process.readLine()
        message = output.data().decode('utf-8').strip()
        while message:
            output = self.process.readLine()
            message = output.data().decode('utf-8').strip()
            self.output.append(message)
