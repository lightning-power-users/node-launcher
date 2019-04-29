from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QPushButton,
    QWidget
)

from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.gui.components.horizontal_line import HorizontalLine
from node_launcher.gui.components.selectable_text import SelectableText
from node_launcher.gui.menu.manage_lnd.alias_layout import AliasLayout
from node_launcher.gui.menu.manage_lnd.lnd_restart_layout import \
    LndRestartLayout
from node_launcher.gui.menu.manage_lnd.tls_layout import TlsLayout
from node_launcher.gui.utilities import reveal
from node_launcher.node_set.lnd.lnd_node import LndNode


class LndConfigurationTab(QWidget):
    def __init__(self, lnd_node: LndNode):
        super().__init__()
        self.lnd_node = lnd_node
        self.layout = QGridLayout()

        self.lnd_version = SelectableText(
            f'LND '
            f'version {self.lnd_node.software.release_version}'
        )
        self.layout.addWidget(self.lnd_version)

        self.alias_layout = AliasLayout()
        self.alias_layout.new_color.connect(
            lambda x: self.set_conf_value('color', x)
        )
        self.alias_layout.alias_editor.textEdited.connect(
            lambda x: self.set_conf_value('alias', x)
        )
        self.layout.addLayout(self.alias_layout)

        self.layout.addWidget(HorizontalLine())

        self.restart_layout = LndRestartLayout(lnd=self.lnd_node)
        self.layout.addLayout(self.restart_layout)

        self.tls_layout = TlsLayout(lnd=self.lnd_node)
        self.layout.addLayout(self.tls_layout)

        self.show_lnd_conf = QPushButton('Show lnd.conf')
        self.show_lnd_conf.clicked.connect(
            lambda: reveal(self.lnd_node.configuration.file.directory)
        )
        self.layout.addWidget(self.show_lnd_conf)

        self.setLayout(self.layout)

    def set_conf_value(self, key: str, new_value: str):
        self.lnd_node.file[key] = new_value

    def show(self):

        super().show()
        self.raise_()
        self.setWindowState(
            self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()
