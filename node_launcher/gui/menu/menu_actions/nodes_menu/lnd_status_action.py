from node_launcher.gui.menu.menu_actions.menu_action import MenuAction
from node_launcher.node_set.lib.node_status import NodeStatus
from node_launcher.node_set.lnd.lnd_node import LndNode


class LndStatusAction(MenuAction):
    def __init__(self, lnd_node: LndNode, parent):
        super().__init__(text='Tor: off', parent=parent)
        self.setEnabled(False)
        self.lnd_node = lnd_node
        self.lnd_node.status.connect(self.update_text)
        self.setVisible(False)

    def update_status(self, new_status: NodeStatus):
        new_text = 'LND: ' + new_status.description
        self.setText(new_text)
        self.setVisible(True)
