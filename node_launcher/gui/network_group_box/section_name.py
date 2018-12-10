from PySide2.QtWidgets import QLabel


class SectionName(QLabel):
    def __init__(self, text: str):
        super().__init__()
        self.setText(text)
