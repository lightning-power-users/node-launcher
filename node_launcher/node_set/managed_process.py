from PySide2.QtCore import QProcess, QByteArray, Signal
from PySide2.QtWidgets import QSystemTrayIcon

from node_launcher.logging import log


class ManagedProcess(QProcess):
    status_update = Signal(str)
    notification = Signal(str, str, QSystemTrayIcon.MessageIcon)
    log_line = Signal(str)

    def __init__(self, binary: str, args):
        super().__init__()
        self.binary = binary
        self.setProgram(binary)
        self.setArguments(args)
        self.setProcessChannelMode(QProcess.MergedChannels)
        self.readyReadStandardOutput.connect(self.handle_output)

    def handle_output(self):
        while self.canReadLine():
            line_bytes: QByteArray = self.readLine()
            try:
                line_str = line_bytes.data().decode('utf-8').strip()
                log.debug(f'Process output', line=line_str, binary=self.binary)
            except UnicodeDecodeError:
                log.error('handle_output decode error', exc_info=True)
                continue
            self.process_output_line(line_str)
            self.log_line.emit(line_str)
