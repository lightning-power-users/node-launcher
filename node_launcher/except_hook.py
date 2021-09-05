import sys
import traceback
from io import StringIO

from node_launcher.gui.qt import Qt, QMessageBox

from node_launcher.constants import NODE_LAUNCHER_RELEASE


def except_hook(exception_type, exception_value, traceback_object):
    notice = f'''Wild bug appears! <br>
Please copy this text and <a href="https://github.com/lightning-power-users/node-launcher/issues/new">open an issue on GitHub</a>.<br>
Node Launcher version {NODE_LAUNCHER_RELEASE}<br><br>
Error information:'''

    traceback_io = StringIO()
    traceback.print_tb(traceback_object, None, traceback_io)
    traceback_io.seek(0)
    traceback_info = traceback_io.read()

    sections = [
        notice,
        str(exception_type),
        str(exception_value),
        traceback_info
    ]
    msg = '<br>'.join(sections)
    error_message = QMessageBox()
    error_message.setTextFormat(Qt.RichText)
    error_message.setTextInteractionFlags(Qt.TextSelectableByMouse)
    error_message.setFixedWidth(800)
    error_message.setText(msg)
    error_message.exec_()
    sys.exit(1)


if __name__ == '__main__':
    from node_launcher.gui.qt import QtWidgets
    sys.excepthook = except_hook

    app = QtWidgets.QApplication([])
    raise Exception()
