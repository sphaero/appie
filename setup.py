import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

requires=['textile', 'markdown', 'Pillow', 'jinja2', 'pyinotify']
if sys.version_info.minor < 5 and sys.version_info.major > 2 :
    requires.append( 'scandir' )

setup(
        name='appie',
        version='0.6',
        description='Static generator for dynamic websites',
        author='Arnaud Loonstra',
        author_email='arnaud@sphaero.org',
        url='http://www.github.com/sphaero/appie/',
        packages=['appie'],
        scripts=['bin/appie'],
        include_package_data=True,
        requires=requires,
        install_requires=requires,
)

