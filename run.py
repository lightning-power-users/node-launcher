import sys

from node_launcher.gui.application import Application

if __name__ == '__main__':
    # sys.excepthook = except_hook
    app = Application()
    sys.exit(app.exec_())
