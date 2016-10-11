SpectrumDb -- a manager for data gathered from spectrum experiments
===================================================================


This project publishes a data manager for RADAR spectrum data readings
collected in TDMS format from the NI Vector Signal Generator. Such RADAR
data is gathered in various coastal locations and metadata is extracted
from it. The gathered data + metadata is presented to the spectrumdb
tool which catalogs the data and presents a query interface. Spectrumdb
scans through a set of directories, builds additional metadata based on
the files it encounters and puts the result into a mongodb collection
which can later be queried and updated.



Prerequisites
--------------

- Mongodb 3.3 (see mongodb.org), Install the MongoDB service by starting
mongod.exe with the --install option. To use an alternate dbpath, specify
the path in the configuration file (e.g. C:\mongodb\mongod.cfg) or on
the command line with the --dbpath option. You can put the database in
any directory on the filesystem.

   mongd.exe -install -dbpath c:/mongodb -log c:/Temp/mongolog.txt

Python dependencies
++++++++++++++++++++
First install Python 2.7.12 set your path to python.exe. 

Get pip. First download the  following:

   https://bootstrap.pypa.io/get-pip.py

Then do the following

   python get-pip.py


You can install most of the following dependencies from a github git shell
using the following command:

    python setup.py install 

- pymongo 
- numpy (pip install numpy)
- pytz (pip install pytz
- npTDMS (Get this from the fork https://github.com/usnistgov/npTDMS )

Additionally, you will need to manually install the following:

- pyqt4 use the installer from here (does not install from setup.py):
    http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.11.4/PyQt4-4.11.4-gpl-Py2.7-Qt4.8.7-x64.exe  
- Matlab engine connector for python. Follow the instructions here:
  https://www.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html




Google Timzone API
+++++++++++++++++++

This is used for lat/lon to timezone conversion and for local time to universal
time conversion. This turns out to be a tricky problem because local time is
often set by legislation (for example whether or not Daylight Savings Time is in
use). You can get an API key by getting a google account and using the
developer console (google around a bit to figure out how). 

- Get a google timezone API key It is required to  determine the timezone for 
  the LAT/LON where you gathered data.



Starting
--------

Start mongod 
+++++++++++++

    # Create a mongod folder where you want the db to reside
    md c:\mongodb
    mongod -dbpath = c:\mongodb

Note: if you installed mongod as a service (see above), 
it should start when you restart windows. If it does not auto-start,
then start it from the command line.

Populating the DB
------------------

First, configure the system using the GUI. Provide the google timezone API key
for this.

There are two methods to populate the DB and browse the data.

- Via the GUI
- Via the command line interface

Graphical user interface
+++++++++++++++++++++++++

Start the db gui application. From a shell type

    spectrumdb

You have to define configure the system first by providing the google API key.
Then define a dataset and then populate it with data.
The UI interactions are fairly obvious. We will not bore you by
giving tiresome instructions.
You do not need to start the GUI if you do not want to browse the data.
You can use the command line interface to do all interactions as outlined
below:

  

Command line interface
+++++++++++++++++++++++

The tool provides command line as well as GUI based interfaces. 
The main command line interface is called populatedb.
You can look at the options using python populatedb  -help etc.
All the functionality of the command line interface is also available
via the GUI.

Here are some command line examples. Set up a dataset (the numbers below are just for illustrative purposes):

     populatedb create -dataset-name SanDiego -lat 32.715 -lon 117.161 -alt 100 -instrument-tz America/Denver -fmin 3500 -fmax 3650 -flo-mhz 3557 -sample-rate 225 -ref-level-dbm 5 -gain 26.4 -fft-size 1024


Populate the DB (assuming the data lives in e:\) as follows

     populatedb populate -dir e:\ -dataset-name SanDiego 

Print the datasets in the Database:

     populatedb print

Print all the metadata in the Database:

     populatedb print-metadata -dataset-name SanDiego

Delete a collection and all the associated metadata

     populatedb drop -dataset-name SanDiego

Please do not put any spaces in the dataset-name parameter 
(for example please dont use a string like "Virgina Beach". 
It is used to create a mongodb collection and mongodb does 
not like spaces in collection names!)

Querying the DB
---------------

There are three ways of querying the DB:

- Via the PYTHON query API
- Via the querydb command line utility
- Via the MATLAB query API


Python Query API
++++++++++++++++

There is just one query interface defined in the module querydb with the 
following method signature:

    find_radar1(datasetName=None, fc_mhz=3550, radar3='U', minSnr = 6, startDate='U', endDate = 'U')


    Parameters:
        - datasetName : The name of the dataset
        - fc_mhz=the center frequency in mhz (default value = 3550)
        - radar3 (Y/N) whether or not to look for radar 3 
          (default is "U" - undefined)
        - minSnr the minimum SNR value (default is 6)
        - startDate : The start date.'%Y-%m-%d %H:%M:%S' format
          (default is "U" - undefined)
        - endDate : The end date '%Y-%m-%d %H:%M:%S' format
          (default is "U" - undefined)

    Return:
        A list of TDMS files matching the query criteria.

You can include module querydb in your code to access the API above.

Query Command Line Utility
+++++++++++++++++++++++++++

There is also a command line utility that you can use to query the database. 
For example:

    querydb.exe -dataset-name=SanDiego -fc-mhz=3570 -radar3=N

returns a list of TDMS files that matched based on searching the metadata:

    [u'E:\\TDMS_Files\\VST11Apr16_093038.tdms']


To specify date ranges, use the start-date and end-date as follows:

     querydb.exe -dataset-name=SanDiego -fc-mhz=3540 -radar3=Y \
        -start-date="2016-04-10 00:00:00" -end-date="2016-04-11 00:00:00"

Note the format for the start and end date must be YYYY-mm-dd HH:MM:SS 
If you specify start date you must specify end date and vice vresa.

returns the following list:

    [u'E:\\TDMS_Files\\VST10Apr16_224711.tdms']

Matlab API interface
++++++++++++++++++++

The MATLAB interface is actually a wrapper around the Python Query API.
To use the MATLAB interface, set the spectrumdb/spectrumdb directory as 
your current directory in MATLAB or include it in your MATLAB path.
If you ran python setup.py install, the MATLAB files will be in the install
location e.g. 

     C:\Python27\Lib\site-packages\spectrumdb-0.1.0-py2.7.egg\spectrumdb

Add this directory to your MATLAB path and run your query.

     >> addpath('C:/Python27/Lib/site-packages/spectrumdb-0.1.0-py2.7.egg/spectrumdb/')
     >> find_radar1('SanDiego','fc_mhz',3570,'radar3','N')

     ans = 

     'E:\TDMS_Files\VST11Apr16_093038.tdms'

Use the following for documentation under MATLAB:

     >> help find_radar1 



Disclaimers
-----------

NIST Disclaimer
+++++++++++++++

This software was developed by employees of the National Institute
of Standards and Technology (NIST), an agency of the Federal
Government. Pursuant to title 17 United States Code Section 105, works
of NIST employees are not subject to copyright protection in the United
States and are considered to be in the public domain. Permission to freely
use, copy, modify, and distribute this software and its documentation
without fee is hereby granted, provided that this notice and disclaimer
of warranty appears in all copies.

THE SOFTWARE IS PROVIDED 'AS IS' WITHOUT ANY WARRANTY OF ANY KIND,
EITHER EXPRESSED, IMPLIED, OR STATUTORY, INCLUDING, BUT NOT LIMITED
TO, ANY WARRANTY THAT THE SOFTWARE WILL CONFORM TO SPECIFICATIONS, ANY
IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE,
AND FREEDOM FROM INFRINGEMENT, AND ANY WARRANTY THAT THE DOCUMENTATION
WILL CONFORM TO THE SOFTWARE, OR ANY WARRANTY THAT THE SOFTWARE WILL BE
ERROR FREE. IN NO EVENT SHALL NASA BE LIABLE FOR ANY DAMAGES, INCLUDING,
BUT NOT LIMITED TO, DIRECT, INDIRECT, SPECIAL OR CONSEQUENTIAL DAMAGES,
ARISING OUT OF, RESULTING FROM, OR IN ANY WAY CONNECTED WITH THIS
SOFTWARE, WHETHER OR NOT BASED UPON WARRANTY, CONTRACT, TORT, OR
OTHERWISE, WHETHER OR NOT INJURY WAS SUSTAINED BY PERSONS OR PROPERTY
OR OTHERWISE, AND WHETHER OR NOT LOSS WAS SUSTAINED FROM, OR AROSE OUT
OF THE RESULTS OF, OR USE OF, THE SOFTWARE OR SERVICES PROVIDED HEREUNDER.

Distributions of NIST software should also include copyright and licensing
statements of any third-party software that are legally bundled with
the code in compliance with the conditions of those licenses.

Copyrights for bundled Scripts
++++++++++++++++++++++++++++++

This software includes code that was downloaded from MATLAB central. 
See licenses directory for redistribution license details.
