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
        self.a = appie.Appie(self.sitesrc)

    def tearDown(self):
        shutil.rmtree("./build")

    def test_appie(self):
        # test site src dir structure
        dstruct = {'files': {
                    'report2008.pdf': 'file://{0}/files'.format(self.sitesrc), 
                    'report2009.pdf': 'file://{0}/files'.format(self.sitesrc), 
                    'report2010.pdf': 'file://{0}/files'.format(self.sitesrc)
                }, 
                'img': {
                    'img': {'spacecat.png': 'file://{0}/img/img'.format(self.sitesrc)
                    }, 
                    'spacecat.png': 'file://{0}/img'.format(self.sitesrc)
                }, 
                'home.textile': 'file://{0}'.format(self.sitesrc), 
                'about.textile': 'file://{0}'.format(self.sitesrc),
                '_test': 'file://./site_src',
                'test.md': 'file://./site_src'
            }
        d = appie.dir_structure_to_dict(self.sitesrc)
        self.assertDictEqual(appie.dir_structure_to_dict(self.sitesrc), dstruct)
        # run appie
        self.a.parse()
        # test site build dir structure
        self.assertTrue(os.path.isdir("./build"))
        self.assertTrue(os.path.isdir("./build/files"))
        self.assertTrue(os.path.isdir("./build/img"))
        # test if file
        self.assertTrue(os.path.isfile("./build/files/report2008.pdf"))
        self.assertTrue(os.path.isfile("./build/files/report2009.pdf"))
        self.assertTrue(os.path.isfile("./build/files/report2010.pdf"))
        self.assertFalse(os.path.exists("./build/_test"))
        self.assertTrue(os.path.isfile("./build/img/spacecat.png"))
        self.assertTrue(os.path.isfile("./build/img/img/spacecat.png"))
        #self.assertTrue(os.path.isfile("./build/img/spacecat.jpg"))
        #self.assertTrue(os.path.isfile("./build/img/spacecat_thumb.jpg"))
        self.assertTrue(os.path.isfile("./build/all.json"))
        # test contents
        with open("./build/all.json") as f:
            j = json.load(f)
        jstruct = {'img': {'img': {'spacecat.png': '/img/img'}, 'spacecat.png': '/img'}, 'about.textile': '\t<h3>About</h3>\n\n\t<p>What about it</p>\n\n\t<p><img alt="" src="img/spacecat.jpg" /></p>', 'home.textile': '\t<h1>Test</h1>\n\n\t<p>This is just a test</p>', 'files': {'report2009.pdf': '/files', 'report2008.pdf': '/files', 'report2010.pdf': '/files'}, '_test': 'Testing\n', 'test.md': ''}
        self.assertDictEqual(jstruct, j)

    def test_markdown(self):
        self.a.add_file_parser(appie.AppieMarkdownParser())
        # run appie
        self.a.parse()
        with open("./build/all.json") as f:
            j = json.load(f)
        self.assertEqual(j['test.md'], "<h1>Markdown</h1>\n<p>Test</p>")

    def test_pngparser(self):
        import PIL
        self.a.add_file_parser(appie.AppiePNGParser())
        # run appie
        self.a.parse()
        with open("./build/all.json") as f:
            j = json.load(f)
        self.assertEqual(j['img']['spacecat.png'], {
                                        'md5': 'todo',
                                        'web': 'spacecat_web.jpg',
                                        'thumb': 'spacecat_thumb.jpg'
                                        })
        img = PIL.Image.open('./build/img/spacecat_web.jpg')
        # images should be less than or equal to specified size in parser 
        self.assertIsInstance(img, PIL.JpegImagePlugin.JpegImageFile)
        self.assertTrue(img.width <= 800)
        self.assertTrue(img.height <= 450)

        img = PIL.Image.open('./build/img/spacecat_thumb.jpg')
        # images should be less than or equal to specified size in parser 
        self.assertIsInstance(img, PIL.JpegImagePlugin.JpegImageFile)
        self.assertTrue(img.width <= 192)
        self.assertTrue(img.height <= 108)


import logging
if __name__ == '__main__':
    #logging.basicConfig(level=logging.DEBUG)
    unittest.main()
