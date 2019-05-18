import os

from PySide2.QtCore import QProcess, QByteArray, Signal, QProcessEnvironment
from PySide2.QtWidgets import QSystemTrayIcon
from node_launcher.constants import IS_LINUX

from node_launcher.logging import log
from node_launcher.node_set.lib.node_status import NodeStatus


class ManagedProcess(QProcess):
    status = Signal(str)
    sync_progress = Signal(str)
    notification = Signal(str, str, QSystemTrayIcon.MessageIcon)
    log_line = Signal(str)

    def __init__(self, binary: str, args):
        super().__init__()
        self.binary = binary
        self.args = args
        self.setProgram(binary)
        self.setArguments(args)
        self.setProcessChannelMode(QProcess.MergedChannels)
        self.readyReadStandardOutput.connect(self.handle_output)
        self.errorOccurred.connect(self.handle_process_error)
        self.finished.connect(self.handle_process_finish)
        self.expecting_shutdown = False
        self.current_status = None

        if IS_LINUX:
            env = QProcessEnvironment.systemEnvironment()
            env.insert('LD_LIBRARY_PATH', os.path.abspath(os.path.join(binary, os.pardir)))
            self.setProcessEnvironment(env)

    def update_status(self, new_status: NodeStatus):
        log.debug('update_status',
                  binary=self.binary,
                  new_status=new_status,
                  current_status=self.current_status)
        self.current_status = new_status
        self.status.emit(str(new_status))

    def process_output_line(self, line):
        pass

    def handle_output(self):
        while self.canReadLine():
            line_bytes: QByteArray = self.readLine()
            try:
                line_str = line_bytes.data().decode('utf-8').strip()
            except UnicodeDecodeError:
                log.error('handle_output decode error', exc_info=True)
                continue
            log.debug(f'Process output', line=line_str, binary=self.binary)
            self.process_output_line(line_str)
            self.log_line.emit(line_str)

    def handle_process_error(self, error: QProcess.ProcessError):
        log.debug('process error', binary=self.binary, error=error)

    def handle_process_finish(self, exit_code: int,
                              exit_status: QProcess.ExitStatus):
        log.debug('process finish', binary=self.binary, exit_code=exit_code,
                  exit_status=exit_status)
        self.update_status(NodeStatus.STOPPED)
