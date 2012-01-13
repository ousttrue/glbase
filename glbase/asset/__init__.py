# coding: utf-8
import abc
import os
import re


LOADABLES=[
        u'.mqo',
        u'.pmd',
        u'.pmx',
        ]
def loadable(path):
    return path.get_extension() in LOADABLES


class IAsset(object):
    @abc.abstractmethod
    def get(self, entry_string):
        pass

    @abc.abstractmethod
    def is_exist(self, entry_string):
        pass

    @abc.abstractmethod
    def get_entries(self):
        pass


class DirectoryAsset(IAsset):
    def __init__(self, path):
        assert isinstance(path, Path)
        self.path=path

    def get(self, entry_string):
        fullpath=os.path.join(self.path.__str__(), entry_string)
        return open(fullpath, 'rb').read()

    def is_exist(self, entry_string):
        fullpath=os.path.join(self.path.__str__(), entry_string)
        return os.path.exists(fullpath)

    def get_entries(self, filter=lambda _: True):
        return [e for e in self.path.get_children() if filter(e)]


class ZipAsset(IAsset):
    def __init__(self, path):
        assert isinstance(path, IPath)
        self.path=path


##############################################################################
def has_drive(path):
    return re.match('''^[a-zA-Z]:''', path)


class Path(object):
    def __init__(self, path_string):
        path_string=os.path.normpath(path_string)
        if not has_drive(path_string):
            path_string=os.path.abspath(path_string)
        self.name=os.path.basename(path_string)
        self.path_string=path_string

    def __str__(self):
        return self.path_string

    def get_name(self):
        return self.name
        
    def is_exist(self):
        return os.path.exists(self.path_string)

    def is_dir(self):
        return os.path.isdir(self.path_string)

    def is_file(self):
        return os.path.isfile(self.path_string)

    def join(self, relative):
        return Path(os.path.join(self.path_string), relative)

    def get_children(self):
        return [Path(os.path.join(self.path_string, e)) 
                for e in os.listdir(self.path_string)]

    def get_extension(self):
        pos=self.path_string.rfind(u'.')
        if pos!=-1:
            return self.path_string[pos:].lower()

