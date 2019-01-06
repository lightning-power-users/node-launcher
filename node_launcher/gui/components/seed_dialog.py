from PySide2 import QtWidgets
from PySide2.QtCore import Qt
from PySide2.QtGui import QPainter, QColor
from PySide2.QtPrintSupport import QPrinter, QPrintDialog
from PySide2.QtWidgets import QDialog, QTextBrowser, QPushButton


class SeedDialog(QDialog):
    def __init__(self, parent=None):
        super(SeedDialog, self).__init__(parent)
        self.setWindowTitle('Mnemonic')

        self.layout = QtWidgets.QVBoxLayout()

        self.text = QTextBrowser(self)
        self.text.setMinimumHeight(500)
        self.layout.addWidget(self.text)

        self.print_button = QPushButton('Print')
        self.layout.addWidget(self.print_button)
        # noinspection PyUnresolvedReferences
        self.print_button.clicked.connect(self.print)

        self.setLayout(self.layout)

    def show(self):
        self.exec_()

    def print(self):
        printer = QPrinter()
        print_program = printer.printProgram()
        printer_name = printer.printerName()
        # Create painter
        painter = QPainter()
        # Start painter
        painter.begin(printer)
        # Grab a widget you want to print
        screen = self.text.grab()
        # Draw grabbed pixmap
        painter.drawPixmap(10, 10, screen)
        # End painting
        painter.end()

        print_dialog = QPrintDialog(printer, self)
        print_dialog.exec_()

    def set_text(self, text: str):
        self.text.setText(text)
        self.text.selectAll()
        self.text.setTextColor(Qt.black)
        self.text.setTextBackgroundColor(Qt.white)
