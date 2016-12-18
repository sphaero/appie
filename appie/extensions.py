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
from html.parser import HTMLParser
from jinja2 import Template
from PIL import Image

logger = logging.getLogger(__name__)


class AbstractHTMLParser(HTMLParser):
    """
    Simple helper class for retrieving the the first paragraph from
    a HTML document.

    The result is saved in the abstract member.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cap = False
        self.abstract = ""

    def handle_starttag(self, tag, attrs):
        if tag[0] == 'h' and len(tag) == 2:
            if self.cap:
                self.cap = False
            else:
                self.cap = True
        if self.cap:
            self.abstract += "<"+tag+">"

    def handle_endtag(self, tag):
        if self.cap:
            if tag == 'body':
                self.cap = False
            else:
                self.abstract += "</"+tag+">"

    def handle_data(self, data):
        if self.cap:
            self.abstract += data


class AppieMarkdownParser(appie.AppieFileParser):
    """
    Simple markdown file to html parser
    """
    def match(self, name):
        if name.endswith(".md"):
            return True

    def parse_file(self, path, filename, dest_path):
        """
        Read the file and return the content parsed through markdown
        """
        meta, html = self.parse_md(path)
        meta['content'] = html
        return meta

    def parse_md(self, file):
        """
        Read the file and return the content parsed through markdown
        """
        md = markdown.Markdown(
                    extensions=[
                        'markdown.extensions.tables',
                        'markdown.extensions.meta',
                        'markdown.extensions.codehilite',
                        'markdown.extensions.toc'
                        ]
                    )
        # generate the html from the .md file
        html = md.convert(self.load_file(file))
        meta = md.Meta
        return meta, html


class AppiePNGParser(appie.AppieFileParser):
    """
    PNG parser converting PNGs to JPG and a JPG thumb

    :note: to not parse PNG images and just copy them to the build root
           use a captital extension (.PNG). The parsers are case sensitive!
    """
    def __init__(self, *args, **kwargs):
        super(appie.AppiePNGParser, self).__init__(*args, **kwargs)
        self.jpg_size = appie.config.get('jpg_size', (1280, 720))
        self.thumb_size = appie.config.get('thumb_size', (384, 216))

    def match(self, name):
        if name.endswith('.png'):
            return True
        return False

    def parse_file(self, path, filename, dest_path):
        logging.debug("PNGParser parsing {0}".format(filename))
        filepath = path
        jpg_filename = os.path.splitext(filename)[0] + "_web.jpg"
        thumb_filename = os.path.splitext(filename)[0] + "_thumb.jpg"

        img = Image.open(filepath)
        size = img.size
        if img.mode in ('RGB', 'RGBA', 'CMYK', 'I'):
            img.thumbnail(self.jpg_size, Image.ANTIALIAS)
            img.save(os.path.join(dest_path, jpg_filename),
                     "JPEG", quality=80, optimize=True,
                     progressive=True)
            img.thumbnail(self.thumb_size, Image.ANTIALIAS)
            img.save(os.path.join(dest_path, thumb_filename), "JPEG",
                     quality=80, optimize=True, progressive=True)
        else:
            logger.warning("Image {0} is not a valid color image (mode={1})"
                           .format(filename, img.mode))
            return {'error': 'Not a valid color image'}

        return {
                'mimetype': 'image/png',    # https://www.w3.org/Graphics/PNG/
                'size': size,              # tuple (width,height)
                'web': jpg_filename,
                'thumb': thumb_filename,
                'path': dest_path,
                'md5': 'todo'
                }


class AppieJPGParser(appie.AppieFileParser):
    """
    JPG parser converting JPGs to progressive JPG and a JPG thumb if they
    are larger than the 'jpg_size' setting.

    :note: to not parse JPG images and just copy them to the build root use
           a captital extension (.JPG). The parsers are case sensitive!
    """
    def __init__(self, *args, **kwargs):
        super(appie.AppieJPGParser, self).__init__(*args, **kwargs)
        self.jpg_size = appie.config.get('jpg_size', (1280, 720))
        self.thumb_size = appie.config.get('thumb_size', (384, 216))

    def match(self, name):
        if name.endswith('.jpg'):
            return True
        return False

    def parse_file(self, path, filename, dest_path):
        logging.debug("JPGParser parsing {0}".format(filename))
        filepath = path
        jpg_filename = os.path.splitext(filename)[0] + "_web.jpg"
        thumb_filename = os.path.splitext(filename)[0] + "_thumb.jpg"

        img = Image.open(filepath)
        size = img.size
        if img.mode in ('RGB', 'RGBA', 'CMYK', 'I'):
            img.thumbnail(self.jpg_size, Image.ANTIALIAS)
            img.save(os.path.join(dest_path, jpg_filename), "JPEG",
                     quality=80, optimize=True, progressive=True)
            img.thumbnail(self.thumb_size, Image.ANTIALIAS)
            img.save(os.path.join(dest_path, thumb_filename), "JPEG",
                     quality=80, optimize=True, progressive=True)
        else:
            logger.warning("Image {0} is not a valid color image (mode={1})"
                           .format(filename, img.mode))
            return {'error': 'Not a valid color image'}

        return {
                'mimetype': 'image/jpg',   # https://www.w3.org/Graphics/PNG/
                'size': size,              # tuple (width,height)
                'web': jpg_filename,
                'thumb': thumb_filename,
                'path': dest_path,
                'md5': 'todo'
                }


class AppieMarkdownToFileParser(appie.AppieFileParser):
    """
    Simple markdown file to html file parser matching on '.md.html'
    extensions.

    :note: this is similar to the normal AppieMarkdownParser but
           it saves the generated html to a file and saves meta data in
           json.
    """
    def __init__(self, match_extension=None, *args, **kwargs):
        """
        :param string match_extension: the extension to match on, by
        default '.md.html'
        """
        self.copyfile = False
        if not match_extension:
            self.match_ext = ".md.html"
        else:
            self.match_ext = match_extension

    def match(self, name):
        if name.endswith(self.match_ext):
            return True

    def parse_file(self, path, filename, dest_path):
        logging.debug("MardownToFileParser parsing {0}".format(filename))
        meta, file_content = self.parse_md(path)
        parser = AbstractHTMLParser()
        parser.feed(file_content)
        meta['abstract'] = parser.abstract
        # copy html content to new file
        with open(os.path.join(dest_path, filename), 'w+') as f:
            f.write(file_content)
        return meta

    def parse_md(self, file):
        """
        Read the file and return the content parsed through markdown
        """
        md = markdown.Markdown(
                    extensions=[
                        'markdown.extensions.tables',
                        'markdown.extensions.meta',
                        'markdown.extensions.codehilite',
                        'markdown.extensions.toc'
                        ]
                    )
        # generate the html from the .md file
        html = md.convert(self.load_file(file))
        meta = md.Meta
        return meta, html


class AppieBlogDirParser(appie.AppieDirParser):
    """
    Matches on a directory named 'blog'. Then runs every .md file
    with metadata into the blog.jinja2 file to create html files
    """
    def match(self, name):
        if name == 'blog':
            return True

    def parse_dir(self, path, dest_path, prev_dict=None):
        prev_dict = prev_dict or {}
        d = {}
        tpl = Template(self.load_file(os.path.join(path, 'blog.jinja2')))
        for item in os.scandir(path):
            # save the relative! path in the buildroot instead of the original
            web_path = dest_path.split(appie.config['target'])[1][1:]
            if item.is_dir():
                # subdirs are parsed as would be done normally
                d[item.name] = self.parse_subdir(item, dest_path, prev_dict)
            elif self.is_modified(item, prev_dict):
                if item.name == "blog.jinja2":
                    # skip the jinja2 template
                    continue
                # find a parser for this file
                parser = appie.Appie.match_file_parsers(item.name)
                d[item.name] = parser.parse_file(item.path, item.name,
                                                 dest_path)
                d[item.name]['path'] = web_path
                d[item.name]['mtime'] = item.stat().st_mtime
                if item.name.endswith(".md"):
                    # run markdown parser output through jinja2
                    html = tpl.render(d[item.name])
                    fname, ext = os.path.splitext(item.name)
                    self.save_file(html, os.path.join(dest_path, fname + ".html"))
                    # rename the key
                    d[fname + ".html"] = d[item.name]
                    d.pop(item.name)
                    continue
                # copy file to dest if no content key
                if not d[item.name].get('content') and parser.copyfile:
                    logging.debug("Copy file {0} to the directory {1}"
                                  .format(path, dest_path))
                    shutil.copy(item.path, dest_path)
            else:
                d[item.name] = prev_dict[item.name]

        return d

    def load_file(self, path, mode='r'):
        """
        parse the file and return the content for the dict

        :param str file: the path to the file
        """
        with open(path, mode, encoding="utf8") as f:
            data = f.read()
        f.close()
        return data

    def save_file(self, data, path, mode='w'):
        """
        parse the file and return the content for the dict

        :param str file: the path to the file
        """
        with open(path, mode, encoding="utf8") as f:
            f.write(data)
        f.close()
        return data
