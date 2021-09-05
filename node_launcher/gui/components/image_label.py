from node_launcher.gui.qt import QtWidgets, Qt, QPixmap

from node_launcher.gui.assets import asset_access


class ImageLabel(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()

        self.setAlignment(Qt.AlignCenter | Qt.AlignCenter)

    def set_image(self, image_name: str):
        path = asset_access.get_asset_full_path(image_name)
        testnet_pixmap = QPixmap(path)
        self.setPixmap(testnet_pixmap)
