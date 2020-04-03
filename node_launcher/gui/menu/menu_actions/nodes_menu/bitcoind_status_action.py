from typing import Optional

from node_launcher.gui.menu.menu_actions.menu_action import MenuAction
from node_launcher.node_set.bitcoind.bitcoind_node import BitcoindNode


class BitcoindStatusAction(MenuAction):
    def __init__(self, bitcoind_node: Optional[BitcoindNode]):
        super().__init__('Bitcoind: off')
        self.setEnabled(False)
        self.bitcoind_node = bitcoind_node
        if self.bitcoind_node:
            self.bitcoind_node.status.connect(self.update_text)
        else:
            self.setVisible(False)

    def update_text(self, line):
        new_text = 'Bitcoind: ' + line.replace('_', ' ')
        self.setText(new_text)
