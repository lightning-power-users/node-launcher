from PySide2.QtWidgets import QAction


class SeparatorAction(QAction):
    def __init__(self):
        super().__init__()
        self.setSeparator(True)
