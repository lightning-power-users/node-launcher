import os
import sys

from node_launcher.app_logging import log


class AssetAccess(object):

    @property
    def assets_directory(self):
        if getattr(sys, 'frozen', False):
            # noinspection PyUnresolvedReferences,PyProtectedMember
            assets_directory = os.path.join(sys._MEIPASS, 'node_launcher/gui/assets/')
        else:
            class_file_path = os.path.realpath(__file__)
            directory_path = os.path.join(class_file_path, os.path.pardir)
            assets_directory = os.path.abspath(directory_path)
        log.debug('Getting assets directory', assets_directory=assets_directory)
        return assets_directory

    def get_asset_full_path(self, asset_name: str) -> str:
        asset_path = os.path.join(self.assets_directory, asset_name)
        if not os.path.isfile(asset_path):
            log.error(f'{asset_path} not found')
            return None
        return asset_path


asset_access = AssetAccess()
