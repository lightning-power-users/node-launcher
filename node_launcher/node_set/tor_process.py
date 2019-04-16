from PySide2.QtCore import Signal

from node_launcher.node_set.managed_process import ManagedProcess


class TorProcess(ManagedProcess):
    bootstrapped = Signal(bool)

    def __init__(self, binary: str, args):
        super().__init__(binary, args)

    def process_output_line(self, line: str):
        if 'Bootstrapped 100%: Done' in line:
            self.bootstrapped.emit(True)
