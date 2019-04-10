from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QPushButton,
    QWidget
)

from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.gui.menu.manage_lnd.alias_layout import AliasLayout
from node_launcher.gui.menu.manage_lnd.lnd_ports_layout import LndPortsLayout
from node_launcher.gui.menu.manage_lnd.lnd_restart_layout import \
    LndRestartLayout
from node_launcher.node_set.lnd import Lnd


class LndConfigurationTab(QWidget):
    def __init__(self, lnd: Lnd):
        super().__init__()
        self.lnd = lnd
        self.layout = QGridLayout()

        self.alias_layout = AliasLayout()
        color = self.lnd.file['color']
        self.alias_layout.set_color(color)
        self.alias_layout.new_color.connect(
            lambda x: self.set_conf_value('color', x)
        )
        self.alias_layout.alias_editor.textEdited.connect(
            lambda x: self.set_conf_value('alias', x)
        )
        self.layout.addLayout(self.alias_layout, column_span=2)

        self.show_lnd_conf = QPushButton('Show lnd.conf')
        # noinspection PyUnresolvedReferences
        self.show_lnd_conf.clicked.connect(
            lambda: reveal(self.lnd.file.directory)
        )
        self.layout.addWidget(
            self.show_lnd_conf,
            same_row=True,
            column=self.columns
        )

        self.ports_layout = LndPortsLayout(lnd=self.lnd)
        self.layout.addLayout(self.ports_layout)

        self.restart_layout = LndRestartLayout(lnd=self.lnd)
        self.layout.addLayout(self.restart_layout)

        self.setLayout(self.layout)

    def set_conf_value(self, key: str, new_value: str):
        self.lnd.file[key] = new_value

    def show(self):
        if self.lnd.file['alias'] is not None:
            self.lnd_tab.alias_layout.set_alias(self.lnd.file['alias'])

        super().show()
        self.raise_()
        self.setWindowState(
            self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()
