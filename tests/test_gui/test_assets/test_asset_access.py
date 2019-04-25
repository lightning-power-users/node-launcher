import os

import pytest

from node_launcher.gui.assets.asset_access import AssetAccess


@pytest.fixture
def asset_access() -> AssetAccess:
    asset_access = AssetAccess()
    return asset_access


class TestAssetAccess(object):
    def test_assets_directory(self, asset_access: AssetAccess):
        test_file_path = os.path.realpath(__file__)
        tests_directory = os.path.abspath(os.path.join(test_file_path, os.pardir, os.pardir, os.pardir))
        project_directory = os.path.abspath(os.path.join(tests_directory, os.pardir))
        module_directory = os.path.join(project_directory, 'node_launcher')
        gui_directory = os.path.join(module_directory, 'gui')
        assets_directory = os.path.join(gui_directory, 'assets')
        assert os.path.isdir(assets_directory)
        assert asset_access.assets_directory == assets_directory

    def test_bitcoin_mainnet_png(self, asset_access: AssetAccess):
        path = asset_access.get_asset_full_path('bitcoin-mainnet.png')
        assert os.path.isfile(path)

    def test_bitcoin_testnet_png(self, asset_access: AssetAccess):
        path = asset_access.get_asset_full_path('bitcoin-testnet.png')
        assert os.path.isfile(path)
