import subprocess


def launch(command):
    result = subprocess.Popen(command, close_fds=True)
    return result


class NodeLauncher(object):
    def __init__(self, command_generator, launch_function=launch):
        self.command_generator = command_generator
        self.launch = launch_function

    def launchTestnetBitcoinQtNode(self):
        result = self.launch(self.command_generator.testnet_bitcoin_qt())
        return result

    def launchMainnetBitcoinQtNode(self):
        result = self.launch(self.command_generator.mainnet_bitcoin_qt())
        return result

    def launchTestnetLndNode(self):
        result = self.launch(self.command_generator.testnet_lnd())
        return result
