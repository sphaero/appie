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
import shutil
from functools import reduce
import textile
import json
import logging

import pprint

logger = logging.getLogger(__name__)

config = {'target': "./build", 'src': "./site_src" } 

def mergedicts(dict1, dict2):
    for k in set(dict1.keys()).union(dict2.keys()):
        if k in dict1 and k in dict2:
            if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                yield (k, dict(mergedicts(dict1[k], dict2[k])))
            else:
                # If one of the values is not a dict, you can't continue merging it.
                # Value from second dict overrides one in first and we move on.
                yield (k, dict2[k])
                # Alternatively, replace this with exception raiser to alert you of value conflicts
        elif k in dict1:
            yield (k, dict1[k])
        else:
            yield (k, dict2[k])

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
    The default parser, does nothing but load files prepended with '_'
    (underscore)
    """
    def parse(self, match_key, d, wd, *args, **kwargs):
        """
        Parses the dictionary d if match_key matches something it wants.
        Raises StopParsing if it doesn't allow for for further parsing 
        of its tree.
        
        :param str match_key: filename to match on
        :param dict d: dictionary belonging to match_key
        :param list wd: current working directory as a list 
        """
        logging.debug("BaseParser parsing match_key {0}".format(match_key))
        if match_key[0] == "_" and d[match_key].startswith('file://'):
            filepath = os.path.join(d[match_key].split('file://')[1], match_key)
            d[match_key] = self._parse_file(filepath)
            raise(AppieExceptStopParsing)

    def _parse_file(self, file):
        """
        read the file and return the content parsed through textile
        
        :param str file: the path to the file
        """
        with open(file, 'r', encoding="utf8") as f:
            data = f.read()
        f.close()
        return data


class AppieTextileParser(AppieBaseParser):
    """
    Simple textile file to html parser
    """
    def parse(self, match_key, d, wd, *args, **kwargs):
        """
        Parses textile files (match_key) with .textile extension to html.
        Raises AppieExceptStopParsing when a file is matched and parsed.
        
        :param str match_key: filename to match on
        :param dict d: dictionary belonging to match_key
        :param list wd: current working directory as a list
        """
        if match_key.endswith(".textile"):
            logging.debug("TextileParser parsing match_key {0}".format(match_key))
            filepath = os.path.join(d[match_key].split('file://')[1], match_key)
            d[match_key] = self._parse_file(filepath)
            raise(AppieExceptStopParsing)

    def _parse_file(self, file):
        """
        read the file and return the content parsed through textile
        """
        return textile.textile(super(AppieTextileParser, self)._parse_file(file))


class Appie(object):
    
    def __init__(self, *args, **kwargs):
        # check if string and convert to list if so
        if isinstance(config["src"], str):
            config["src"] = [config["src"]]
        self._buildwd = os.path.abspath(config["target"])
        self._directory_parsers = []
        self._file_parsers = [AppieTextileParser(), AppieBaseParser()]

    def add_directory_parser(self, inst):
        """
        Adds a parser instance to match on directory names
   
        :param instance inst: parser instance
        """     
        self._directory_parsers.insert(0, inst)

    def add_file_parser(self, inst):
        """
        Adds a parser instance to match on filenames
   
        :param instance inst: parser instance
        """     
        self._file_parsers.insert(0, inst)

    def parse(self):
        """
        Parse the all source directories
        """
        # create the buildroot
        try:
            os.makedirs(self._buildwd)
        except FileExistsError:
            pass

        final = {}
        for src in config["src"]:
            dirtree = dir_structure_to_dict(src)
            self.parse_file(dirtree, self._buildwd)
            final = dict(mergedicts(final, dirtree))
        self.save_dict(final, os.path.join(config["target"], 'all.json'))

    def parse_file(self, d, wd=""):
        """
        Parse a dictionary leaf

        :param dict d: the dictionary to parse
        :param string wd: string containing the target directory
        """
        for key, val in d.items():
            # test if we match a directory parser
            try: 
                self._match_dir_parsers(key, d, wd)
            except AppieExceptStopParsing:
                logging.debug("parser called to stop parsing this tree \
                                {0}".format(key))
                continue
            if isinstance(val, dict):
                # if a dictionary recurse but first create its dir
                try:
                    os.makedirs(os.path.join(wd, key))
                except FileExistsError:
                    pass
                self.parse_file(val, os.path.join(wd, key))
            elif val.startswith("file://"):
                # if a file either copy the file or parse it
                # and replace the url in the dict
                try:
                    self._match_file_parsers(key, d, wd)
                except AppieExceptStopParsing:
                    continue

                filepath = os.path.join(val.split('file://')[1], key)
                logging.debug("Copy file {0} to the directory {1}"\
                                .format(filepath, wd))
                shutil.copy(filepath, wd)
                # save the relative! path in the buildroot instead of the original
                d[key] = wd.split(self._buildwd)[1][1:]

            #else:
            #    logging.debug("ERROR: key:{0}, val:{1}".format(key, val))
            #    raise Exception("value not a dict, nor a leaf")

    def _match_dir_parsers(self, key, d, wd):
        for parser in self._directory_parsers:
            parser.parse(key, d, wd)

    def _match_file_parsers(self, key, d, wd):
        for parser in self._file_parsers:
            parser.parse(key, d, wd)

    def save_dict(self, d, filepath):
        """
        Save dictionary to json file

        :param dict d: the dictionary to save
        :param string filepath: string containing the full target filepath
        """
        with open(filepath, 'w') as f:
            json.dump(d, f)


if __name__ == '__main__':
    #pprint.pprint(dir_structure_to_dict('../tests/site_src'))
    a = Appie(src='../tests/site_src')
    a.parse()
