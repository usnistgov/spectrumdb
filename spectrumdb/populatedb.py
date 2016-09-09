import os
import sys
import argparse
import nptdms
import pymongo
import json
import nptdms
import timezone
import datetime
import time
from nptdms import TdmsFile




db = pymongo.MongoClient()




def drop_metadata(dataset_name):
    get_metadata(dataset_name).drop()
    db.metadata.drop_collection("metadata." + dataset_name)

def purge_dataset(dataset_name):
    """
    Drop the data and metadata corresponding to a dataset.
    """
    get_metadata(dataset_name).drop()
    get_datasets().remove({"name":dataset_name})


def get_metadata(dataset_name):
    if "metadata." + dataset_name in db.metadata.collection_names():
        return db.metadata["metadata." + dataset_name]
    else:
        db.metadata.create_collection("metadata." + dataset_name)
        return db.metadata["metadata." + dataset_name]

def get_datasets():
    if "datasets" in db.metadata.collection_names():
        return db.metadata["datasets"]
    else:
        db.metadata.create_collection("datasets")
        return db.metadata["datasets"]

def dataset_exists(dataset_name):
    """
    return true if a dataset descriptor exists.
    """
    return get_datasets().find_one({"name":dataset_name}) is not None


def extract_prefix(filename, prefix):
    prefixLength = len(filename) - len(prefix)
    return filename[0:prefixLength]

def get_month(month):
    """
    convert from a month string to a month integer.
    """
    if month == "Jan" :
        return 1
    elif month == "Feb" :
        return 2
    elif month == "Mar" :
        return 3
    elif month == "Apr":
        return 4
    elif month == "May" :
        return 5
    elif month == "Jun" :
        return 6
    elif month == "Jul" :
        return 7
    elif month == "Aug" :
        return 8
    elif month == "Sep" :
        return 9
    elif month == "Oct" :
        return 10
    elif month == "Nov" :
        return 11
    elif month == "Dec" :
        return 12
    else :
        raise Exception("Invalid month string " + month)

def extract_timestamp(prefix):
    """
    Return a python date-time structure corresponding to a file name
    prefix.
    """
    pos = prefix.index('_')
    if pos == -1:
        print "Invalid prefix. Must be of the form Name_xxxxxx where xxxxxx is \
               a timestamp"
    #Characters 4&5 are the day, e.g. 11
    day = int(prefix[3:5])
    #Characters 6,7 & 8 are the month, e.g. Apr
    monthStr = prefix[5:8]
    month = get_month(monthStr)
    #Characters 9 & 10 are the year, e.g. 16
    year = int("20" + prefix[8:10])
    #Character 11 is always an underscore
    #Characters 12 & 13 are the hour in 24 hour time, e.g. 10
    hour = int(prefix[11:13])
    #Characters 14 &15 are the minutes: e.g. 54
    minutes = int(prefix[13:15])
    #Characters 16 & 17 are the seconds: e.g. 22
    seconds = int(prefix[15:17])
    d = datetime.datetime(year,month,day,hour,minutes,seconds)
    return d

def extract_date(prefix):
    pos = prefix.index('_')
    if pos == -1:
        print "Invalid prefix. Must be of the form Name_xxxxxx where xxxxxx is \
               a timestamp"
    date_string = prefix[3,pos]


def debug_print_files(folder):
    for folderName, subfolders, filenames in os.walk(folder):
       if subfolders:
           for subfolder in subfolders:
              debug_print_files(subfolder)
       for filename in filenames:
            filepath = os.path.abspath(folderName + "/" + filename)
            if os.path.exists(filepath) :
                print folderName + "/" + filename



def create_dataset(dataset_name, lat, lon, alt, instrument_tz) :
    """
    Create a dataset if it does not exist. Throw exception if it does 
    exist
    """
    if dataset_exists(dataset_name):
        raise Exception("Dataset is already present")
    datasets = get_datasets()
    info = {}
    info["name"] = dataset_name
    info["lat"] = lat
    info["lon"] = lon
    info["alt"] = alt
    info["instrumentTz"] = instrument_tz
    tzId, tzName = timezone.getLocalTimeZoneFromGoogle(int(time.time()),
            lat,lon)
    info["measurementTz"] = tzId
    datasets.insert(info)

def get_dataset(dataset_name):
    """
    Get the dataset descriptor for a given dataset_name.
    """
    retval = get_datasets().find_one({"name":dataset_name})
    if retval is None:
        raise Exception("Dataset " + dataset_name + " not found ")
    return retval


def recursive_walk_metadata(dataset_name,folder,prefix_list):
    """
    Walk through the subfolders picking up the metadata and populating
    the metadata as a JSON document into mongodb.
    """
    if not dataset_exists(dataset_name):
        raise Exception("dataset " + dataset_name + " not found. Create it.")
    dataset = get_dataset(dataset_name)

    for folderName, subfolders, filenames in os.walk(folder):
           if subfolders:
               for subfolder in subfolders:
                 recursive_walk_metadata(dataset_name,subfolder, prefix_list)

           for filename in filenames:
                pathname = os.path.abspath(folderName + "/"  + filename)
                if filename.endswith("_MaxSpectra.tsv"):
                    prefix = extract_prefix(filename, "_MaxSpectra.tsv")
                    metadataType = "MaxSpectra"
                elif filename.endswith("_PeakAmplitude.txt"):
                    prefix = extract_prefix(filename,"_PeakAmplitude.txt")
                    metadataType = "PeakAmplitude"
                elif filename.endswith(".tdms"):
                    prefix = extract_prefix(filename,".tdms")
                    metadataType = "tdms"
                    tdmsMetadata = TdmsFile(pathname).getJsonMetadata()
                else:
                    continue

                query = {"prefix":prefix}
                metadata = get_metadata(dataset_name).find_one(query)
                if metadata is None:
                    print "create record for ", prefix
                    metadata = {}
                    metadata["prefix"] = prefix
                    metadata[metadataType] = pathname
                    date = extract_timestamp(prefix)
                    ts = time.mktime(date.timetuple())
                    metadata["instrumentDate"] = str(date)
                    metadata["instrumentTimeStamp"] = ts
                    target_tz = dataset["measurementTz"]
                    instrument_tz = dataset["instrumentTz"]
                    targetTimestamp = timezone.translateTime(
                            date,instrument_tz,target_tz)
                    localTimestamp = time.mktime(targetTimestamp.timetuple())
                    metadata["measurementDate"] = str(targetTimestamp)
                    metadata["measurementTimeStamp"] = localTimestamp
                    lat = dataset["lat"]
                    lon = dataset["lon"]
                    universalTimestamp = timezone.getUniversalTimeAtLocation(
                            localTimestamp,lat,lon)
                    metadata["universalTimeStamp"] = universalTimestamp
                    if metadataType == "tdms":
                        metadata["tdmsMetadata"] = tdmsMetadata
                    get_metadata(dataset_name).insert(metadata)
                else:
                    metadata[metadataType] = pathname
                    if metadataType == "tdms":
                        metadata["tdmsMetadata"] = tdmsMetadata
                    get_metadata(dataset_name).update({"prefix":prefix},
                            metadata, upsert = False)

                prefix_list.add(prefix)

def list_datasets():
    datasets = get_datasets()
    cur = datasets.find()
    result = []
    for dataset in cur:
        del dataset["_id"]
        result.append(dataset)
    return result


def dump_db(dataset_name):
    cur = get_metadata(dataset_name).find()
    for metadata in cur:
        del metadata["_id"]
        print (json.dumps(metadata,indent = 4))

if __name__ == "__main__":
    global lat, lon, alt
    parser = argparse.ArgumentParser(description = "Args for populating "
            "the DB")
    parser.add_argument('-dir', type = str , help =  "root directory for the"
            " data", default=None)

    parser.add_argument('-dataset-name', type = str, help = "Dataset Name",
            default = None)

    parser.add_argument('-lat', type = float, help = "latitude ", default=None)

    parser.add_argument('-lon', type = float, help = "longitude", default=None)

    parser.add_argument('-alt', type = float, help = "longitude", default=None)

    parser.add_argument('-instrument-tz', type = str, help = "timezone ID for"
            "measurement system (e.g. America/Denver). "
            "Note: Do not use names such as EDT, MDT etc.", default = None)

    parser.add_argument('-action', type = str,
            help = "drop | populate | print", default = None)


    args = parser.parse_args()
    root_dir = args.dir
    dataset_name = args.dataset_name
    action = args.action
    if (action != "populate" and action  != "print" and action != "drop" and
            action != "create-dataset") :
        print ("Action must be populate or print or drop or create-dataset")
        sys.exit()


    if dataset_name is None:
        print "Please specify dataset name"
        sys.exit()


    if action is "populate" and (lat is None or lon is None or alt is None) :
        print "Please specify location (lat/lon/alt) where data was gathered."
        sys.exit()


    if action == "populate" and root_dir is None:
        print "Please specify root directory for the data set"
        sys.exit()

    if action == "populate":
        prefix_list  = set([])
        recursive_walk_metadata(dataset_name,root_dir,prefix_list)
    elif action == "drop":
        purge_dataset(dataset_name)
    elif action == "create-dataset":
        if (args.lat is None or args.lon is None or args.alt is None 
            or args.instrument_tz is None):
            print ("specify lat, lon, alt, instrument_tz")
            sys.exit()
        lat = float(args.lat)
        lon = float(args.lon)
        alt = float(args.alt)
        instrument_tz = args.instrument_tz
        create_dataset(dataset_name, lat, lon, alt, instrument_tz)
    elif action == "dump":
        dump_db(dataset_name)
    else:
        print("Invalid action specified")


