
from node_launcher.gui.qt import (
    Qt, SIGNAL, QProcess, QByteArray, QDialog, QGridLayout, QTextEdit, QLineEdit, QCompleter
)

from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.data import JsonLexer

from node_launcher.app_logging import log
from node_launcher.node_set.lib.network_node import NetworkNode


class ConsoleDialog(QDialog):

    def __init__(self, node: NetworkNode):
        super().__init__()

        self.node = node

        self.show_help = True

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.acceptRichText = True
        self.output_area.document().setMaximumBlockCount(5000)
        self.layout.addWidget(self.output_area)

        self.input_area = QLineEdit()
        self.completer = QCompleter()
        # noinspection PyUnresolvedReferences
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.input_area.setCompleter(self.completer)
        self.input_area.setFocus()
        self.layout.addWidget(self.input_area)

        self.input_area.returnPressed.connect(self.execute_user_command)

    @property
    def cli(self):
        try:
            return self.node.software.cli
        except AttributeError:
            return None

    @property
    def cli_args(self):
        try:
            return self.node.configuration.cli_args
        except AttributeError:
            return None

    def showEvent(self, event):
        super().showEvent(event)

        if self.show_help:
            success = self.run_command('help')
            if success:
                self.show_help = False

    def execute_user_command(self):
        cmd = str(self.input_area.text())
        self.input_area.clear()
        self.run_command(cmd)

    def run_command(self, command):
        try:
            if self.cli is None or self.cli_args is None:
                self.output_area.append('Node starting up, please try again later...')
                return False

            self.output_area.append(f'> {command}\n')

            process = QProcess()
            process.setProgram(self.cli)
            process.setCurrentReadChannel(0)

            # noinspection PyUnresolvedReferences
            process.readyReadStandardError.connect(
                lambda: self.handle_cli_error_output(process)
            )

            # noinspection PyUnresolvedReferences
            process.readyReadStandardOutput.connect(
                lambda: self.handle_cli_output(process)
            )

            args = command.split(' ')
            if args[0] == self.cli.split('/')[-1]:
                args.pop(0)
            process.setArguments(self.cli_args + args)
            process.start()

            log.info(
                'run_command',
                program=self.cli,
                args=self.cli_args,
                cmd=command
            )

            return True
        except Exception:
            self.output_area.append('Node starting up, please try again later...')
            return False

    def handle_cli_error_output(self, cli_process: QProcess):
        output: QByteArray = cli_process.readAllStandardError()
        message = output.data().decode('utf-8').strip()
        self.output_area.append(message)

    def handle_cli_output(self, cli_process: QProcess):
        output: QByteArray = cli_process.readAllStandardOutput()
        message = output.data().decode('utf-8').strip()

        if message.startswith('{') or message.startswith('['):
            formatter = HtmlFormatter()
            formatter.noclasses = True
            formatter.linenos = False
            formatter.nobackground = True
            message = highlight(message, JsonLexer(), formatter)
            self.output_area.insertHtml(message)
        else:
            self.output_area.append(message)
