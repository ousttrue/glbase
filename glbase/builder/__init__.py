from . import mqobuilder
from . import pmdbuilder
from . import pmxbuilder
import glbase.asset


def load_model(asset, entry_string):
    assert isinstance(asset, glbase.asset.IAsset)
    extension=glbase.asset.get_extension(entry_string)
    if extension==u'.mqo':
        return mqobuilder.build(asset, entry_string)
    elif extension==u'.pmd':
        return pmdbuilder.build(asset, entry_string)
    elif extension==u'.pmx':
        return pmxbuilder.build(asset, entry_string)

