from PySide2 import QtWidgets
from PySide2.QtGui import QPainter
from PySide2.QtPrintSupport import QPrinter, QPrintDialog
from PySide2.QtWidgets import QDialog, QTextBrowser, QPushButton


class SeedDialog(QDialog):
    def __init__(self, parent=None):
        super(SeedDialog, self).__init__(parent)
        self.setWindowTitle('Mnemonic')

        self.layout = QtWidgets.QVBoxLayout()

        self.text = QTextBrowser(self)
        self.layout.addWidget(self.text)

        self.print_button = QPushButton('Print')
        self.layout.addWidget(self.print_button)
        self.print_button.clicked.connect(self.print)

        self.setLayout(self.layout)

    def show(self):
        self.exec_()

    def print(self):
        printer = QPrinter()
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
