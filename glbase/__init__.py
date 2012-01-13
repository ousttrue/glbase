# coding: utf-8
import glbase.asset
from .controller import Controller
from . import builder


def get_asset(path_string):
    path=glbase.asset.Path(path_string)
    if not path.is_exist():
        return None

    if path.is_dir():
        return glbase.asset.DirectoryAsset(path)
    elif path.is_zipfile():
        return glbase.asset.ZipAsset(path)


def get_extension(path_string):
    pos=path_string.rfind(u'.')
    if pos!=-1:
        return path_string[pos:].lower()


def load_model(asset, entry_string):
    assert isinstance(asset, glbase.asset.IAsset)
    extension=get_extension(entry_string)
    if extension==u'.mqo':
        return glbase.builder.mqo_build(asset, entry_string)
    elif extension==u'.pmd':
        return glbase.builder.pmd_build(asset, entry_string)
    elif extension==u'.pmx':
        return glbase.builder.pmx_build(asset, entry_string)

