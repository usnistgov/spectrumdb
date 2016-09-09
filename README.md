## SpectrumDb -- a manager for data gathered from spectrum experiments


This project publishes a data manager for RADAR spectrum data readings. It scans through a set of directories, builds metadata based on the files it encounters and puts the metadata
into a mongodb collection which can later be queried and updated.


# Prerequisites

- Mongodb 3.3 (see mongodb.org), Install the MongoDB service by starting
mongod.exe with the --install option. To use an alternate dbpath, specify
the path in the configuration file (e.g. C:\mongodb\mongod.cfg) or on
the command line with the --dbpath option. You can put the database in
any directory on the filesystem.

   mongd.exe -install -dbpath c:/mongodb -log c:/Temp/mongolog.txt


- Python 2.7.12 set your path to python.exe 
- pymongo 
- numpy (pip install numpy)
- pytz (pip install pytz
- npTDMS ( get this from the fork https://github.com/usnistgov/npTDMS )
- Get a google timezone API key and set up the followng environment
variable. GOOGLE\_TIMZONE\_API\_KEY in your windows environment. This
is required to do time conversions from your lat/lon location where you
gathered data to universal time. 



# Starting

- Start mongod 

  md c:\mongodb
  mongod -dbpath = c:\mongodb

Note: if you installed mongod as a service (see above), it should start when you restart windows.
  

# Example invocations

Set up a dataset (the numbers below are just for illustrative purposes):

   python populatedb.py -action create-dataset -dataset-name SanDiego -lat 32.715 -lon 117.161 -alt 100 



Populate the DB (assuming the data lives in e:\) as follows

  python populatedb.py -action populate -dir e:\ -dataset-name SanDiego 

Print the datasets in the Database:

  python populatedb.py -action print-datasets

Print all the metadata in the Database:

  python populatedb.py -action print-metadata

Delete a collection

  python populatedb.py -action drop -dataset-name SanDiego

Please do not put any spaces in the datasetName parameter (for example please dont use a string like "Virgina Beach". It is used to create a mongodb collection and mongodb does not like spaces in collection names!)

