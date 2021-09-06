from node_launcher.gui.menu.menu_actions.menu_action import MenuAction
from node_launcher.node_set.lnd.lnd_node import LndNode


class LndStatusAction(MenuAction):
    def __init__(self, lnd_node: LndNode, parent):
        super().__init__(text='Tor: off', parent=parent)
        self.setEnabled(False)
        self.lnd_node = lnd_node
        self.lnd_node.status.connect(self.update_text)

    def update_text(self, line):
        new_text = 'LND: ' + line.replace('_', ' ')
        if line != 'synced':
            self.setText(new_text)
        else:
            self.lnd_node.client
