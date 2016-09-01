## SpectrumDb -- a manager for data gathered from spectrum experiments


This project publishes a data manager for RADAR spectrum data readings. It scans through a set of directories, builds metadata based on the files it encounters and puts the metadata
into a mongodb collection which can later be queried and updated.


# Prerequisites

- Mongodb 3.3 (see mongodb.org)
- Python 2.7.12 set your path to python.exe 
- numpy (pip install numpy)
- npTDMS ( get this from the fork https://github.com/usnistgov/npTDMS )


# Configuring

- Edit config.json and set up your dbpath  

# Starting

- Start mongod 

  md c:\dbdir
  mongod -dbpath = c:\dbdir
  

# Populating the db with new data

Populate the DB (assuming the data lives in e:\) as follows

  python populate_db.py -dir e:\ -datasetName SanDiego

Please do not put any spaces in the datasetName. It is used to create a mongodb collection!

