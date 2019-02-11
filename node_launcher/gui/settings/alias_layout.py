from PySide2.QtGui import QPalette, QColor
from PySide2.QtWidgets import QColorDialog, QLineEdit, QLabel, QPushButton
from PySide2.QtCore import Signal

from node_launcher.gui.components.grid_layout import QGridLayout


class AliasLayout(QGridLayout):
    new_color = Signal(str)

    def __init__(self):
        super().__init__()

        self.alias_editor = QLineEdit()
        self.alias_editor.setMaxLength(32)
        # noinspection PyUnresolvedReferences
        self.alias_editor.returnPressed.connect(self.alias_editor.clearFocus)
        self.addWidget(QLabel('LN Node Alias'), column=1, column_span=1)
        self.addWidget(self.alias_editor, column=2, column_span=2,
                       same_row=True)

        self.addWidget(QLabel('LN Node Color'), column=1, column_span=1)
        self.color_label = QLabel()
        self.color_label.setAutoFillBackground(True)
        self.color_label.setFixedSize(10, 10)
        self.addWidget(self.color_label, column_span=1, column=2,
                       same_row=True)

        self.select_color_button = QPushButton('Select color')
        # noinspection PyUnresolvedReferences
        self.select_color_button.clicked.connect(self.select_color)
        self.addWidget(self.select_color_button, column=3, column_span=1,
                       same_row=True)

        self.color_dialog = QColorDialog(self.parentWidget())

    def select_color(self):
        color = self.color_dialog.getColor()
        if color.isValid():
            self.set_palette(color)
            self.color_dialog.setCurrentColor(color)
            # noinspection PyUnresolvedReferences
            self.new_color.emit(color.name())

    def set_alias(self, text: str):
        self.alias_editor.setText(text)

    def set_color(self, color_hex: str):
        color = QColor(color_hex)
        if color.isValid():
            self.set_palette(color)
            self.color_dialog.setCurrentColor(color)

    def set_palette(self, color: QColor):
        palette = self.color_label.palette()
        palette.setColor(QPalette.Background, color)
        self.color_label.setPalette(palette)
