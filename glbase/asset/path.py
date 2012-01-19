import os
import re


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

