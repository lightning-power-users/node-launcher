from PySide2.QtWidgets import QColorDialog, QPushButton, QLineEdit

from node_launcher.gui.components.grid_layout import QGridLayout


class AliasLayout(QGridLayout):
    def __init__(self):
        super().__init__()
        self.alias_dialog = QLineEdit()
        self.color_dialog = QColorDialog()

        self.alias = None
        self.color = None

        self.alias_label = AliasLabel()
        self.color_label = ColorLabel()

        self.change_alias_button = QPushButton('Change Alias')
        self.change_alias_button.clicked.connect(
            lambda: self.
        )