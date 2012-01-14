# coding: utf-8
import abc
import os
import re
import zipfile


def get_extension(path_string):
    pos=path_string.rfind(u'.')
    if pos!=-1:
        return path_string[pos:].lower()


LOADABLES=[
        u'.mqo',
        u'.pmd',
        u'.pmx',
        ]
def loadable(asset, entry):
    return get_extension(entry) in LOADABLES


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


class DirectoryAsset(IAsset):
    def __init__(self, path):
        assert isinstance(path, Path)
        assert path.is_dir()
        self.path=path

    def get(self, entry_string):
        fullpath=os.path.join(self.path.__str__(), entry_string)
        return open(fullpath, 'rb').read()

    def is_exist(self, entry_string):
        fullpath=os.path.join(self.path.__str__(), entry_string)
        return os.path.exists(fullpath)

    def get_entries(self, filter=lambda _: True):
        return [e for e in self.path.get_children() if filter(self, e)]


class ZipAsset(IAsset):
    def __init__(self, path, encoding='ascii'):
        assert isinstance(path, Path)
        assert path.is_zipfile()
        self.path=path
        self.encoding=encoding

    def get(self, entry_string):
        with zipfile.ZipFile(self.path.__str__()) as z:
            return z.read(entry_string.encode(self.encoding))

    def is_exist(self, entry_string):
        with zipfile.ZipFile(self.path.__str__()) as z:
            try:
                return z.getinfo(entry_string.encode(self.encoding))
            except KeyError as e:
                return False

    def get_entries(self, filter):
        with zipfile.ZipFile(self.path.__str__()) as z:
            entries=[e.decode(self.encoding) for e in z.namelist()]
            return [e for e in entries if filter(self, e)]


def get_asset(path_string):
    path=Path(path_string)
    if not path.is_exist():
        return None

    if path.is_dir():
        return DirectoryAsset(path)
    elif path.is_zipfile():
        return ZipAsset(path, 'cp932')


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

    def is_zipfile(self):
        return zipfile.is_zipfile(self.path_string)

    def join(self, relative):
        return Path(os.path.join(self.path_string), relative)

    def get_children(self):
        return [self.path_string.decode('cp932')
                for e in os.listdir(self.path_string)]

    def get_extension(self):
        pos=self.path_string.rfind(u'.')
        if pos!=-1:
            return self.path_string[pos:].lower()

