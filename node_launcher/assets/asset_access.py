import os
import sys


class AssetAccess(object):
    # noinspection PyUnresolvedReferences,PyProtectedMember
    def __init__(self):
        if getattr(sys, 'frozen', False):
            self.assets_directory = os.path.join(sys._MEIPASS, 'assets')
        else:
            class_file_path = os.path.realpath(__file__)
            self.assets_directory = os.path.abspath(
                os.path.join(class_file_path,
                             os.path.pardir))

    def get_asset_full_path(self, asset_name: str) -> str:
        asset_path = os.path.join(self.assets_directory, asset_name)
        if not os.path.isfile(asset_path):
            raise Exception(f'{asset_path} not found')
        return asset_path


asset_access = AssetAccess()
