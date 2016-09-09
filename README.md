## SpectrumDb -- a manager for data gathered from spectrum experiments


This project publishes a data manager for RADAR spectrum data readings. It scans through a set of directories, builds metadata based on the files it encounters and puts the metadata
into a mongodb collection which can later be queried and updated.


# Prerequisites

- Mongodb 3.3 (see mongodb.org). You can install mongod to start as a windows
sevice as follows, for example:

   mongd.exe -install -dbpath c:/mongodb -log c:/Temp/mongolog.txt

- Python 2.7.12 set your path to python.exe 
- numpy (pip install numpy)
- pytz (pip install pytz
- npTDMS ( get this from the fork https://github.com/usnistgov/npTDMS )
- Get a google timezone API key and set up the followng environment variable. GOOGLE\_TIMZONE\_API\_KEY in your windows environment. This is required to do time conversions from your lat/lon location where you gathered data to universal time. 

You can install all dependencies in one shot by using 

  pip install -r requirements.txt



# Starting

- Start mongod 

  md c:\mongodb
  mongod -dbpath = c:\mongodb

Note: if you installed mongod as a service (see above), it should start when you restart windows.
  

# Populating the db with new data

Populate the DB (assuming the data lives in e:\) as follows

  python populate_db.py -dir e:\ -datasetName SanDiego -lat 32.715 -lon 117.161 -alt 100 -action populate

Please do not put any spaces in the datasetName parameter (for example please dont use a string like "Virgina Beach". It is used to create a mongodb collection and mongodb does not like spaces in collection names!)

