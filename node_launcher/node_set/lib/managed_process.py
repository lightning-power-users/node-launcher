from PySide2.QtCore import QProcess, QByteArray, Signal
from PySide2.QtWidgets import QSystemTrayIcon

from node_launcher.logging import log
from node_launcher.node_set.lib.node_status import NodeStatus


class ManagedProcess(QProcess):
    status = Signal(str)
    notification = Signal(str, str, QSystemTrayIcon.MessageIcon)
    log_line = Signal(str)

    def __init__(self, binary: str, args):
        super().__init__()
        self.binary = binary
        self.setProgram(binary)
        self.setArguments(args)
        self.setProcessChannelMode(QProcess.MergedChannels)
        self.readyReadStandardOutput.connect(self.handle_output)
        self.errorOccurred.connect(self.handle_process_error)
        self.finished.connect(self.handle_process_finish)

    def update_status(self, new_status: NodeStatus):
        new_status = str(new_status)
        log.debug('process change_status',
                  binary=self.binary,
                  new_status=new_status)
        self.current_status = new_status
        self.status.emit(new_status)

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

    def handle_process_error(self, error: QProcess.ProcessError):
        log.debug('process error', binary=self.binary, error=error)

    def handle_process_finish(self, exit_code: int,
                              exit_status: QProcess.ExitStatus):
        log.debug('process finish', binary=self.binary, exit_code=exit_code,
                  exit_status=exit_status)

        self.update_status(NodeStatus.STOPPED)
