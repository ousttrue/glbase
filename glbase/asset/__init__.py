# coding: utf-8
from .path import *
from .iasset import IAsset
from .directoryasset import DirectoryAsset
from .zipasset import ZipAsset, ZipEntry


def get_asset(src):
    if isinstance(src, IAsset):
        return src

    if isinstance(src, Path):
        path=src
    elif isinstance(src, ZipEntry):
        return src.get_asset()
    else:
        path=Path(src)

    if not path.is_exist():
        return None

    return path.get_asset()

def pwd():
    return DirectoryAsset.pwd()

