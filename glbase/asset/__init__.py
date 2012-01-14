# coding: utf-8
import abc
import os
import re
import sys
import zipfile


'''
monkey patch
'''
class ZipInfo(zipfile.ZipInfo):
    def __init__(self, filename="NoName", date_time=(1980,1,1,0,0,0)):
        self.orig_filename = filename   # Original file name in archive

        # Terminate the file name at the first null byte.  Null bytes in file
        # names are used as tricks by viruses in archives.
        null_byte = filename.find(chr(0))
        if null_byte >= 0:
            filename = filename[0:null_byte]
        # This is used to ensure paths in generated ZIP files always use
        # forward slashes as the directory separator, as required by the
        # ZIP format specification.
        # !!!! コメントアウト !!!!
        #if os.sep != "/" and os.sep in filename:
        #    filename = filename.replace(os.sep, "/")

        self.filename = filename        # Normalized file name
        self.date_time = date_time      # year, month, day, hour, min, sec
        # Standard values:
        self.compress_type = zipfile.ZIP_STORED # Type of compression for the file
        self.comment = ""               # Comment for each file
        self.extra = ""                 # ZIP extra data
        if sys.platform == 'win32':
            self.create_system = 0          # System which created ZIP archive
        else:
            # Assume everything else is unix-y
            self.create_system = 3          # System which created ZIP archive
        self.create_version = 20        # Version which created ZIP archive
        self.extract_version = 20       # Version needed to extract archive
        self.reserved = 0               # Must be zero
        self.flag_bits = 0              # ZIP flag bits
        self.volume = 0                 # Volume number of file header
        self.internal_attr = 0          # Internal attributes
        self.external_attr = 0          # External file attributes
        # Other attributes are set by class ZipFile:
        # header_offset         Byte offset to the file header
        # CRC                   CRC-32 of the uncompressed file
        # compress_size         Size of the compressed file
        # file_size             Size of the uncompressed file

    def _decodeFilename(self):
        if self.flag_bits & 0x800:
            return self.filename.decode('cp932') # 日本語Windows用
        else:
            return self.filename
zipfile.ZipInfo=ZipInfo


##############################################################################
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
                print e
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
        return os.listdir(self.path_string)

    def get_extension(self):
        pos=self.path_string.rfind(u'.')
        if pos!=-1:
            return self.path_string[pos:].lower()

