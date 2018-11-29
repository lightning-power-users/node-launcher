from PySide2.QtCore import Qt
from PySide2.QtWidgets import QLabel, QWidget

from node_launcher.constants import LPU_ADVERTISEMENT


class AdvertisementLabel(QLabel):
    def __init__(self, parent_widget: QWidget):
        super().__init__(parent_widget)
        self.setOpenExternalLinks(True)
        self.setFixedHeight(self.height() * 2)
        self.setText(LPU_ADVERTISEMENT)
        self.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
