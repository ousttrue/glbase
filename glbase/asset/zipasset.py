# coding: utf-8
import zipfile
from .iasset import IAsset


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


