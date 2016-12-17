import sys
import unittest
import shutil
import os
import json
import appie
import appie.extensions

if sys.version.startswith('3'):
    unicode = str


class AppieTest(unittest.TestCase):

    def setUp(self, *args, **kwargs):
        self.maxDiff = None
        appie.config['src'] = "./tests/site_src"
        self.sitesrc = appie.config['src']
        self.a = appie.Appie()

    def tearDown(self):
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
        jstruct = { '_test': {
                        'content': 'Testing\n', 
                        'mtime': 0, 
                        'path': ''
                    },
                    'about.textile': {
                        'content': '\t<h3>About</h3>\n'
                              '\n'
                              '\t<p>What about it</p>\n'
                              '\n'
                              '\t<p><img alt="" src="img/spacecat.jpg" /></p>',
                        'mtime': 0,
                        'path': ''
                    },
                    'blog.md.html': {
                        'mtime': 0, 
                        'path': ''
                    },
                    'files': {
                        'mtime': 0,
                        'path': '',
                        'report2008.pdf': {
                            'mtime': 0, 
                            'path': 'files'
                        },
                        'report2009.pdf': {
                            'mtime': 0, 
                            'path': 'files'
                        },
                        'report2010.pdf': {
                            'mtime': 0, 
                            'path': 'files'
                        }
                    },
                    'home.textile': {
                        'content': '\t<h1>Test</h1>\n\n\t<p>This is just a test</p>',
                        'mtime': 0,
                        'path': ''
                    },
                    'img': {
                        'img': {
                            'mtime': 0,
                            'path': 'img',
                            'spacecat.png': {
                                'mtime': 0,
                                'path': 'img/img'
                            }
                        },  
                        'mtime': 0,
                        'path': '',
                        'spacecat.jpg': {
                            'mtime': 0, 
                            'path': 'img'
                        },
                        'spacecat.png': {
                            'mtime': 0, 
                            'path': 'img'
                        }
                    },
                    'test.md': {
                        'mtime': 0, 
                        'path': ''
                    }
                }

        # run appie
        self.a.add_file_parser( appie.AppieTextileParser() )
        self.a.parse()
        # test site build dir structure
        self.assertTrue(os.path.isdir("./build"))
        self.assertTrue(os.path.isdir("./build/files"))
        self.assertTrue(os.path.isdir("./build/img"))
        # test if file
        self.assertTrue(os.path.isfile("./build/files/report2008.pdf"))
        self.assertTrue(os.path.isfile("./build/files/report2009.pdf"))
        self.assertTrue(os.path.isfile("./build/files/report2010.pdf"))
        self.assertTrue(os.path.isfile("./build/blog.md.html"))
        self.assertFalse(os.path.exists("./build/_test"))
        self.assertTrue(os.path.isfile("./build/img/spacecat.png"))
        self.assertTrue(os.path.isfile("./build/img/spacecat.jpg"))
        self.assertTrue(os.path.isfile("./build/img/img/spacecat.png"))
        #self.assertTrue(os.path.isfile("./build/img/spacecat.jpg"))
        #self.assertTrue(os.path.isfile("./build/img/spacecat_thumb.jpg"))
        self.assertTrue(os.path.isfile("./build/all.json"))
        # test contents
        with open("./build/all.json") as f:
            j = json.load(f)
        # but first zero all mtime keys
        self.zero_mtime(j)
        self.assertDictEqual(jstruct, j)

    @unittest.skip('bla')
    def test_markdown(self):
        self.a.add_file_parser(appie.AppieMarkdownParser())
        # run appie
        self.a.parse()
        with open("./build/all.json") as f:
            j = json.load(f)
        self.assertEqual(j['test.md'], "<h1>Markdown</h1>\n<p>Test</p>")

    @unittest.skip('bla')
    def test_markdown_to_file(self):
        self.a.add_file_parser(appie.AppieMarkdownToFileParser())
        # run appie
        self.a.parse()
        with open("./build/all.json") as f:
            j = json.load(f)
        self.assertEqual(j['blog.md.html'], {
                'title' : ['My Document'],
                'summary' : ['A brief description of my document.'],
                'authors' : ['Waylan Limberg', 'John Doe'],
                'date' : ['October 2, 2007'],
                'blank-value' : [''],
                'abstract' : '<h1>A heading</h1>\n<p>This is the first paragraph of the document.</p>',
                'base_url' : ['http://example.com']
            })
        self.assertTrue(os.path.isfile("./build/blog.md.html"))
        with open("./build/blog.md.html") as f:
            html = f.read()
        self.assertEqual(html, "<h1 id=\"a-heading\">A heading</h1>\n<p>This is the first paragraph of the document.</p>")

    def test_pngparser(self):
        import PIL
        print( dir(appie) )
        self.a.add_file_parser(appie.AppiePNGParser())
        # run appie
        self.a.parse()
        with open("./build/all.json") as f:
            j = json.load(f)
        self.zero_mtime(j)
        self.assertEqual(j['img']['spacecat.png'], {
                                        'md5': 'todo',
                                        'path': 'img',
                                        'mimetype': 'image/png',
                                        'mtime': 0,
                                        'size': [598, 335],
                                        'web': 'spacecat_web.jpg',
                                        'thumb': 'spacecat_thumb.jpg'
                                        })
        img = PIL.Image.open('./build/img/spacecat_web.jpg')
        # images should be less than or equal to specified size in parser 
        self.assertIsInstance(img, PIL.JpegImagePlugin.JpegImageFile)
        self.assertTrue(img.width <= 1280)
        self.assertTrue(img.height <= 720)

        img = PIL.Image.open('./build/img/spacecat_thumb.jpg')
        # images should be less than or equal to specified size in parser 
        self.assertIsInstance(img, PIL.JpegImagePlugin.JpegImageFile)
        self.assertTrue(img.width <= 384)
        self.assertTrue(img.height <= 216)

    @unittest.skip('bla')
    def test_jpgparser(self):
        import PIL
        self.a.add_file_parser(appie.AppieJPGParser())
        # run appie
        self.a.parse()
        with open("./build/all.json") as f:
            j = json.load(f)
        self.assertEqual(j['img']['spacecat.jpg'], {
                                        'md5': 'todo',
                                        'path': 'img',
                                        'web': 'spacecat_web.jpg',
                                        'thumb': 'spacecat_thumb.jpg'
                                        })
        img = PIL.Image.open('./build/img/spacecat_web.jpg')
        # images should be less than or equal to specified size in parser 
        self.assertIsInstance(img, PIL.JpegImagePlugin.JpegImageFile)
        self.assertTrue(img.width <= 1280)
        self.assertTrue(img.height <= 720)

        img = PIL.Image.open('./build/img/spacecat_thumb.jpg')
        # images should be less than or equal to specified size in parser 
        self.assertIsInstance(img, PIL.JpegImagePlugin.JpegImageFile)
        self.assertTrue(img.width <= 384)
        self.assertTrue(img.height <= 216)


#class AppieMultiTest(unittest.TestCase):

    #def setUp(self, *args, **kwargs):
        #self.maxDiff = None
        #appie.config['src'] = ["./tests/site_src", "./tests/site_src2"]
        #self.sitesrc = appie.config['src']
        #self.a = appie.Appie()

    #def tearDown(self):
        #try:
            #shutil.rmtree("./build")
        #except FileNotFoundError:
            #pass

    #def test_multisrc(self):
        ## run appie
        #self.a.parse()
        ## test site build dir structure
        #self.assertTrue(os.path.isdir("./build"))
        #self.assertTrue(os.path.isdir("./build/files"))
        #self.assertTrue(os.path.isdir("./build/files2"))
        #self.assertTrue(os.path.isdir("./build/img"))
        ## test if file
        #self.assertTrue(os.path.isfile("./build/files/report2008.pdf"))
        #self.assertTrue(os.path.isfile("./build/files/report2009.pdf"))
        #self.assertTrue(os.path.isfile("./build/files/report2010.pdf"))
        #self.assertTrue(os.path.isfile("./build/files/report2011.pdf"))
        #self.assertTrue(os.path.isfile("./build/files2/report2012.pdf"))
        #self.assertTrue(os.path.isfile("./build/blog.md.html"))
        #self.assertFalse(os.path.exists("./build/_test"))
        #self.assertTrue(os.path.isfile("./build/img/spacecat.png"))
        #self.assertTrue(os.path.isfile("./build/img/spacecat.jpg"))
        #self.assertTrue(os.path.isfile("./build/img/img/spacecat.png"))
        ##self.assertTrue(os.path.isfile("./build/img/spacecat.jpg"))
        ##self.assertTrue(os.path.isfile("./build/img/spacecat_thumb.jpg"))
        #self.assertTrue(os.path.isfile("./build/all.json"))
        ## test contents
        #with open("./build/all.json") as f:
            #j = json.load(f)
        #jstruct = {'img': 
                    #{'img': {'spacecat.png': 'img/img'}, 
                    #'spacecat.png': 'img', 'spacecat.jpg': 'img'}, 
                    #'about.textile': '\t<h3>About</h3>\n\n\t<p>What about it</p>\n\n\t<p><img alt="" src="img/spacecat.jpg" /></p>', 
                    #'home.textile': '\t<h1>Test</h1>\n\n\t<p>This is just a test</p>', 
                    #'files': {'report2009.pdf': 'files', 'report2008.pdf': 'files', 'report2011.pdf': 'files', 'report2010.pdf': 'files'}, 
                    #'files2': {'report2012.pdf': 'files2'}, 
                    #'_test': 'Testing2\n', 
                    #'test.md': '', 'blog.md.html': '',
                    #'test2.md': '', 'blog.md.html': ''}
        #self.assertDictEqual(jstruct, j)


import logging
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
