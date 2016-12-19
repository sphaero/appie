import sys
import unittest
import shutil
import os
import json
import appie
import appie.extensions

if sys.version.startswith('3'):
    unicode = str


class BlogTest(unittest.TestCase):

    def setUp(self, *args, **kwargs):
        self.maxDiff = None
        appie.config['src'] = "./tests/site_src3"
        self.sitesrc = appie.config['src']
        self.a = appie.Appie()

    def tearDown(self):
        return
        try:
            shutil.rmtree("./build")
        except FileNotFoundError:
            pass

    def zero_mtime(self, d):
        for k,v in d.items():
            if isinstance(v, dict):
                r = self.zero_mtime(v)
            elif k == 'mtime':
                d[k] = 0

    def test_appie(self):
        jstruct = {'blog': 
            {'first_post.html': {'content': '<h1 id="first-post">First Post</h1>\n'
                                        '<p>Hello world!</p>',
                            'date': ['2016-11-04'],
                            'mtime': 0,
                            'path': 'blog',
                            'summary': ['A brief description of my document.'],
                            'tags': ['tag1', 'tag2'],
                            'title': ['First Post']},
          'mtime': 0,
          'path': ''}}

        # run appie
        self.a.add_directory_parser( appie.AppieBlogDirParser() )
        self.a.add_file_parser( appie.AppieMarkdownParser() )
        self.a.parse()
        # test site build dir structure
        self.assertTrue(os.path.isdir("./build"))
        #self.assertTrue(os.path.isdir("./build/img"))
        # test if file
        self.assertTrue(os.path.isfile("./build/blog/first_post.html"))
        self.assertFalse(os.path.isfile("./build/blog/first_post.md"))
        #self.assertTrue(os.path.isfile("./build/img/spacecat.jpg"))
        self.assertTrue(os.path.isfile("./build/all.json"))
        # test contents
        with open("./build/all.json") as f:
            j = json.load(f)
        # but first zero all mtime keys
        self.zero_mtime(j)
        #import pprint
        #pprint.pprint(j)
        self.assertDictEqual(jstruct, j)

import logging
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
