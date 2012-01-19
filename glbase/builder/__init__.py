import os
from . import mqobuilder
from . import pmdbuilder
from . import pmxbuilder
import glbase.asset


def load_model(asset, entry_string):
    assert isinstance(asset, glbase.asset.IAsset)
    _, extension=os.path.splitext(entry_string)
    if extension==u'.mqo':
        return mqobuilder.build(asset, entry_string)
    elif extension==u'.pmd':
        return pmdbuilder.build(asset, entry_string)
    elif extension==u'.pmx':
        return pmxbuilder.build(asset, entry_string)
    else:
        print 'unknown type', asset, entry_string, extension

