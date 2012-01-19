# coding: utf-8
from .path import *
from .iasset import IAsset
from .directoryasset import DirectoryAsset
from .zipasset import ZipAsset


def get_asset(path_string):
    path=Path(path_string)
    if not path.is_exist():
        return None

    if path.is_dir():
        return DirectoryAsset(path)
    elif path.is_zipfile():
        return ZipAsset(path, 'cp932')

def pwd():
    return DirectoryAsset.pwd()

