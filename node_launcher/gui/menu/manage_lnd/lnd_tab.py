from PySide2.QtWidgets import QWidget

from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.gui.menu.manage_lnd.alias_layout import AliasLayout
from node_launcher.node_set.lnd import Lnd


class LndTab(QWidget):
    def __init__(self, lnd: Lnd):
        super().__init__()

        self.lnd = lnd
        self.alias_layout = AliasLayout()

        color = self.lnd.file['color']
        self.alias_layout.set_color(color)
        self.alias_layout.new_color.connect(
            lambda x: self.set_conf_value('color', x)
        )

        self.alias_layout.alias_editor.textEdited.connect(
            lambda x: self.set_conf_value('alias', x)
        )
        self.lnd_layout = QGridLayout()
        self.lnd_layout.addLayout(self.alias_layout, column_span=2)

        self.setLayout(self.lnd_layout)

    def set_conf_value(self, key: str, new_value: str):
        self.lnd.file[key] = new_value

