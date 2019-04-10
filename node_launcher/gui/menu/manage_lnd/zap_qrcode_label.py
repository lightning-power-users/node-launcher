from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QLabel


class ZapQrcodeLabel(QLabel):
    def __init__(self, lndconnect_qrcode):
        super().__init__()
        lndconnect_qrcode.save('qrcode.png', 'PNG')

        pixmap = QPixmap('qrcode.png')
        pixmap = pixmap.scaledToWidth(400)
        self.setWindowTitle('Zap QR Code')
        self.resize(400, 400)
        self.setPixmap(pixmap)
