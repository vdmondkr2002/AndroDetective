import fnmatch
import os
import tarfile
import time

from pathlib import Path
from scripts.funcs import *
from zipfile import ZipFile

class FileSeekerBase:
    # This is an abstract base class
    def search(self, filepattern_to_search, return_on_first_hit=False):
        '''Returns a list of paths for files/folders that matched'''
        pass

    def cleanup(self):
        '''close any open handles'''
        pass

class FileSeekerDir(FileSeekerBase):
    def __init__(self, directory):
        FileSeekerBase.__init__(self)
        self.directory = directory
        self._all_files = []
        logfunc('Building files listing...')
        self.build_files_list(directory)
        logfunc(f'File listing complete - {len(self._all_files)} files')

    def build_files_list(self, directory):
        '''Populates all paths in directory into _all_files'''
        try:
            files_list = os.scandir(directory)
            for item in files_list:
                self._all_files.append(item.path)
                if item.is_dir(follow_symlinks=False):
                    self.build_files_list(item.path)
        except Exception as ex:
            logfunc(f'Error reading {directory} ' + str(ex))

    def search(self, filepattern, return_on_first_hit=False):
        if return_on_first_hit:
            for item in self._all_files:
                if fnmatch.fnmatch(item, filepattern):
                    return [item]
            return []
        return fnmatch.filter(self._all_files, filepattern)
        