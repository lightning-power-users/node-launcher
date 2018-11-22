import subprocess


class NodeLauncher(object):
    def __init__(self, command_generator):
        self.command_generator = command_generator

    @staticmethod
    def launch(command):
        result = subprocess.Popen(command, close_fds=True)
        return result

    def launchTestnetBitcoinQtNode(self):
        result = self.launch(self.command_generator.testnet_bitcoin_qt())
        return result

    def launchMainnetBitcoinQtNode(self):
        result = self.launch(self.command_generator.mainnet_bitcoin_qt())
        return result
