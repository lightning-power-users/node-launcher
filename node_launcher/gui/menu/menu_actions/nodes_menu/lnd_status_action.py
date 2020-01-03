from node_launcher.gui.menu.menu_actions.menu_action import MenuAction
from node_launcher.node_set.lnd.lnd_node import LndNode


class LndStatusAction(MenuAction):
    def __init__(self, lnd_node: LndNode):
        super().__init__('Tor: off')
        self.setEnabled(False)
        self.lnd_node = lnd_node
        self.lnd_node.status.connect(self.update_text)

    def update_text(self, line):
        new_text = 'LND: ' + line.replace('_', ' ')
        self.setText(new_text)
