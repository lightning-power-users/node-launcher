from node_launcher.gui.menu.menu_actions.menu_action import MenuAction
from node_launcher.node_set.tor.tor_node import TorNode


class TorStatusAction(MenuAction):
    def __init__(self, tor_node: TorNode, parent):
        super().__init__(text='Tor: off', parent=parent)
        self.setEnabled(False)
        self.tor_node = tor_node
        self.tor_node.status.connect(self.update_status)

    def update_status(self, line: str):
        if line == 'synced':
            self.setVisible(False)
            return
        new_text = 'Tor: ' + line.replace('_', ' ')
        self.setText(new_text)
        if not self.isVisible():
            self.setVisible(True)
