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

config = {
    'target': "./build", 
    'src': "./site_src" 
} 

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


class AppieDirParser(object):
    """
    The default dir parser. Searches for parsers matching file or 
    directory parsers. If none found it recurses into subdirs and 
    loads files prepended with '_'(underscore). 
    Files are copied to the build root.
    
    A file is represented by a dictionary with at least the following keys
    * content: file content if applicable
    * path: filepath ( in the build dir )
    * mtime: modification time
    """    
    def match(self, name):
        """
        Test if this parser matches for a name
        
        :param str name: file or directory name
        """ 
        return False
        
    def is_modified(self, dirobj, prev_dict):
        """
        Check file's mtime and compares it to the previous run value
        
        Returns true if newer
        """
        if not prev_dict or not prev_dict.get(dirobj.name):
            return True   # no previous data found so modified
        return dirobj.stat().st_mtime > prev_dict.get(dirobj.name)[ 'mtime' ] 

    def parse_dir(self, path, dest_path, prev_dict=None):
        """
        Parse a directory. Will search parser to match file or directory names
        
        :param str path: path of the directory
        :param str dest_path: path of the destination directory
        :param dict prev_dict: the dictionary belonging to this directory loaded
                               from a previous run
        Returns the dictionary with contents of the directory
        """
        prev_dict = prev_dict or {}
        d = {}
        for item in os.scandir(path):
            # save the relative! path in the buildroot instead of the original
            web_path = dest_path.split(config['target'])[1][1:]
            if item.is_dir():
                d[item.name] = self.parse_subdir( item, dest_path, prev_dict, web_path)
            elif self.is_modified( item, prev_dict ):
                # find a parser for this file
                parser = Appie.match_file_parsers(item.name)
                d[item.name] = parser.parse_file( item.path, item.name, dest_path )
                d[item.name]['path'] = web_path
                d[item.name]['mtime'] = item.stat().st_mtime
                # copy file to dest if no content key
                if not d[item.name].get( 'content' ) and parser.copyfile:
                    logging.debug("Copy file {0} to the directory {1}"\
                                    .format(path, dest_path))
                    shutil.copy(item.path, dest_path)
            else:
                d[item.name] = prev_dict[item.name]
                
        return d

    def parse_subdir(self, diritem, dest_path, prev_dict, web_path):
        ret = {}
        new_dest_path = os.path.join(dest_path, diritem.name)
        # first create its dir
        try:
            os.makedirs(new_dest_path)
        except FileExistsError:
            pass
        # find a parser for this dir
        parser = Appie.match_dir_parsers(diritem.name)
        content = parser.parse_dir( diritem.path, new_dest_path, prev_dict.get( diritem.name ))
        # add meta information if the parser returned content
        if content:
            content['path'] = web_path
            content['mtime'] = diritem.stat().st_mtime
        else:
            # if not we can remove the dir       TODO: does this hold?
            # will error if new_dest_path not empty
            os.remove(new_dest_path)
        return content


class AppieFileParser(object):
    """
    Appie default file parser. Loads the content of a file if
    it starts with _ (underscore).
    """
    def __init__(self, *args, **kwargs):
        self.copyfile = True                # use the flag to tell the dirparser
                                            # to copy the file or not

    def match(self, name):
        """
        Matches on files with the extension .textile
        """
        if name[0] == '_':
            return True

    def parse_file(self, path, filename, dest_path):
        """
        Parse file. If it starts with '_' (underscore) it will be loaded
        and returned as the content key in a dictionary
        
        Override this method in a custom parser class and add any data you
        need.
        
        :param str path: Path to the file
        :param str filename: The name of the file
        """
        if self.match(filename):                         # we only test again because the FileParser is always returned if
            return { 'content': self.load_file(path) }   # no other parser matches but we only want to load if starting with _
        return {}
        
    def load_file(self, path, mode='r'):
        """
        parse the file and return the content for the dict
        
        :param str file: the path to the file
        """
        with open(path, mode, encoding="utf8") as f:
            data = f.read()
        f.close()
        
        return data


class AppieTextileParser(AppieFileParser):
    """
    Simple textile file to html parser
    """
    def match(self, name):
        """
        Matches on files with the extension .textile
        """
        logging.debug('Matching AppieTextileParser to {0}'.format(name))
        if name.endswith('.textile'):
            return True

    def parse_file(self, path, filename, dest_path):
        """
        Parses textile files to html.
        
        :param path: full path of the file
        :param filename: the name of the file
        
        Returns a dictionary with the content of the file in the content
        key!
        """
        logging.debug("TextileParser parsing {0}".format(filename))
        t = textile.textile(self.load_file(path))
        return { 'content': t }


class Appie(object):
    
    dir_parsers = []
    file_parsers = []

    def __init__(self, *args, **kwargs):
        # check if string and convert to list if so
        if isinstance(config["src"], str):
            config["src"] = [config["src"]]
        self._buildwd = os.path.abspath(config["target"])

    def add_directory_parser(self, inst):
        """
        Adds a parser instance to match on directory names
   
        :param instance inst: parser instance
        """     
        Appie.dir_parsers.insert(0, inst)

    def add_file_parser(self, inst):
        """
        Adds a parser instance to match on filenames
   
        :param instance inst: parser instance
        """     
        Appie.file_parsers.insert(0, inst)

    @staticmethod
    def match_dir_parsers(dirname):
        """
        Returns the parser for the directory
        
        :params str dirname: directory name to match on
        """
        for p in Appie.dir_parsers:
            if p.match(dirname):
                return p
        return AppieDirParser() # default is self

    @staticmethod
    def match_file_parsers(filename):
        """
        Returns the parser for the file
        
        :params str filename: filename to match on
        """
        for p in Appie.file_parsers:
            if p.match(filename):
                return p
        return AppieFileParser() # default is AppieFileParser

    def parse(self):
        """
        Parse the all source directories
        """
        # create the buildroot
        prev = None     # previous all.json container
        try:
            os.makedirs(self._buildwd)
        except FileExistsError:
            # try to load previous run
            try:
                prev = self.load_dict( os.path.join(self._buildwd, 'all.json' ) )
            except FileNotFoundError:
                prev = None

        final = {}
        for src in config["src"]:
            d = AppieDirParser().parse_dir( src, config["target"], prev )
            final = dict(mergedicts(final, d))
        #return final
        self.save_dict(final, os.path.join(config["target"], 'all.json'))

    def save_dict(self, d, filepath):
        """
        Save dictionary to json file

        :param dict d: the dictionary to save
        :param string filepath: string containing the full target filepath
        """
        with open(filepath, 'w') as f:
            json.dump(d, f)

    def load_dict(self, filepath):
        """
        load json file

        :param dict d: the dictionary to save
        :param string filepath: string containing the full target filepath
        """
        with open(filepath, 'r') as f:
            d = json.load(f)
        return d

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    config["src"] = '../tests/site_src'
    a = Appie()
    a.add_file_parser(AppieTextileParser())
    a.parse()
