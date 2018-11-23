from node_launcher.command_generator import CommandGenerator


class TestCommandGenerator(object):
    def test_testnet_bitcoin_qt(self):
        assert len(CommandGenerator().testnet_bitcoin_qt())

    def test_mainnet_bitcoin_qt(self):
        assert len(CommandGenerator().mainnet_bitcoin_qt())

    def test_testnet_lnd(self):
        assert len(CommandGenerator().testnet_lnd())
