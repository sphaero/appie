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

logger = logging.getLogger(__name__)

class AppieMarkdownParser(appie.AppieBaseParser):
    """
    Simple markdown file to html parser
    """
    def parse(self, match_key, d, *args, **kwargs):
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
