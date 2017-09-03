#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from setuptools import setup
import sys
from distutils.core import setup, Extension
import sys
import os
import numpy
from numpy.distutils.core import setup as npy_setup

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
    'h5py',
]

test_requirements = [
]


def configuration(parent_package='',top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration('',parent_package,top_path)

    config.add_extension('pypathway.analysis.modelling.third_party.hotnet2.hotnet2.c_routines',
                         sources=['pypathway/analysis/modelling/third_party/hotnet2/hotnet2/src/c/c_routines.pyf',
                                    'pypathway/analysis/modelling/third_party/hotnet2/hotnet2/src/c/c_routines.c'])
    return config

npy_setup(**configuration(top_path='').todict())

# c extension for fast node swap.
c_ext = Extension("pypathway.utils._node", ["./pypathway/src/node_src/_chi2.c", "./pypathway/src/node_src/heap.c",
                                            "./pypathway/src/node_src/randpick.c", "./pypathway/src/node_src/main.c"],
                  extra_compile_args=["-std=c99"] if not sys.platform == 'darwin' else None)

# c extension for magi pathway select
selects = Extension('pypathway.utils._select', ["./pypathway/src/select/_chi2.c",
                                                 "./pypathway/src/select/color_coding.cpp",
                                                 "./pypathway/src/select/PPI_Graph.cpp"],
                    extra_compile_args=["-std=c99"] if not sys.platform == 'darwin' else None)

# c extension for magi cluster
cluster = Extension('pypathway.utils._cluster', ["./pypathway/src/cluster/_chi2.c",
                                                 "./pypathway/src/cluster/clustering.cpp",
                                                 "./pypathway/src/cluster/PPI_Graph.cpp"],
                    extra_compile_args=["-std=c99"] if not sys.platform == 'darwin' else None)

# c extension for fast strong connected component
fast_scc = Extension("pypathway.analysis.modelling.third_party.hotnet2.hotnet2.fast_scc", [
    "pypathway/analysis/modelling/third_party/hotnet2/hotnet2/c_ext_src/fast_scc.c",
    "pypathway/analysis/modelling/third_party/hotnet2/hotnet2/c_ext_src/basic.c",
    "pypathway/analysis/modelling/third_party/hotnet2/hotnet2/c_ext_src/data_structure.c",
    "pypathway/analysis/modelling/third_party/hotnet2/hotnet2/c_ext_src/graphic.c",
    "pypathway/analysis/modelling/third_party/hotnet2/hotnet2/c_ext_src/test_data.c"])


if sys.platform == "darwin":
    # fix the include issue of distutuls in macos
    os.environ['CFLAGS'] = "-I{}".format(numpy.get_include())

setup(
    ext_modules=[fast_scc],
    include_dirs=numpy.get_include(),
)


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
    ext_modules=[c_ext, selects, cluster, fast_scc],
)


