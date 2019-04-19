from PySide2.QtCore import Signal, QObject


class NetworkNode(QObject):
    status = Signal(str)

    def __init__(self):
        super().__init__()
