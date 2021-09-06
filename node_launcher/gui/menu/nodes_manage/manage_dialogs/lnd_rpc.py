from functools import partial

from google.protobuf.json_format import MessageToDict

from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.gui.qt import Qt, QCursor, QAction, QDialog, QMenu, QTreeWidget, \
    QTreeWidgetItem, QGroupBox, QPushButton
from node_launcher.logging import log

from node_launcher.node_set.lnd.lnd_client import LndClient
from node_launcher.node_set.lnd.lnd_client.v0131beta.rpc_pb2_grpc import LightningStub, LightningServicer, Lightning
from node_launcher.node_set.lnd.lnd_node import LndNode
from node_launcher.node_set.lnd.lnd_threaded_client import LndThreadedClient

from node_launcher.node_set.lnd.lnd_client.v0131beta import rpc_pb2 as ln


class LndRpcDialog(QDialog):
    node: LndNode
    client: LndThreadedClient

    def __init__(self, node: LndNode = None, client: LndClient = None):
        super().__init__()
        self.node = node
        self.layout = QGridLayout()
        self.command_map = {
            'AddInvoice': 'Invoice',
            'ChannelAcceptor': 'ChannelAcceptResponse',
            'DecodePayReq': 'PayReqString',
            'DescribeGraph': 'ChannelGraphRequest',
            'ExportAllChannelBackups': 'ChanBackupExportRequest',
            'FundingStateStep': 'FundingTransitionMsg',
            'GetChanInfo': 'ChanInfoRequest',
            'GetNetworkInfo': 'NetworkInfoRequest',
            'GetNodeInfo': 'NodeInfoRequest',
            'GetNodeMetrics': 'NodeMetricsRequest',
            'ListInvoices': 'ListInvoiceRequest',
            'LookupInvoice': 'PaymentHash',
            'OpenChannelSync': 'OpenChannelRequest',
            'RestoreChannelBackups': 'RestoreChanBackupRequest',
            'SendPayment': 'SendRequest',
            'SendPaymentSync': 'SendRequest',
            'SendToRouteSync': 'SendToRouteRequest',
            'StopDaemon': 'StopRequest',
            'SubscribeChannelBackups': 'ChannelBackupSubscription',
            'SubscribeChannelEvents': 'ChannelEventSubscription',
            'SubscribeChannelGraph': 'GraphTopologySubscription',
            'SubscribeInvoices': 'InvoiceSubscription',
            'SubscribePeerEvents': 'PeerEventSubscription',
            'SubscribeTransactions': 'GetTransactionsRequest',
            'UpdateChannelPolicy': 'PolicyUpdateRequest',
            'VerifyChanBackup': 'ChanBackupSnapshot'
        }

        self.node.status.connect(self.update_buttons)
        if client is None:
            self.client = node.client
        else:
            self.client = client
    def update_buttons(self, status):
        if status != 'synced':
            print(status)
            return
        commands = [c for c in dir(Lightning) if not c.startswith('_')]
        command_outline = {}
        for command in commands:
            if command in self.command_map:
                request_object_name = self.command_map[command]
            else:
                request_object_name = f'{command}Request'
            request = getattr(ln, request_object_name)
            fields = request.DESCRIPTOR.fields
            command_outline[request_object_name] = {}
            for field in fields:
                command_outline[request_object_name][field.name] = {
                    'has_default_value': field.has_default_value,
                    'default_value': field.default_value,
                    'type': [c for c in dir(field) if c.startswith('TYPE_') and getattr(field, c) == field.type][0]

                }
            if len(command_outline[request_object_name]) == 0:
                setattr(self, request_object_name + '_button', QPushButton(request_object_name, self))
                button = getattr(self, request_object_name + '_button')
                button.command = command
                button.request_object_name = request_object_name
                button.clicked.connect(partial(getattr(self.node.client.client.lnd_client, button.command), getattr(ln, button.request_object_name)()))
                self.layout.addWidget(button)

        self.setLayout(self.layout)

        # self.client.list_all()

    def handle_click(self, click_event, request_object_name):
        log.debug('handle_click', click_event=click_event, request_object_name=request_object_name)

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
        client = LndThreadedClient(lnd_client=self.client)
        client.signals.result.connect(self.handle_peers_list)

