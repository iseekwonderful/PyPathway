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
    'gseapy>=0.8.4',
    'networkx',
    'pandas',
    'scipy',
    'statsmodels',
    'goatools',
    'jinja2',
    'sqlite3',
    'requests>=1.0',
    'ipython',
    'jupyter',
    'echarts-python',
    'numpy',
    'wget',
]

test_requirements = [
]

# c extension for fast node swap.
c_ext = Extension("pypathway.utils._node", ["./pypathway/src/node_src/_chi2.c", "./pypathway/src/node_src/heap.c",
                                            "./pypathway/src/node_src/randpick.c", "./pypathway/src/node_src/main.c"])

# c extension for magi pathway select
selects = Extension('pypathway.utils._select', ["./pypathway/src/select/_chi2.c",
                                                 "./pypathway/src/select/color_coding.cpp",
                                                 "./pypathway/src/select/PPI_graph.cpp"])

# c extension for magi cluster
cluster = Extension('pypathway.utils._cluster', ["./pypathway/src/cluster/_chi2.c",
                                                 "./pypathway/src/cluster/clustering.cpp",
                                                 "./pypathway/src/cluster/PPI_graph.cpp"])


setup(
    name='PyPathway',
    version='0.3.3',
    description="A Python package biological network analysis and visualization",
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
    keywords='pathway',
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
