# coding: utf-8
import abc
import os
import re


class IAsset(object):
    @abc.abstractmethod
    def get(self, entry_string):
        pass

    @abc.abstractmethod
    def is_exist(self, entry_string):
        pass


class DirectoryAsset(IAsset):
    def __init__(self, path):
        assert isinstance(path, IPath)
        self.path=path

    def get(self, entry_string):
        fullpath=os.path.join(self.path.__str__(), entry_string)
        return open(fullpath, 'rb').read()

    def is_exist(self, entry_string):
        fullpath=os.path.join(self.path.__str__(), entry_string)
        return os.path.exists(fullpath)


class ZipAsset(IAsset):
    def __init__(self, path):
        assert isinstance(path, IPath)
        self.path=path


##############################################################################
def has_drive(path):
    return re.match('''^[a-zA-Z]:''', path)

class IPath(object):
    def __init__(self, path_string):
        assert isinstance(path_string, unicode)
        self.name=os.path.basename(path_string)

    @abc.abstractmethod
    def is_exist(self):
        pass

    @abc.abstractmethod
    def is_dir(self):
        pass


class Path(IPath):
    def __init__(self, path_string):
        super(Path, self).__init__(path_string)
        path_string=os.path.normpath(path_string)
        if not has_drive(path_string):
            path_string=os.path.abspath(path_string)
        self.path_string=path_string

    def __str__(self):
        return self.path_string
        
    def is_exist(self):
        return os.path.exists(self.path_string)

    def is_dir(self):
        return os.path.isdir(self.path_string)

