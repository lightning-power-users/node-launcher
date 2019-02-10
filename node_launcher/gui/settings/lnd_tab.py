from PySide2.QtWidgets import QWidget

from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.gui.settings.alias_layout import AliasLayout
from node_launcher.node_set.lnd import Lnd


class LndTab(QWidget):
    def __init__(self, lnd: Lnd):
        super().__init__()

        self.lnd = lnd
        self.alias_layout = AliasLayout()
        if self.lnd.file['alias'] is not None:
            self.alias_layout.set_alias(self.lnd.file['alias'])

        color = self.lnd.file['color']
        self.alias_layout.set_color(color)
        self.alias_layout.new_color.connect(
            self.set_new_color
        )

        self.alias_layout.alias_editor.textEdited.connect(
            self.set_new_alias
        )
        self.lnd_layout = QGridLayout()
        self.lnd_layout.addLayout(self.alias_layout, column_span=2)

        self.setLayout(self.lnd_layout)

    def set_new_alias(self, new_alias: str):
        self.lnd.file['alias'] = new_alias

    def set_new_color(self, new_color: str):
        self.lnd.file['color'] = new_color
