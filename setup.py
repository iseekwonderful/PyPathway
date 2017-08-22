#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from setuptools import setup
import sys
from distutils.core import setup, Extension


try:
   import pypandoc
   readme = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
   readme = ''


requirements = [
    'requests>=1.0',
    'ipython',
    'jupyter',
    'echarts-python',
    'numpy',
    'wget',
]

test_requirements = [
]

c_ext = Extension("pypathway.utils._node", ["./pypathway/src/node_src/_chi2.c", "./pypathway/src/node_src/heap.c",
                                            "./pypathway/src/node_src/randpick.c", "./pypathway/src/node_src/main.c"])

selects = Extension('pypathway.utils._select', ["./pypathway/src/select/_chi2.c",
                                                 "./pypathway/src/select/color_coding.cpp",
                                                 "./pypathway/src/select/PPI_graph.cpp"])

cluster = Extension('pypathway.utils._cluster', ["./pypathway/src/cluster/_chi2.c",
                                                 "./pypathway/src/cluster/clustering.cpp",
                                                 "./pypathway/src/cluster/PPI_graph.cpp"])


setup(
    name='pypathway',
    version='0.3。1',
    description="A Python package for playing with pathways",
    long_description=readme,
    author="sheep",
    author_email='sss3barry@gmail.com',
    url='https://github.com/iseekwonderful/pypathway',
    packages=[
        'pypathway',
    ],
    package_dir={'pypathway':
                 'pypathway'},
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3 (GPLv3)",
    zip_safe=False,
    keywords='pypathway',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    ext_modules=[c_ext, selects, cluster],
)
