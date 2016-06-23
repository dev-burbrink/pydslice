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

print(sys.version_info)
if sys.version_info < (3,0):
    raise NotImplementedError("Sorry, you need at least Python 3.x to use pydslice.")

#import pydslice 

setup(name='pydslice',
      version='1.0',
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
        'License :: OSI Approved :: LGPL License',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Programming Language :: Python :: 3.x',
        ],
     )
