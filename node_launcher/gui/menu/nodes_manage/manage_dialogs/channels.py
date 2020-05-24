from PySide2.QtCore import Qt
from PySide2.QtGui import QCursor
from PySide2.QtWidgets import QAction, QDialog, QGridLayout, QMenu, QTreeWidget, \
    QTreeWidgetItem

from node_launcher.node_set.lib.node_status import NodeStatus
from node_launcher.node_set.lnd.lnd_node import LndNode
from node_launcher.node_set.lnd.lnd_threaded_client import LndThreadedClient


class ChannelsDialog(QDialog):
    node: LndNode
    client: LndThreadedClient

    def __init__(self, node: LndNode):
        super().__init__()

        self.node = node

        self.layout = QGridLayout()

        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(['ID', 'Status', 'Capacity'])
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.open_menu)
        self.layout.addWidget(self.tree)

        self.setLayout(self.layout)

        self.node.status.connect(
            self.handle_lnd_node_status_change
        )

        self.client = LndThreadedClient(self.node.configuration)
        self.client.signals.result.connect(self.handle_list)
        self.client.signals.error.connect(self.handle_error)

    def handle_lnd_node_status_change(self, status):
        if status == NodeStatus.SYNCED:
            self.client.list_all()

    def handle_error(self):
        self.client.list_all()

    def handle_list(self, data):
        for peer_data in data['peers']:
            peers = self.tree.findItems(peer_data.pub_key,
                                        Qt.MatchExactly | Qt.MatchRecursive, 0)
            if not len(peers):
                peer = QTreeWidgetItem()
                peer.setText(0, str(peer_data.pub_key))
                peer.setText(1, 'Connected')
                self.tree.addTopLevelItem(peer)

        for open_channel_data in data['open_channels']:
            peers = self.tree.findItems(open_channel_data.remote_pubkey,
                                        Qt.MatchExactly | Qt.MatchRecursive, 0)
            if not len(peers):
                peer = QTreeWidgetItem()
                peer.setText(0, str(open_channel_data.remote_pubkey))
                peer.setText(1, 'Disconnected')
                self.tree.addTopLevelItem(peer)
            else:
                peer = peers[0]

            channels = self.tree.findItems(str(open_channel_data.chan_id),
                                           Qt.MatchExactly | Qt.MatchRecursive,
                                           0)
            if not len(channels):
                channel = QTreeWidgetItem()
                channel.setText(0, str(open_channel_data.chan_id))
                peer.addChild(channel)
            else:
                channel = channels[0]

            channel.setText(1, 'Open')
            channel.setText(2, str(open_channel_data.capacity))

        for closed_channel_data in data['closed_channels']:
            peers = self.tree.findItems(closed_channel_data.remote_pubkey,
                                        Qt.MatchExactly | Qt.MatchRecursive, 0)
            if not len(peers):
                peer = QTreeWidgetItem()
                peer.setText(0, str(closed_channel_data.remote_pubkey))
                peer.setText(1, 'Disconnected')
                self.tree.addTopLevelItem(peer)
            else:
                peer = peers[0]

            channels = self.tree.findItems(str(closed_channel_data.chan_id),
                                           Qt.MatchExactly | Qt.MatchRecursive,
                                           0)
            if not len(channels):
                channel = QTreeWidgetItem()
                channel.setText(0, str(closed_channel_data.chan_id))
                peer.addChild(channel)
            else:
                channel = channels[0]

            channel.setText(1, 'Closed')
            channel.setText(2, str(closed_channel_data.capacity))

    def open_menu(self, event):
        indexes = self.tree.selectedIndexes()
        if len(indexes) > 0:
            level = 0
            index = child_index = indexes[0]
            while index.parent().isValid():
                index = index.parent()
                level += 1
        else:
            return

        item = self.tree.itemFromIndex(child_index)

        menu = QMenu(self)
        if level == 0:
            close_channels_action = QAction('Close all channels', self)
            menu.addAction(close_channels_action)
        elif level == 1:
            close_channel_action = QAction('Close channel', self)
            chan_id = int(item.data(0, 0))
            close_channel_action.triggered.connect(lambda: self.close_channel(chan_id))
            menu.addAction(close_channel_action)

        menu.popup(QCursor.pos())

    def close_channel(self, chan_id: int):
        client = LndThreadedClient(self.node.configuration)
        client.signals.result.connect(self.handle_peers_list)
