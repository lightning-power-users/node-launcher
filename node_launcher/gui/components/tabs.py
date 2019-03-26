from PySide2.QtWidgets import QTabWidget, QWidget

from node_launcher.gui.network_buttons.network_widget import NetworkWidget


class Tabs(QTabWidget):
    def __init__(self, network_widget: NetworkWidget):
        super(Tabs, self).__init__()
        self.setTabPosition(QTabWidget.North)
        self.addTab(network_widget, 'Network')
