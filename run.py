import sys

from PySide2 import QtWidgets

from node_launcher.gui.launch_widget import LaunchWidget

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    widget = LaunchWidget()
    widget.show()

    sys.exit(app.exec_())
