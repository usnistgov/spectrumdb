# This software was developed by employees of the National Institute
# of Standards and Technology (NIST), an agency of the Federal
# Government. Pursuant to title 17 United States Code Section 105, works
# of NIST employees are not subject to copyright protection in the United
# States and are considered to be in the public domain. Permission to freely
# use, copy, modify, and distribute this software and its documentation
# without fee is hereby granted, provided that this notice and disclaimer
# of warranty appears in all copies.
#
# THE SOFTWARE IS PROVIDED 'AS IS' WITHOUT ANY WARRANTY OF ANY KIND,
# EITHER EXPRESSED, IMPLIED, OR STATUTORY, INCLUDING, BUT NOT LIMITED
# TO, ANY WARRANTY THAT THE SOFTWARE WILL CONFORM TO SPECIFICATIONS, ANY
# IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE,
# AND FREEDOM FROM INFRINGEMENT, AND ANY WARRANTY THAT THE DOCUMENTATION
# WILL CONFORM TO THE SOFTWARE, OR ANY WARRANTY THAT THE SOFTWARE WILL BE
# ERROR FREE. IN NO EVENT SHALL NASA BE LIABLE FOR ANY DAMAGES, INCLUDING,
# BUT NOT LIMITED TO, DIRECT, INDIRECT, SPECIAL OR CONSEQUENTIAL DAMAGES,
# ARISING OUT OF, RESULTING FROM, OR IN ANY WAY CONNECTED WITH THIS
# SOFTWARE, WHETHER OR NOT BASED UPON WARRANTY, CONTRACT, TORT, OR
# OTHERWISE, WHETHER OR NOT INJURY WAS SUSTAINED BY PERSONS OR PROPERTY
# OR OTHERWISE, AND WHETHER OR NOT LOSS WAS SUSTAINED FROM, OR AROSE OUT
# OF THE RESULTS OF, OR USE OF, THE SOFTWARE OR SERVICES PROVIDED HEREUNDER.
#
# Distributions of NIST software should also include copyright and licensing
# statements of any third-party software that are legally bundled with
# the code in compliance with the conditions of those licenses.


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
  package_dir={'spectrumdb':'spectrumdb'},
  package_data={'spectrumdb':['dispSpectrogram.m','find_radar1.m','parse_pv_pairs.m']},
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
  install_requires = ['numpy','pymongo','matplotlib','npTDMS==0.8.123'],
  dependency_links = [
      "git://github.com/usnistgov/npTDMS.git#egg=npTDMS-0.8.123"
  ],
  entry_points = """
  [console_scripts]
  spectrumdb=spectrumdb.dbgui:main
  populatedb=spectrumdb.populatedb:main
  querydb=spectrumdb.querydb:main
  """
)
