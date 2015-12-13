import sys
import unittest
import shutil
import os
import json
import appie

if sys.version.startswith('3'):
    unicode = str


class AppieTest(unittest.TestCase):

    def setUp(self, *args, **kwargs):
        self.sitesrc = "./site_src"
        appie.Appie("./site_src")

    def tearDown(self):
        shutil.rmtree("./build")

    def test_appie(self):
        # test site src dir structure
        dstruct = {'about.textile': 'file:///home/people/arnaud/Documents/sphaero/appie/tests/site_src', 'img': {'spacecat.png': 'file:///home/people/arnaud/Documents/sphaero/appie/tests/site_src/img'}, 'home.textile': 'file:///home/people/arnaud/Documents/sphaero/appie/tests/site_src', 'files': {'report2009.pdf': 'file:///home/people/arnaud/Documents/sphaero/appie/tests/site_src/files', 'report2008.pdf': 'file:///home/people/arnaud/Documents/sphaero/appie/tests/site_src/files', 'report2010.pdf': 'file:///home/people/arnaud/Documents/sphaero/appie/tests/site_src/files'}}
        self.assertDictEqual(appie.dir_structure_to_dict(self.sitesrc), dstruct)
        # run appie
        
        # test site build dit structure
        self.assertTrue(os.path.isdir("./build"))
        self.assertTrue(os.path.isdir("./build/files"))
        self.assertTrue(os.path.isdir("./build/img"))
        # test if file
        self.assertTrue(os.path.isfile("./build/file/report2008.pdf"))
        self.assertTrue(os.path.isfile("./build/file/report2009.pdf"))
        self.assertTrue(os.path.isfile("./build/file/report2010.pdf"))
        self.assertTrue(os.path.isfile("./build/img/spacecat.png"))
        self.assertTrue(os.path.isfile("./build/img/spacecat.jpg"))
        self.assertTrue(os.path.isfile("./build/img/spacecat_thumb.jpg"))
        self.assertTrue(os.path.isfile("./build/all.json"))
        # test contents
        with open("./build/all.json") as f:
            j = json.load(f)
        print(j)
