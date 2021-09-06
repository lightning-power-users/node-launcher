from PySide2.QtCore import Qt
from PySide2.QtGui import QCursor
from PySide2.QtWidgets import QAction, QDialog, QGridLayout, QMenu, QTreeWidget, \
    QTreeWidgetItem

from node_launcher.logging import log

from node_launcher.node_set.lnd.lnd_client.lnd_client import LndClient, ln
from node_launcher.node_set.lnd.lnd_node import LndNode
from node_launcher.node_set.lnd.lnd_threaded_client import LndThreadedClient

class ChannelsDialog(QDialog):
    node: LndNode
    client: LndThreadedClient

    def __init__(self, lnd_client: LndClient):
        super().__init__()

        self.layout = QGridLayout()

        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(
            [
                'Identifier',
                'Status',
                'Capacity'
            ]
        )
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.open_menu)
        self.layout.addWidget(self.tree)

        self.setLayout(self.layout)

        self.client = LndThreadedClient(lnd_client=lnd_client)
        self.client.signals.result.connect(self.handle_list)
        self.client.signals.error.connect(self.handle_error)

        self.client.list_all_peers()

    def handle_error(self):
        self.client.list_all_peers()

    def handle_list(self, data):
        for pubkey in data.keys():
            new_peer_data, new_channels_data = data[pubkey]
            peers = self.tree.findItems(pubkey,
                                        Qt.MatchExactly | Qt.MatchRecursive, 0)
            if not len(peers):
                peer = QTreeWidgetItem()
                peer.setText(0, str(pubkey))
                self.tree.addTopLevelItem(peer)
            else:
                peer = peers[0]

            if new_peer_data is not None:
                peer.setText(1, 'Connected')
            else:
                peer.setText(1, 'Disconnected')

            for channel_data in new_channels_data:
                if isinstance(channel_data, ln.ChannelCloseSummary):
                    identifier = channel_data.channel_point
                else:
                    log.debug('channel_data',
                              channel_data_type=type(channel_data))
                    continue
                channels = self.tree.findItems(identifier,
                                               Qt.MatchExactly | Qt.MatchRecursive,
                                               0)


                if not len(channels):
                    channel = QTreeWidgetItem()
                    channel.setText(0, str(channel_data.chan_id))
                    peer.addChild(channel)
                else:
                    channel = channels[0]

                channel.setText(1, 'Open')
                channel.setText(2, str(channel_data.capacity))


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
        client = LndThreadedClient(lnd_client=self.client)
        client.signals.result.connect(self.handle_peers_list)
