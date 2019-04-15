from PySide2.QtCore import Signal

from node_launcher.gui.components.output_widget import OutputWidget
from node_launcher.node_set.tor import Tor


class TorOutput(OutputWidget):
    tor_bootstrapped = Signal(bool)

    def __init__(self, tor: Tor):
        super().__init__('tor')
        self.tor = tor
        self.process = tor.process

        self.process.readyReadStandardOutput.connect(self.handle_output)
        self.setWindowTitle('Tor Output')

    def process_output_line(self, line: str):
        if 'Bootstrapped 100%: Done' in line:
            self.tor_bootstrapped.emit(True)
