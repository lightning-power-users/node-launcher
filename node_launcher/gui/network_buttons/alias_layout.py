from PySide2.QtGui import QPalette
from PySide2.QtWidgets import QColorDialog, QLineEdit, QLabel, QPushButton

from node_launcher.gui.components.grid_layout import QGridLayout


class AliasLayout(QGridLayout):
    def __init__(self):
        super().__init__()

        self.alias_editor = QLineEdit()
        self.alias_editor.setMaxLength(32)
        self.alias_editor.returnPressed.connect(
            self.alias_editor.clearFocus
        )
        self.addWidget(QLabel('LN Node Alias'), column=1, column_span=1)
        self.addWidget(self.alias_editor, column=2, column_span=1,
                       same_row=True)

        self.select_color_button = QPushButton('Select color')
        self.select_color_button.clicked.connect(self.select_color)
        self.addWidget(self.select_color_button, column=1, column_span=1)

        self.color_label = QLabel()
        self.color_label.setAutoFillBackground(True)
        self.color_label.setFixedSize(10, 10)
        self.addWidget(self.color_label, column_span=2, column=2,
                       same_row=True)

    def select_color(self):
        color = QColorDialog(self.parentWidget()).getColor()
        if color.isValid():
            palette = self.color_label.palette()
            palette.setColor(QPalette.Background, color)
            self.color_label.setPalette(palette)
