from unittest.mock import MagicMock

from node_launcher.node_launcher import NodeLauncher


class TestNodeLauncher(object):
    def test_launchTestnetBitcoinQtNode(self):
        command_generator = MagicMock()
        command_generator.testnet_bitcoin_qt = MagicMock(return_value=['echo', 'hello'])
        node_launcher = NodeLauncher(command_generator)
        result = node_launcher.launchTestnetBitcoinQtNode()
        assert result.pid
