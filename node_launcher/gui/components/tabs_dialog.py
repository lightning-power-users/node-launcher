from PySide2.QtWidgets import QDialog, QTabWidget


class TabsDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.tab_widget = QTabWidget()

        self.tab_widget.currentChanged.connect(
            self.tab_changed_event
        )

    def tab_changed_event(self, tab_index: int):
        if tab_index == 0:
            self.console_tab.input.setFocus()
