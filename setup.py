#!/usr/bin/env python
# -*- coding: utf-8 -*-



import os
import numpy

from Cython.Distutils import build_ext

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup
    from distutils.extension import Extension


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

np_lib = os.path.dirname(numpy.__file__)
np_inc = numpy.get_include()

extensions = [Extension('tde.substrings.ccss',
                        sources=['tde/substrings/ccss.pyx'],
                        extra_compile_args=['-shared', '-pthread', '-fPIC',
                                            '-fwrapv', '-O3', '-Wall',
                                            '-fno-strict-aliasing'],
                        include_dirs=['/usr/include/python2.7', np_inc]),
              Extension('tde.substrings.levenshtein',
                        sources=['tde/substrings/levenshtein.pyx'],
                        extra_compile_args=['-shared', '-pthread', '-fPIC',
                                            '-fwrapv', '-O3', '-Wall',
                                            '-fno-strict-aliasing'],
                        include_dirs=['/usr/include/python2.7', np_inc])]

setup(
    name='tde',
    version='0.1.2',
    description='DESCRIPTION',
    long_description=readme + '\n\n' + history,
    author='Maarten Versteegh',
    author_email='maartenversteegh@gmail.com',
    url='https://github.com/mwv/tde',
    packages=[
        'tde', 'tde.data', 'tde.util',  'tde.measures', 'tde.substrings'
    ],
    package_dir={'tde':
                 'tde'},
    include_package_data=True,
    install_requires=requirements,
    license="GPLv3",
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
    cmdclass={'build_ext': build_ext},
    ext_modules=extensions,
)
