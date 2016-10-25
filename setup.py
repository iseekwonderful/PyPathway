#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import sys

# with open('README.rst') as readme_file:
#     readme = readme_file.read()

# with open('HISTORY.rst') as history_file:
#     history = history_file.read()

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
]

test_requirements = [
]

setup(
    name='pypathway',
    version='0.1.7',
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
    license="Creative Commons BY 3.0",
    zip_safe=False,
    keywords='pypathway',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
