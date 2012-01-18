from . import mqobuilder
from . import pmdbuilder
from . import pmxbuilder
import glbase.asset


"""
def load_model(argv):
    if not os.path.isdir(argv[0]) and not zipfile.is_zipfile(argv[0]):
        assert(len(argv)==1)
        argv=[
                os.path.dirname(argv[0]), 
                os.path.basename(argv[0]), 
                ]
    print 'load_model', argv
    asset=glbase.get_asset(argv[0].decode('cp932'))
    if not asset:
        print 'fail to get asset'
        return

    if len(argv)<2:
        # specify asset entry
        entries=asset.get_entries(lambda asset, entry: glbase.asset.loadable(asset, entry))
        if len(entries)==0:
            print 'no loadable entry'
            return
        elif len(entries)==1:
            index=0
        else:
            index=selector(entries)
        entry_string=entries[index]
    else:
        entry_string=argv[1].decode('cp932')

    print entry_string
    return glbase.load_model(asset, entry_string)
"""


def load_model(asset, entry_string):
    assert isinstance(asset, glbase.asset.IAsset)
    extension=glbase.asset.get_extension(entry_string)
    if extension==u'.mqo':
        return mqobuilder.build(asset, entry_string)
    elif extension==u'.pmd':
        return pmdbuilder.build(asset, entry_string)
    elif extension==u'.pmx':
        return pmxbuilder.build(asset, entry_string)
    else:
        print 'unknown type', asset, entry_string, extension

