#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command


if sys.hexversion < 0x30500f0:
    print('Pygmy requires at least Python 3.5')
    sys.exit(1)


NAME = 'pygy'
DESCRIPTION = 'Pygmy - Open-Source Python Based Link Shortner'
URL = 'https://github.com/amitt001/pygmy'
EMAIL = 'mail2amit19@gmail.com'
AUTHOR = 'Amit Tripathi'

REQUIRED = [
    'bcrypt',
    'Django',
    'passlib',
    'Flask',
    'Flask-Cors',
    'Flask-JWT-Extended',
    'Flask-Script',
    'geoip2',
    'gunicorn',
    'PyJWT',
    'pytest',
    'requests',
    'SQLAlchemy'
]

here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

# about = {}
# with open(os.path.join(here, NAME, '__version__.py')) as f:
#     exec(f.read(), about)


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine…')
        os.system('twine upload dist/*')

        sys.exit()


setup(
    name=NAME,
    version='0.1.0',
    description=DESCRIPTION,
    long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages('src', exclude=['tests']),
    package_dir={'': 'src'},
    # If your package is a single module, use this instead of 'packages':
    # py_modules=['mypackage'],

    # entry_points={
    #     'console_scripts': ['mycli=mymodule:cli'],
    # },
    install_requires=REQUIRED,
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
    },
)