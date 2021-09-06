from node_launcher.gui.menu.menu_actions.menu_action import MenuAction
from node_launcher.gui.menu.nodes_manage.nodes_manage import NodesManageDialog
from node_launcher.node_set import NodeSet


class NodeManageAction(MenuAction):
    def __init__(self, node_set: NodeSet, system_tray, parent):
        super().__init__(text='Manage Nodes', parent=parent)
        self.setText('Manage Nodes')
        self.node_set = node_set
        self.system_tray = system_tray
        self.nodes_manage_dialog = NodesManageDialog(
            node_set=self.node_set,
            system_tray=self.system_tray,
            parent=parent
        )
        self.triggered.connect(
            self.nodes_manage_dialog.show
        )
