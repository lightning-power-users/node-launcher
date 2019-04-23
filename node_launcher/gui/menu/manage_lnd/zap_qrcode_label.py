from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QLabel

from node_launcher.node_set.lnd.lnd_configuration import LndConfiguration


class ZapQrcodeLabel(QLabel):
    def __init__(self, configuration: LndConfiguration):
        super().__init__()
        self.configuration = configuration

    def populate(self):
        self.configuration.lndconnect_qrcode.save('qrcode.png', 'PNG')
        pixmap = QPixmap('qrcode.png')
        pixmap = pixmap.scaledToWidth(400)
        self.setWindowTitle('Zap QR Code')
        self.resize(400, 400)
        self.setPixmap(pixmap)
