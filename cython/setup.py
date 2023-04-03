import glob
import platform
import sys
from distutils.sysconfig import customize_compiler

from Cython.Build import cythonize
from Cython.Distutils import build_ext
from setuptools import setup, Extension

if sys.platform == 'win32':
    VC_INCLUDE_REDIST = False  # Set to True to include C runtime dlls in distribution.
    from distutils import msvccompiler
    from platform import architecture

    VC_VERSION = msvccompiler.get_build_version()
    ARCH = "x64" if architecture()[0] == "64bit" else "x86"

try:
    import numpy

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

DEBUG = False
NAME = "simple-cython-example"
VERSION = "0.1"
DESCR = "A small template project that shows how to wrap C/C++ code into python using Cython"
URL = "https://bap-software.net/en/"
REQUIRES = ['numpy', 'cython', 'six']

AUTHOR = "Tristan A. Hearn"
EMAIL = "tristanhearn@gmail.com"

LICENSE = "Apache 2.0"

PACKAGES = ["quantlib"]

CYTHON_DIRECTIVES = {"embedsignature": True,
                     "language_level": '3str',
                     "auto_pickle": False}

SUPPORT_CODE_INCLUDE = './cpp_layer'

QL_LIBRARY = 'QuantLib'

# FIXME: would be good to be able to customize the path with environment
# variables in place of hardcoded paths ...
if sys.platform == 'darwin':
    INCLUDE_DIRS = [
        '/usr/local/include', '.', '../sources/boost_1_55_0',
        SUPPORT_CODE_INCLUDE
    ]
    LIBRARY_DIRS = ["/usr/local/lib"]

elif sys.platform == 'win32':
    # With MSVC2008, the library is called QuantLib.lib but with MSVC2010, the
    # naming is QuantLib-vc100-mt
    if VC_VERSION >= 10.0:
        QL_LIBRARY = 'QuantLib-vc%d0-%s-mt' % (VC_VERSION, ARCH)

    INCLUDE_DIRS = [
        r'c:\dev\QuantLib-1.4',  # QuantLib headers
        r'c:\dev\boost_1_56_0',  # Boost headers
        '.',
        SUPPORT_CODE_INCLUDE
    ]
    LIBRARY_DIRS = [
        r"C:\dev\QuantLib-1.4\build\vc%d0\%s\Release" % (
            VC_VERSION, ("x64" if ARCH == "x64" else "Win32")),  # for the dll lib
        r"C:\dev\QuantLib-1.4\lib",
        '.',
        r'.\dll',
    ]
elif sys.platform.startswith('linux'):  # 'linux' on Py3, 'linux2' on Py2
    INCLUDE_DIRS = ['/usr/local/include', '/usr/include', '.', SUPPORT_CODE_INCLUDE]
    LIBRARY_DIRS = ['/usr/local/lib', '/usr/lib']

if HAS_NUMPY:
    INCLUDE_DIRS.append(numpy.get_include())


def get_define_macros():
    # defines = [ ('HAVE_CONFIG_H', None)]
    defines = []
    if sys.platform == 'win32':
        # based on the SWIG wrappers
        defines += [
            (name, None) for name in [
                '__WIN32__', 'WIN32', 'NDEBUG', '_WINDOWS', 'NOMINMAX', 'WINNT',
                '_WINDLL', '_SCL_SECURE_NO_DEPRECATE', '_CRT_SECURE_NO_DEPRECATE',
                '_SCL_SECURE_NO_WARNINGS'
            ]
        ]
    return defines


def get_extra_compile_args():
    if sys.platform == 'win32':
        args = ['/GR', '/FD', '/Zm250', '/EHsc']
        if DEBUG:
            args.append('/Z7')
    else:
        args = []

    return args


def get_extra_link_args():
    if sys.platform == 'win32':
        args = ['/subsystem:windows', '/machine:%s' % ("X64" if ARCH == "x64" else "I386")]
        if DEBUG:
            args.append('/DEBUG')
    elif sys.platform == 'darwin':
        major, minor = [
            int(item) for item in platform.mac_ver()[0].split('.')[:2]]
        if major == 10 and minor >= 9:
            # On Mac OS 10.9 we link against the libstdc++ library.
            args = ['-stdlib=libstdc++', '-mmacosx-version-min=10.6']
        else:
            args = []
    else:
        args = ['-Wl,--strip-all']

    return args


def collect_extensions():
    """ Collect all the directories with Cython extensions and return the list
    of Extension.
    Th function combines static Extension declaration and calls to cythonize
    to build the list of extensions.
    """

    kwargs = {
        'language': 'c',
        'include_dirs': INCLUDE_DIRS,
        'library_dirs': LIBRARY_DIRS,
        'define_macros': get_define_macros(),
        'extra_compile_args': get_extra_compile_args(),
        'extra_link_args': get_extra_link_args(),
        'libraries': [QL_LIBRARY]
    }

    collected_extensions = cythonize(
        [Extension('*', glob.glob("*/lib/*.c") + ['**/*.pyx'], **kwargs)],
        compiler_directives=CYTHON_DIRECTIVES, nthreads=4)

    return collected_extensions


class pyql_build_ext(build_ext):
    """
    Custom build command for quantlib that on Windows copies the quantlib dll
    and optionally c runtime dlls to the quantlib package.
    """

    def build_extensions(self):
        customize_compiler(self.compiler)
        try:
            self.compiler.compiler_so.remove("-Wstrict-prototypes")
        except (AttributeError, ValueError):
            pass
        self.compiler.compiler_so = [f for f in self.compiler.compiler_so if 'lto' not in f]
        build_ext.build_extensions(self)


if __name__ == "__main__":
    setup(install_requires=REQUIRES,
          packages=PACKAGES,
          zip_safe=False,
          name=NAME,
          version=VERSION,
          description=DESCR,
          author=AUTHOR,
          author_email=EMAIL,
          url=URL,
          license=LICENSE,
          include_package_data=True,
          cmdclass={"build_ext": pyql_build_ext},
          ext_modules=collect_extensions(),
          setup_requires=['cython'],
          )
