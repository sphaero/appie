# Appie extensions
#
# Copyright (c) 2015, Arnaud Loonstra, All rights reserved.
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
import appie
import markdown
import logging
import os
import shutil
import filecmp

from PIL import Image

logger = logging.getLogger(__name__)


class AppieMarkdownParser(appie.AppieBaseParser):
    """
    Simple markdown file to html parser
    """
    def parse(self, match_key, d, wd, *args, **kwargs):
        if match_key.endswith(".md"):
            logging.debug("MardownParser parsing match_key {0}".format(match_key))
            filepath = os.path.join(d[match_key].split('file://')[1], match_key)
            d[match_key] = self._parse_file(filepath)
            raise(appie.AppieExceptStopParsing)

    def _parse_file(self, file):
        """
        read the file and return the content parsed through textile
        """
        return markdown.markdown(
                    super(AppieMarkdownParser, self)._parse_file(file))


class AppiePNGParser(appie.AppieBaseParser):
    """
    PNG parser converting PNGs to JPG and a JPG thumb
    
    Note: to not parse PNG images and just copy them to the build root use
    a captital extension (.PNG). The parsers are case sensitive! 
    """
    def __init__(self, *args, **kwargs):
        self.jpg_size = appie.config.get('jpg_size', (1280,720))
        self.thumb_size = appie.config.get('thumb_size', (384,216))

    def parse(self, match_key, d, wd, *args, **kwargs):
        if match_key.endswith(".png"):
            logging.debug("PNGParser parsing match_key {0}@{1}".format(match_key, wd))
            filepath = os.path.join(d[match_key].split('file://')[1], match_key)
            jpg_filename = os.path.splitext(match_key)[0] + "_web.jpg"
            thumb_filename = os.path.splitext(match_key)[0] + "_thumb.jpg"
            # first test if the image already exists in the build dir
            # and is the same so we can skip it
            if not os.path.exists(os.path.join(wd, match_key)) or not filecmp.cmp(filepath, os.path.join(wd, match_key)):                
                img = Image.open(filepath)
                if img.mode in ('RGB', 'RGBA', 'CMYK', 'I'):
                    img.thumbnail(self.jpg_size, Image.ANTIALIAS)
                    img.save(os.path.join(wd, jpg_filename))
                    img.thumbnail(self.thumb_size, Image.ANTIALIAS)
                    img.save(os.path.join(wd, thumb_filename))
                else:
                    logger.warning("Image {0} is not a valid color image (mode={1}"\
                                    .format(match_key, img.mode))
                    return

            # get wd relative path excluding first /
            wdpath = wd.split(os.path.abspath(appie.config['target']))[1][1:]
            # copy the original to the root working dir
            shutil.copy(filepath, wd)
            d[match_key] = {
                            'web': jpg_filename, 
                            'thumb': thumb_filename,
                            'path': wdpath,
                            'md5': 'todo'
                            }
            raise(appie.AppieExceptStopParsing)
