from node_launcher.gui.qt import QIcon, QAction


class MenuAction(QAction):
    def __init__(self, text: str, icon: QIcon = None, parent=None):
        if icon is not None:
            super().__init__(icon, parent)
        else:
            super().__init__(text, parent)
