import sys

from PySide2.QtCore import Slot, QCoreApplication
from PySide2.QtWidgets import QApplication, QMenu

from node_launcher.gui.main_widget import MainWidget


class Application(QApplication):
    def __init__(self):
        super().__init__()
        self.aboutToQuit.connect(self.quit_app)

    @Slot()
    def quit_app(self):
        self.widget.network_widget.node_set.lnd.process.terminate()
        self.widget.network_widget.node_set.lnd.process.waitForFinished(2000)
        self.widget.network_widget.node_set.bitcoin.process.terminate()
        self.widget.network_widget.node_set.bitcoin.process.waitForFinished(2000)
        self.widget.network_widget.node_set.bitcoin.process.kill()

        QCoreApplication.exit(0)


if __name__ == '__main__':
    # sys.excepthook = except_hook

    app = Application()
    app.widget = MainWidget()

    menu = QMenu()

    bitcoind_output_action = menu.addAction('See Bitcoin Output')
    bitcoind_output_action.triggered.connect(app.widget.network_widget.nodes_layout.bitcoind_output_widget.show)

    lnd_output_action = menu.addAction('See LND Output')
    lnd_output_action.triggered.connect(app.widget.network_widget.nodes_layout.lnd_output_widget.show)

    quit_action = menu.addAction('Quit')
    quit_action.triggered.connect(lambda _: app.quit())
    app.widget.setContextMenu(menu)
    app.setQuitOnLastWindowClosed(False)
    app.widget.show()
    sys.exit(app.exec_())
