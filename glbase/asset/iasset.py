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

    def get_drive(self):
        return self.path.get_drive()

    def from_root(self):
        from .zipasset import ZipAsset
        from .directoryasset import DirectoryAsset
        for p in self.path.from_root():
            if p.is_zipfile():
                yield ZipAsset(p)
            else:
                yield DirectoryAsset(p)

