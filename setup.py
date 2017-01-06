try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
        name='appie',
        version='0.5',
        description='Static generator for dynamic websites',
        author='Arnaud Loonstra',
        author_email='arnaud@sphaero.org',
        url='http://www.github.com/sphaero/appie/',
        packages=['appie'],
        scripts=['bin/appie'],
        include_package_data=True,
        requires=['textile', 'markdown', 'Pillow', 'jinja2'],
        install_requires=['textile', 'markdown', 'Pillow', 'jinja2'],
)

