#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy
import sys
from distutils.extension import Extension
from distutils.sysconfig import *
from distutils.util import *
from Cython.Distutils import build_ext

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

py_inc = [get_python_inc()]
np_lib = os.path.dirname(numpy.__file__)
np_inc = [os.path.join(np_lib, 'core/include')]

setup(
    name='tde',
    version='0.1.0',
    description='DESCRIPTION',
    long_description=readme + '\n\n' + history,
    author='Maarten Versteegh',
    author_email='maartenversteegh@gmail.com',
    url='https://github.com/mwv/tde',
    packages=[
        'tde',
    ],
    package_dir={'tde':
                 'tde'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='tde',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GPLv3 License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    # cmdclass={'build_ext': build_ext},
    # ext_modules=[Extension('ccss', ['tde/ccss.pyx'],
    #                        include_dirs=py_inc + np_inc)],
    # include_dirs=[numpy.get_include(),
    #               os.path.join(numpy.get_include(), 'numpy')],
    test_suite='tests',
    tests_require=test_requirements
)
