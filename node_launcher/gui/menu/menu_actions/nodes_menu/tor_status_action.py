from node_launcher.gui.menu.menu_actions.menu_action import MenuAction
from node_launcher.node_set.tor.tor_node import TorNode


class TorStatusAction(MenuAction):
    def __init__(self, tor_node: TorNode):
        super().__init__('Tor: off')
        self.setEnabled(False)
        self.tor_node = tor_node
        self.tor_node.status.connect(self.update_text)

    def update_text(self, line):
        new_text = 'Tor: ' + line.replace('_', ' ')
        self.setText(new_text)
