

class TestCommandGenerator(object):
    def test_bitcoin_qt(self, command_generator):
        command = command_generator.bitcoin_qt(command_generator.mainnet)
        assert command[1].startswith('-datadir=')

    def test_testnet_bitcoin_qt(self, command_generator):
        command = command_generator.testnet_bitcoin_qt()
        assert command[-1] == '-testnet=1'

    def test_mainnet_bitcoin_qt(self, command_generator):
        command = command_generator.mainnet_bitcoin_qt()
        assert command[-1] == '-testnet=0'

    def test_testnet_lnd(self, command_generator):
        assert len(command_generator.testnet_lnd())

    def test_mainnet_lnd(self, command_generator):
        assert len(command_generator.mainnet_lnd())

    def test_testnet_lncli(self, command_generator):
        testnet_lncli = command_generator.testnet_lncli()
        assert testnet_lncli

    def test_mainnet_lncli(self, command_generator):
        mainnet_lncli = command_generator.mainnet_lncli()
        assert mainnet_lncli
