#!/usr/bin/env python

# setup.py
#
# Copyright (C) 2016 Josh Burbrink <dev.burbrink@gmail.com>

import sys
import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

#import pydslice 

setup(name='pydslice',
      version='1.0.2',
      description='Python library for computing dynamic slices using a debugger',
      long_description='Python library for computing dynamic slices using a debugger',
      author='Josh Burbrink',
      author_email='dev.burbrink@gmail.com',
      url='https://github.com/dev-burbrink/pydslice',
      packages = ['pydslice'],
      license='LGPL',
      platforms = 'any',
      classifiers=['Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Programming Language :: Python',
        ],
     )
