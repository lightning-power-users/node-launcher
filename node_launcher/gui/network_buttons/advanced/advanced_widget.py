from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget

from node_launcher.gui.network_buttons.advanced.zap_layout import ZapLayout
from .configuration_files_layout import ConfigurationFilesLayout
from .ports_layout import PortsLayout
from .tls_layout import TlsLayout
from .versions_layout import VersionsLayout
from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.gui.components.horizontal_line import HorizontalLine
from node_launcher.node_set import NodeSet


class AdvancedWidget(QWidget):
    def __init__(self, node_set: NodeSet):
        super().__init__()
        self.setWindowTitle('Advanced')
        self.node_set = node_set

        self.columns = 2

        self.layout = QGridLayout()

        self.versions_layout = VersionsLayout(node_set=node_set)
        self.ports_layout = PortsLayout(node_set=node_set)
        self.actions_layout = ConfigurationFilesLayout(node_set=node_set)
        self.zap_layout = ZapLayout(node_set=self.node_set)
        self.tls_layout = TlsLayout(node_set=self.node_set)

        self.layout.addLayout(self.versions_layout, column_span=self.columns)
        self.layout.addWidget(HorizontalLine(), column_span=self.columns)
        self.layout.addLayout(self.ports_layout, column_span=self.columns)
        self.layout.addWidget(HorizontalLine(), column_span=self.columns)
        self.layout.addLayout(self.actions_layout, column_span=self.columns)
        self.layout.addWidget(HorizontalLine(), column_span=self.columns)
        self.layout.addLayout(self.zap_layout, column_span=self.columns)
        self.layout.addWidget(HorizontalLine(), column_span=self.columns)
        self.layout.addLayout(self.tls_layout, column_span=self.columns)

        self.setLayout(self.layout)

    def show(self):
        super().show()
        self.raise_()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()
