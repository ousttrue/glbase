import os
from .iasset import IAsset
from .path import Path


class DirectoryAsset(IAsset):
    def __init__(self, path):
        assert isinstance(path, Path)
        assert path.is_dir()
        self.path=path

    def get(self, entry_string):
        fullpath=os.path.join(self.path.__str__(), entry_string)
        return open(fullpath, 'rb').read()

    def is_exist(self, entry_string):
        fullpath=os.path.join(self.path.__str__(), entry_string)
        return os.path.exists(fullpath)

    def get_entries(self, filter=lambda assset, entry_string: True):
        return [e for e in self.path.get_children() if filter(self, e)]

    @staticmethod
    def pwd():
        path=os.path.abspath('.')
        return DirectoryAsset(Path(path.decode('utf-8')))

