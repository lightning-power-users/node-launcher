import sys

from node_launcher.constants import (
    OPERATING_SYSTEM, NODE_LAUNCHER_RELEASE,
    TARGET_BITCOIN_RELEASE, TARGET_LND_RELEASE
)
from node_launcher.gui.application import Application
from node_launcher.logging import log

if __name__ == '__main__':
    # sys.excepthook = except_hook

    log.info(
        'constants',
        OPERATING_SYSTEM=OPERATING_SYSTEM,
        NODE_LAUNCHER_RELEASE=NODE_LAUNCHER_RELEASE,
        TARGET_BITCOIN_RELEASE=TARGET_BITCOIN_RELEASE,
        TARGET_LND_RELEASE=TARGET_LND_RELEASE
    )

    app = Application()
    sys.exit(app.exec_())
