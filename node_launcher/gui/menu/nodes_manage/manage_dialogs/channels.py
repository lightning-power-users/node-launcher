from PySide2 import QtGui
from PySide2.QtCore import Qt, SIGNAL, QProcess, QByteArray, QTimer
from PySide2.QtGui import QCursor
from PySide2.QtWidgets import QDialog, QGridLayout, QTextEdit, QLineEdit, \
    QCompleter, QTableWidget, QTreeView, QTreeWidget, QTreeWidgetItem, QMenu

from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.data import JsonLexer

from node_launcher.gui.models.tree_model import TreeModel
from node_launcher.logging import log
from node_launcher.node_set.lnd.lnd_node import LndNode
from node_launcher.node_set.lnd.lnd_threaded_client import LndThreadedClient


class ChannelsDialog(QDialog):
    node: LndNode

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

        self.client = LndThreadedClient(self.node.configuration)
        self.client.signals.result.connect(self.handle_peers_list)
        self.timer = QTimer()
        self.timer.timeout.connect(self.recurring_timer)
        self.timer.setInterval(1000)
        self.timer.start()

    def recurring_timer(self):
        self.client.list_peers()

    def handle_peers_list(self, data):
        for peer_data in data['peers']:
            peer = QTreeWidgetItem()
            peer.setText(0, str(peer_data.remote_pubkey))
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

    def open_menu(self, position):
        indexes = self.tree.selectedIndexes()
        if len(indexes) > 0:
            level = 0
            index = indexes[0]
            while index.parent().isValid():
                index = index.parent()
                level += 1
        else:
            return

        menu = QMenu(self)
        if level == 0:
            menu.addAction('Close all channels', self)
        elif level == 1:
            menu.addAction('Close channel', self)
            renameAction.triggered.connect(lambda: self.renameSlot(event))
            self.menu.addAction(renameAction)

        menu.popup(QCursor.pos())
