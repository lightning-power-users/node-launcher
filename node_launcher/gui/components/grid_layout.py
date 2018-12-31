from PySide2 import QtWidgets
from PySide2.QtWidgets import QWidget


class QGridLayout(QtWidgets.QGridLayout):
    def __init__(self, *args, **kwargs):
        super(QGridLayout, self).__init__(*args, **kwargs)
        self.row_number = 1

    def addWidget(self,
                  widget: QWidget,
                  same_row: bool = False,
                  column: int = 1,
                  row_span: int = 1,
                  column_span: int = 1):
        if same_row:
            row = self.row_number - 1
        else:
            row = self.row_number
            self.row_number += 1
        super(QGridLayout, self).addWidget(widget,
                                           row,
                                           column,
                                           row_span,
                                           column_span)

    def addLayout(self,
                  widget: QWidget,
                  same_row: bool = False,
                  column: int = 1,
                  row_span: int = 1,
                  column_span: int = 1):
        if same_row:
            row = self.row_number - 1
        else:
            row = self.row_number
            self.row_number += 1
        super(QGridLayout, self).addLayout(widget,
                                           row,
                                           column,
                                           row_span,
                                           column_span)

