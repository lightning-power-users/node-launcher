import sys

from PySide2 import QtWidgets

from node_launcher.gui.main_widget import MainWidget

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MainWidget()

    widget.show()

    sys.exit(app.exec_())
