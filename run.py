import os
import sys

from node_launcher.constants import (
    OPERATING_SYSTEM, NODE_LAUNCHER_RELEASE
)
from node_launcher.except_hook import except_hook
from node_launcher.gui.application import Application
from node_launcher.app_logging import log
from node_launcher.node_set.lib.constants import (
    TARGET_BITCOIN_RELEASE,
    TARGET_LND_RELEASE
)

if __name__ == '__main__':
    if not os.environ.get('NODE_LAUNCHER_EXCEPT_HOOK'):
        sys.excepthook = except_hook

    log.info(
        'constants',
        OPERATING_SYSTEM=OPERATING_SYSTEM,
        NODE_LAUNCHER_RELEASE=NODE_LAUNCHER_RELEASE,
        TARGET_BITCOIN_RELEASE=TARGET_BITCOIN_RELEASE,
        TARGET_LND_RELEASE=TARGET_LND_RELEASE
    )

    app = Application()
    sys.exit(app.start())
