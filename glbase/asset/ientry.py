import abc


class IEntry(object):
    __metaclass__=abc.ABCMeta
    def __init__(self, entry_string):
        self.entry_string=entry_string

    def __str__(self):
        return self.entry_string

