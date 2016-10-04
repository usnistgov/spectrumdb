import os

from setuptools import setup


def read_version():
    here = os.path.abspath(os.path.dirname(__file__))
    version_path = os.path.sep.join((here, "spectrumdb", "version.py"))
    v_globals = {}
    v_locals = {}
    exec(open(version_path).read(), v_globals, v_locals)
    return v_locals['__version__']


setup(
  name = 'spectrumdb',
  version = read_version(),
  description = ("Spectrum datafile management"
    " for radar spectrum measurement experiments."),
  author = 'M. Ranganathan',
  author_email = 'mranga@nist.gov',
  url = 'https://github.com/usnistgov/spectrumdb',
  packages = ['spectrumdb', 'spectrumdb.test'],
  long_description=open('README.rst').read(),
  license = 'Public Domain',
  classifiers = [
    'Development Status :: Alpha ',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Topic :: Scientific/Engineering',
    'License :: Public Domain',
    'Intended Audience :: NIST CTL',
    'Natural Language :: English',
  ],
  install_requires = ['numpy', 'pymongo','matplotlib','npTDMS'],
  entry_points = """
  [console_scripts]
  dbgui=spectrumdb.dbgui:main
  """
)
