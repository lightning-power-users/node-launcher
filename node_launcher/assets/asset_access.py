import os
import sys


class AssetAccess(object):

    @property
    def assets_directory(self):
        if getattr(sys, 'frozen', False):
            # noinspection PyUnresolvedReferences,PyProtectedMember
            return os.path.join(sys._MEIPASS, 'assets')
        else:
            class_file_path = os.path.realpath(__file__)
            directory_path = os.path.join(class_file_path, os.path.pardir)
            abs_directory_path = os.path.abspath(directory_path)
            return abs_directory_path

    def get_asset_full_path(self, asset_name: str) -> str:
        asset_path = os.path.join(self.assets_directory, asset_name)
        if not os.path.isfile(asset_path):
            raise Exception(f'{asset_path} not found')
        return asset_path


asset_access = AssetAccess()
