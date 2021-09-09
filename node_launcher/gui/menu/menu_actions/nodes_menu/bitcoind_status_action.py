from typing import Optional

from node_launcher.gui.menu.menu_actions.menu_action import MenuAction
from node_launcher.node_set.bitcoind.bitcoind_node import BitcoindNode


class BitcoindStatusAction(MenuAction):
    def __init__(self, bitcoind_node: Optional[BitcoindNode], parent):
        super().__init__(text='Bitcoind: off', parent=parent)
        self.setEnabled(False)
        self.bitcoind_node = bitcoind_node
        self.bitcoind_node.status.connect(self.update_status)
        self.setVisible(False)

    def update_status(self, line: str):
        if line == 'synced':
            self.setVisible(False)
            return
        new_text = 'Bitcoind: '
        if line == 'syncing':
            new_text += self.bitcoind_node.process.current_description
        else:
            new_text += line.replace('_', ' ')
        self.setText(new_text)
        if not self.isVisible():
            self.setVisible(True)
