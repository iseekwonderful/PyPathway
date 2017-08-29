from distutils.core import setup, Extension
import numpy.distutils.misc_util
from sys import platform
from subprocess import call

# todos if platform is osx export the CFLAGS

if platform == 'darwin':
    call("export CFLAGS='-I{}'".format(numpy.distutils.misc_util.get_numpy_include_dirs()[0]), shell=True)

print("export CFLAGS='-I{}'".format(numpy.distutils.misc_util.get_numpy_include_dirs()[0]))    

c_ext = Extension("_chi2", ["c_ext_src/_chi2.c", "c_ext_src/basic.c", "c_ext_src/data_structure.c",
 "c_ext_src/graphic.c", "c_ext_src/test_data.c"])

setup(
    ext_modules=[c_ext],
    include_dirs=numpy.distutils.misc_util.get_numpy_include_dirs(),
)
