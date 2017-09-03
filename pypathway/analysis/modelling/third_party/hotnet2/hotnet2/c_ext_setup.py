from distutils.core import setup, Extension
import numpy.distutils.misc_util
import os
from sys import platform

# todos if platform is osx export the CFLAGS

fast_scc = Extension("fast_scc", ["c_ext_src/fast_scc.c", "c_ext_src/basic.c", "c_ext_src/data_structure.c",
 "c_ext_src/graphic.c", "c_ext_src/test_data.c"])


if platform == "darwin":
    # fix the include issue of distutuls in macos
    os.environ['CFLAGS'] = "-I{}".format(numpy.get_include())

setup(
    ext_modules=[fast_scc],
    include_dirs=numpy.distutils.misc_util.get_numpy_include_dirs(),
)
