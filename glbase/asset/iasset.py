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

    @abc.abstractmethod
    def get_drive(self):
        pass

