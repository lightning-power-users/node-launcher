import sys

from PySide2 import QtWidgets

from node_launcher.command_generator import CommandGenerator
from node_launcher.configuration import Configuration
from node_launcher.configuration.bitcoin_configuration import \
    BitcoinConfiguration
from node_launcher.gui.launch_widget import LaunchWidget
from node_launcher.node_launcher import NodeLauncher

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    bitcoin_mainnet_conf = BitcoinConfiguration()
    bitcoin_testnet_conf = BitcoinConfiguration()
    command_generator = CommandGenerator(
        testnet_conf=Configuration('testnet', bitcoin_testnet_conf),
        mainnet_conf=Configuration('mainnet', bitcoin_mainnet_conf)
    )
    node_launcher = NodeLauncher(command_generator)
    widget = LaunchWidget(node_launcher)
    widget.show()

    sys.exit(app.exec_())
