from typing import Optional

from node_launcher.gui.menu.menu_actions.menu_action import MenuAction
from node_launcher.node_set.bitcoind.bitcoind_node import BitcoindNode


class BitcoindStatusAction(MenuAction):
    def __init__(self, bitcoind_node: Optional[BitcoindNode], parent):
        super().__init__(text='Bitcoind: off', parent=parent)
        self.setEnabled(False)
        self.bitcoind_node = bitcoind_node
        self.bitcoind_node.status.connect(self.update_text)
        self.setVisible(False)

    def update_text(self, line):
        new_text = 'Bitcoind: ' + line.replace('_', ' ')
        self.setText(new_text)

        if line == 'synced':
            self.setVisible(False)
        if line != 'synced' and not self.isVisible():
            self.setVisible(True)
