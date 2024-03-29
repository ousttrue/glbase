import os
import re
import string
import zipfile
from ctypes import windll
from .ientry import IEntry


def get_drives():
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.uppercase:
        if bitmask & 1:
            drives.append(letter.decode('ascii'))
        bitmask >>= 1
    return drives


class Path(object):
    def __init__(self, path_string):
        path_string=os.path.normpath(path_string)
        m=re.match('''^([a-zA-Z]):''', path_string)
        if m:
            pass
        else:
            # no drive
            path_string=os.path.abspath(path_string)
        # set drive
        m=re.match('''^([a-zA-Z]):''', path_string)
        self.drive=m.group(1).upper()

        self.name=os.path.basename(path_string)
        self.path_string=path_string.replace(u'\\', u'/')

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
        return [self.get_append(e) for e in os.listdir(self.path_string)]

    def get_extension(self):
        pos=self.path_string.rfind(u'.')
        if pos!=-1:
            return self.path_string[pos:].lower()

    def get_dirname(self):
        return Path(os.path.dirname(self.path_string))

    def get_drive(self):
        return self.drive

    def get_append(self, e):
        m=re.match('''^([a-zA-Z]):$''', self.path_string)
        if m:
            return Path(u'%s/%s' % (self.path_string, e))
        else:
            return Path(os.path.join(self.path_string, e))

    def from_root(self):
        current=None
        for e in self.path_string.split(u'/'):
            if e==u'':
                continue
            if not current:
                # drive
                current=Path(u'%s/' % e)
            else:
                current=current.get_append(e)
            yield current

    def get_asset(self):
        from .directoryasset import DirectoryAsset
        from .zipasset import ZipAsset
        if self.is_dir():
            return DirectoryAsset(self)
        elif self.is_zipfile():
            return ZipAsset(self, 'cp932')
        else:
            return DirectoryAsset(self.get_dirname())

    @staticmethod
    def pwd():
        path=os.path.abspath('.')
        return Path(path.decode('utf-8'))

