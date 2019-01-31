import sys
import time
import traceback
from io import StringIO

from PySide2 import QtWidgets
from PySide2.QtWidgets import QMessageBox

from node_launcher.constants import NODE_LAUNCHER_RELEASE
from node_launcher.gui.main_widget import MainWidget


def excepthook(excType, excValue, tracebackobj):
    '''
    Global function to catch unhandled exceptions.

    @param excType exception type
    @param excValue exception value
    @param tracebackobj traceback object
    '''
    separator = '-' * 80
    time_string = time.strftime('%Y-%m-%d, %H:%M:%S')
    email = 'support@lightningpowerusers.zendesk.com'
    notice = f'''
        An unhandled exception occurred. Please report the problem\n
        on GitHub or via email to {email}.\n
        Error information:\n
        '''

    error_message = f'{excType}: \n{excValue}'

    traceback_io = StringIO()
    traceback.print_tb(tracebackobj, None, traceback_io)
    traceback_io.seek(0)
    traceback_info = traceback_io.read()
    sections = [
        separator,
        time_string,
        separator,
        error_message,
        separator,
        traceback_info
    ]
    msg = '\n'.join(sections)
    errorbox = QMessageBox()
    errorbox.setText(str(notice) + str(msg) + str(NODE_LAUNCHER_RELEASE))
    errorbox.exec_()
    sys.exit(1)


if __name__ == '__main__':
    sys.excepthook = excepthook

    app = QtWidgets.QApplication([])

    widget = MainWidget()

    widget.show()

    sys.exit(app.exec_())
