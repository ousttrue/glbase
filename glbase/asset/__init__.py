# coding: utf-8
import abc


class IAsset(object):
    __metaclass__=abc.ABCMeta
    @abc.abstractmethod
    def get(self, entry_string):
        pass

    @abc.abstractmethod
    def is_exist(self, entry_string):
        pass

    @abc.abstractmethod
    def get_entries(self, filter):
        pass


def get_asset(path_string):
    from .path import Path
    path=Path(path_string)
    if not path.is_exist():
        return None

    from .directoryasset import DirectoryAsset
    from .zipasset import ZipAsset
    if path.is_dir():
        return DirectoryAsset(path)
    elif path.is_zipfile():
        return ZipAsset(path, 'cp932')

