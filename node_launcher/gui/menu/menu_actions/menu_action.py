from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QAction


class MenuAction(QAction):
    def __init__(self, text: str, icon: QIcon = None, parent=None):
        super().__init__(icon, text, parent)
