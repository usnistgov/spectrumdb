SpectrumDb -- a manager for data gathered from spectrum experiments
===================================================================


This project publishes a data manager for RADAR spectrum data readings. It scans through a set of directories, builds metadata based on the files it encounters and puts the metadata
into a mongodb collection which can later be queried and updated.


Prerequisites
-------------

- Mongodb 3.3 (see mongodb.org), Install the MongoDB service by starting
mongod.exe with the --install option. To use an alternate dbpath, specify
the path in the configuration file (e.g. C:\mongodb\mongod.cfg) or on
the command line with the --dbpath option. You can put the database in
any directory on the filesystem.

   mongd.exe -install -dbpath c:/mongodb -log c:/Temp/mongolog.txt

Python dependencies
-------------------

- Python 2.7.12 set your path to python.exe 
- pymongo 
- openpyxl
- numpy (pip install numpy)
- pytz (pip install pytz
- npTDMS (NOTE: get this from the fork https://github.com/usnistgov/npTDMS )
- pyqt4 use the installer from here 
    http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.11.4/PyQt4-4.11.4-gpl-Py2.7-Qt4.8.7-x64.exe  
- Matlab engine connector for python. 

Google Timzone API
------------------

This is used for lat/lon to timezone conversion and for local time to universal
time conversion. This turns out to be a tricky problem because local time is
often set by legislation (for example whether or not Daylight Savings Time is in
use). You can get an API key by getting a google account and using the
developer console (google around a bit to figure out how). 

- Get a google timezone API key and set up the followng environment
variable. GOOGLE\_TIMZONE\_API\_KEY in your windows environment. This
is required to do time conversions from your lat/lon location where you
gathered data to universal time. 



Starting
--------

- Start mongod 

    # Create a mongod folder where you want the db to reside
    md c:\mongodb
    mongod -dbpath = c:\mongodb

Note: if you installed mongod as a service (see above), 
it should start when you restart windows.

- Start the db application

    python dbgui.py  
  

Example invocations
-------------------


The tool provides command line as well as GUI based invocation.
You can look at the options using python populatedb.py -help etc.

Here are some command line examples. Set up a dataset (the numbers below are just for illustrative purposes):

     python populatedb.py create -dataset-name SanDiego -lat 32.715 -lon 117.161 -alt 100 -instrument-tz America/Denver -fmin 3500 -fmax 3650 -flo-mhz 3557 -sample-rate 225 -ref-level-dbm 5 -gain 26.4 -fft-size 1024


Populate the DB (assuming the data lives in e:\) as follows

     python populatedb.py populate -dir e:\ -dataset-name SanDiego 

Print the datasets in the Database:

     python populatedb.py print

Print all the metadata in the Database:

     python populatedb.py print-metadata -dataset-name SanDiego

Delete a collection and all the associated metadata

     python populatedb.py drop -dataset-name SanDiego

Please do not put any spaces in the dataset-name parameter 
(for example please dont use a string like "Virgina Beach". 
It is used to create a mongodb collection and mongodb does 
not like spaces in collection names!)

