import sys

from PySide2 import QtWidgets

from node_launcher.command_generator import CommandGenerator
from node_launcher.configuration import Configuration, LndConfiguration
from node_launcher.configuration.bitcoin_configuration import \
    BitcoinConfiguration
from node_launcher.gui.launch_widget import LaunchWidget
from node_launcher.node_launcher import NodeLauncher

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    bitcoin_mainnet_conf = BitcoinConfiguration('mainnet')
    bitcoin_testnet_conf = BitcoinConfiguration('testnet')
    lnd_mainnet_conf = LndConfiguration('mainnet')
    lnd_testnet_conf = LndConfiguration('testnet')
    mainnet_configuration = Configuration('mainnet',
                                          bitcoin_configuration=bitcoin_mainnet_conf,
                                          lnd_configuration=lnd_mainnet_conf)
    testnet_configuration = Configuration('testnet',
                                          bitcoin_configuration=bitcoin_testnet_conf,
                                          lnd_configuration=lnd_testnet_conf)
    command_generator = CommandGenerator(
        testnet_conf=testnet_configuration,
        mainnet_conf=mainnet_configuration
    )
    node_launcher = NodeLauncher(command_generator)
    widget = LaunchWidget(node_launcher)

    widget.show()

    sys.exit(app.exec_())
