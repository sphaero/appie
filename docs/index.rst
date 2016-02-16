.. Appie documentation master file, created by
   sphinx-quickstart on Tue Feb 16 17:37:22 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Appie's documentation!
=================================
Appie is a simple static generator for dynamic websites. Dynamic websites?
Yes! Although Appie can generate HTML files its focus is on providing all
information of files residing in your website's directory. As a HTML file
can not see what's available on your webserver Appie will provide a JSON
file containing exactly this. From this the HTML file, using javascript,
can figure things out. By matching to certain filenames the JSON file can
be filled with specific data. For example a file with the .textile
extension is parsed into HTML. Same holds for files ending with a .md
extension.

Installation
------------

Use pip to install Appie:

    pip install https://github.com/sphaero/appie/archive/master.zip

Appie is developed for Python3!

Contents:

.. toctree::
   :maxdepth: 2

   appie.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

