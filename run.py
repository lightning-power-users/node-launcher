import sys

from PySide2 import QtWidgets

from node_launcher.gui.main_widget import MainWidget
from node_launcher.utilities.except_hook import except_hook

if __name__ == '__main__':
    sys.excepthook = except_hook

    app = QtWidgets.QApplication([])
    widget = MainWidget()
    widget.show()
    sys.exit(app.exec_())
