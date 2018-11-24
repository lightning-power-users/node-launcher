import os

import pytest

from node_launcher.assets.asset_access import AssetAccess


@pytest.fixture
def asset_access():
    asset_access = AssetAccess()
    return asset_access


class TestAssetAccess(object):
    def test_assets_directory(self, asset_access):
        test_file_path = os.path.realpath(__file__)
        tests_directory = os.path.abspath(os.path.join(test_file_path, os.pardir))
        project_directory = os.path.abspath(os.path.join(tests_directory, os.pardir))
        module_directory = os.path.join(project_directory, 'node_launcher')
        assets_directory = os.path.join(module_directory, 'assets')
        assert os.path.isdir(assets_directory)
        assert asset_access.assets_directory == assets_directory
