# coding: utf-8
from .asset import *
from .controller import Controller
from . import builder


def load_model(asset, entry_string):
    assert isinstance(asset, IAsset)
    extension=get_extension(entry_string)
    if extension==u'.mqo':
        return builder.mqo_build(asset, entry_string)
    elif extension==u'.pmd':
        return builder.pmd_build(asset, entry_string)
    elif extension==u'.pmx':
        return builder.pmx_build(asset, entry_string)

