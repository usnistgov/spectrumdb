SpectrumDb -- a manager for data gathered from spectrum experiments
===================================================================


This project publishes a data manager for RADAR spectrum data readings. It scans through a set of directories, builds metadata based on the files it encounters and puts the metadata
into a mongodb collection which can later be queried and updated.


Prerequisites
--------------

- Mongodb 3.3 (see mongodb.org), Install the MongoDB service by starting
mongod.exe with the --install option. To use an alternate dbpath, specify
the path in the configuration file (e.g. C:\mongodb\mongod.cfg) or on
the command line with the --dbpath option. You can put the database in
any directory on the filesystem.

   mongd.exe -install -dbpath c:/mongodb -log c:/Temp/mongolog.txt

Python dependencies
-------------------

You can install most of the following dependencies from a github git shell.
Run python setup.py install

- Python 2.7.12 set your path to python.exe 
- pymongo 
- numpy (pip install numpy)
- pytz (pip install pytz
- npTDMS (Get this from the fork https://github.com/usnistgov/npTDMS )
- pyqt4 use the installer from here 
    http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.11.4/PyQt4-4.11.4-gpl-Py2.7-Qt4.8.7-x64.exe  
- Matlab engine connector for python. Follow the instructions here.
  https://www.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html

After installing dependencies

    python setup.py install 



Google Timzone API
------------------

This is used for lat/lon to timezone conversion and for local time to universal
time conversion. This turns out to be a tricky problem because local time is
often set by legislation (for example whether or not Daylight Savings Time is in
use). You can get an API key by getting a google account and using the
developer console (google around a bit to figure out how). 

- Get a google timezone API key and set up the followng environment
variable. GOOGLE\_TIMZONE\_API\_KEY in your windows environment. This
is required to  determine the timezone for the LAT/LON where you gathered
data.



Starting
--------

Start mongod 

    # Create a mongod folder where you want the db to reside
    md c:\mongodb
    mongod -dbpath = c:\mongodb

Note: if you installed mongod as a service (see above), 
it should start when you restart windows. If it does not auto-start,
then start it from the command line.

Starting the Graphical user interface
-------------------------------------

Start the db gui application

    dbgui

You have to define a dataset first and then populate it with data.
The UI interactions are fairly obvious. We will not bore you by
giving tiresome instructions.
  

Command line invocations
--------------------------

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

Query API
---------

There is just one query interface defined in the module querydb with the 
following method signature:

   find_radar1(datasetName=None, fc_mhz=3550, radar3=None,
        minSnr = 6, startDate=None, endDate = None)


    Parameters:
        - datasetName : The name of the dataset
        - fc=the center frequency in mhz (default value = 3550)
        - radar3 (Y/N) whether or not to look for radar 3 (default is "N")
        - minSnr the minimum SNR value (default is 6)
        - startDate : The start date.'%Y-%m-%d %H:%M:%S' format
        - endDate : The end date '%Y-%m-%d %H:%M:%S' format

    Return:
        A list of TDMS files matching the query criteria.

You can include module querydb in your code to access the API above.

Query DB Command Line Utility
-----------------------------

There is also a command line utility that you can use to query the database. 
For example:

    querydb.exe -dataset-name=SanDiego -fc-mhz=3570 -radar3=N

returns a list of TDMS files that matched based on searching the metadata:

    [u'E:\\TDMS_Files\\VST11Apr16_093038.tdms']


To specify date ranges, use the start-date and end-date as follows:
    querydb.exe -dataset-name=SanDiego -fc-mhz=3540 -radar3=Y \
        -start-date="2016-04-10 00:00:00" -end-date="2016-04-11 00:00:00"

returns the following list:

    [u'E:\\TDMS_Files\\VST10Apr16_224711.tdms']

Matlab interface
----------------

TBD

    



Disclaimers
-----------

This software was developed by employees of the National Institute of Standards and Technology (NIST). This software has been contributed to the public domain. Pursuant to title 15 Untied States Code Section 105, works of NIST employees are not subject to copyright protection in the United States and are considered to be in the public domain. As a result, a formal license is not needed to use this software.

This software is provided "AS IS." NIST MAKES NO WARRANTY OF ANY KIND, EXPRESS, IMPLIED OR STATUTORY, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT AND DATA ACCURACY. NIST does not warrant or make any representations regarding the use of the software or the results thereof, including but not limited to the correctness, accuracy, reliability or usefulness of this software.

