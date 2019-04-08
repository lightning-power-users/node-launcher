from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QDialogButtonBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget
)

from node_launcher.gui.menu.manage_lnd.lnd_tab import LndTab
from node_launcher.node_set import NodeSet


class LndConfigurationTab(QWidget):
    def __init__(self, node_set: NodeSet, parent=None):
        super().__init__(parent=parent)
        self.node_set = node_set
        self.tab_widget = QTabWidget()


        self.lnd_tab = LndTab(self.node_set.lnd)
        self.tab_widget.addTab(self.lnd_tab, 'LND')

        self.button_box = QDialogButtonBox()
        self.button_box.addButton('Ok', QDialogButtonBox.AcceptRole)

        self.button_box.accepted.connect(self.accept)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.tab_widget)
        self.main_layout.addWidget(self.button_box)

        self.show_lnd_conf = QPushButton('Show lnd.conf')
        # noinspection PyUnresolvedReferences
        self.show_lnd_conf.clicked.connect(
            lambda: reveal(self.node_set.lnd.file.directory)
        )
        self.addWidget(self.show_lnd_conf, same_row=True, column=self.columns)

        self.setLayout(self.main_layout)

        self.setWindowTitle('Settings')

    def show(self):
        if self.node_set.lnd.file['alias'] is not None:
            self.lnd_tab.alias_layout.set_alias(self.node_set.lnd.file['alias'])

        super().show()
        self.raise_()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()
