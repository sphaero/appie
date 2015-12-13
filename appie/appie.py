#!/usr/bin/python3 
# 
# Copyright (c) 2013, Arnaud Loonstra, All rights reserved.
# Copyright (c) 2013, Stichting z25.org, All rights reserved.
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License v3 for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library.

import os
from functools import reduce
import textile

import pprint

def dir_structure_to_dict(rootdir):
    """
    Creates a nested dictionary that represents the folder structure of rootdir
    """
    # based on http://code.activestate.com/recipes/577879-create-a-nested-dictionary-from-oswalk/
    dir = {}
    rootdir = rootdir.rstrip(os.sep)
    start = rootdir.rfind(os.sep) + 1
    for path, dirs, files in os.walk(rootdir):
        files = [f for f in files if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']
        folders = path[start:].split(os.sep)
        subdir = dict.fromkeys(files, "file://"+path)
        parent = reduce(dict.get, folders[:-1], dir)
        parent[folders[-1]] = subdir
    # return dir structure as a dict without the rootdir name
    return dir[rootdir[start:]]


class AppieExceptStopParsing(Exception):
    pass


class AppieBaseParser(object):

    """
    The default parser, does nothing
    """
    def parse(self, match_key, d, *args, **kwargs):
        """
        Parses the dictionary d if match_key matches something it wants.
        Raises StopParsing if it doesn't allow for for further parsing 
        of its tree.
        """
        pass


class AppieTextileParser(AppieBaseParser):
    """
    Simple textile file to html parser
    """
    def parse(self, match_key, d, *args, **kwargs):
        print(match_key)
        if match_key.endswith(".textile"):
            filepath = os.path.join(d[match_key].split('file://')[1], match_key)
            print("parsing ", filepath)
            d[match_key] = self._parse_file(filepath)
            raise(AppieExceptStopParsing)

    def _parse_file(self, file):
        """
        read the file and return the content parsed through textile
        """
        with open(file, 'r', encoding="utf8") as f:
                data = f.read()
        f.close()
        return textile.textile(data)
 

class Appie(object):
    
    def __init__(self, *args, **kwargs):
        self._buildroot = kwargs.get("target", "./build")
        self._buildsrc = kwargs.get("src", "./site_src")
        self._directory_parsers = []
        self._file_parsers = [AppieTextileParser()]

    def parse(self):
        dirtree = dir_structure_to_dict(self._buildsrc)
        self.parse_file(dirtree)
        #pprint.pprint(dirtree)

    def parse_file(self, d):
        for key, val in d.items():
            # test if we match a directory parser
            try: 
                self._match_dir_parsers(key, d)
            except AppieExceptStopParsing:
                print("parser called to stop parsing this tree")
                break
            if isinstance(val, dict):
                self.parse_file(val)
            elif val.startswith("file://"):
                # is a file so either copy the file or parse it
                # and replace the url in the dict
                try:
                    self._match_file_parsers(key, d)
                except AppieExceptStopParsing:
                    break
                #d[key] += "test"
            else:
                raise Exception("value not a dict")

    def _match_dir_parsers(self, key, d):
        for parser in self._directory_parsers:
            parser.parse(key, d)

    def _match_file_parsers(self, key, d):
        for parser in self._file_parsers:
            parser.parse(key, d)


if __name__ == '__main__':
    #pprint.pprint(dir_structure_to_dict('../tests/site_src'))
    a = Appie(src='../tests/site_src')
    a.parse()
