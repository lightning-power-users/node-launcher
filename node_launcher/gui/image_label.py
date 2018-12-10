from PySide2 import QtWidgets
from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap

from node_launcher.assets.asset_access import asset_access


class ImageLabel(QtWidgets.QLabel):
    def __init__(self, image_name: str):
        super().__init__()
        path = asset_access.get_asset_full_path(image_name)
        testnet_pixmap = QPixmap(path)
        self.setPixmap(testnet_pixmap)

        self.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
