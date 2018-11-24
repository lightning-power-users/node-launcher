import os


class AssetAccess(object):
    def __init__(self):
        class_file_path = os.path.realpath(__file__)
        self.assets_directory = os.path.abspath(os.path.join(class_file_path,
                                                             os.path.pardir))

    def get_asset_full_path(self, asset_name: str) -> str:
        asset_path = os.path.join(self.assets_directory, asset_name)
        return asset_path
