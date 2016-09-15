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
import numpy as np
import math
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


def create_dataset(dataset_name=None,
                lat=None,
                lon=None,
                alt=None,
                instrument_tz=None,
                antenna=None,
                gain=None,
                reflevel_dbm=None,
                flo_mhz=None,
                fmin=None,
                fmax=None,
                sample_rate=None,
                fft_size=None):
    """
    Create a dataset if it does not exist. Throw exception if it does
    exist.
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
    info["antenna"] = antenna
    info["gain"] = gain
    info["reflevel_dbm"] = reflevel_dbm
    info["fmin"] = fmin
    info["fmax"] = fmax
    info["flo_mhz"]= flo_mhz
    info["sample_rate"] = sample_rate
    info["fft_size"] = fft_size

    datasets.insert(info)

def get_dataset(dataset_name):
    """
    Get the dataset descriptor for a given dataset_name.
    """
    retval = get_datasets().find_one({"name":dataset_name})
    if retval is None:
        raise Exception("Dataset " + dataset_name + " not found ")
    return retval


def compute_peak_stats_worker(fname,fmin,fmax,flo_mhz,fft_size,sample_rate,gaindB):
    # convert amplifier gain to linear units
    Vgain=pow(10,(gaindB/20.0))
    # VST calibration in dB
    VcaldB=1.64
    Vcal=pow(10,(VcaldB/20.0))
    # Load the data into a 2d array.
    temp = np.loadtxt(fname,dtype='float',delimiter='\t')
    # Normalize the data with fft size
    z = temp/fft_size
    #Apply calibrations for front end gain, cable loss, splitter loss
    z = z/Vgain
    z = z*Vcal
    z_len = len(z)
    #Frequency array for the FFT
    fmhz = (float(sample_rate)/fft_size)*np.arange(-fft_size/2,fft_size/2) + flo_mhz
    # Power values in dbm
    z_dbm = 20*np.log10(z) - 10*np.log10(100) + 30
    #set fc to frequency of peak power between 3520 MHz and fLO+100 MHz,
    #excluding the LO. The following will return an index array of
    #non-contiguous elements.
    fj = ((fmhz >= 3520) & (fmhz <= flo_mhz+100) & ((fmhz < flo_mhz-1) |
        (fmhz > flo_mhz+1))).nonzero()
    # fmhz_j is the frequencies of interest in our range 
    fmhz_j = fmhz[fj]
    # slice the array to the indices of interest. All rows and a subset of
    # columns in the range of interest.
    sliced_array = z_dbm[:,fj[0]]
    # compute the 2d index value of the max location. argmax retuns a 1-d
    # result. unravel_index gives the 2d index values.
    fci = np.unravel_index(np.argmax(sliced_array),np.shape(sliced_array))
    # The max power value at the location of interest.
    pmax_dbm = np.round(sliced_array[fci],decimals=1)
    # Find the center frequency where the power is max.
    fc_mhz = fmhz_j[fci[1]]
    # The frequencies of interest where we want to compute statistics
    fi = np.arange(fmin,fmax + 10,10)
    # initialize indices. These are indices which fmhz is closest to fi
    # There might be a way to do this without looping in numpy
    k = 0
    m = 0
    r = []
    while (m < len(fmhz) and k < len(fi)):
        if fmhz[m] >= fi[k]:
            k += 1
            r.append(m)
        else:
            m += 1

    # r now contains FFT indices that are close to the frequencies of interest.
    # Adjust the indices to be closest to the frequencies of interest by
    # looking in the neighborhood. j is the fft freqindices that are closest to the
    # indices of interest.

    j = []
    k = 0
    for m in r:
         d = abs(fi[k] - fmhz[m])
         d1 = abs(fi[k] - fmhz[m-1])
         d2 = abs(fi[k] + fmhz[m+1])
         min_diff = min(d,d1,d2)
         if min_diff == d:
             j.append(m)
         elif min_diff == d1:
             j.append(m-1)
         elif min_diff == d2:
             j.append(m+1)
         k = k +1


    # now compute the power vector for each column
    zisq = np.power(z[:,j],2)
    # Compute the mean for each column
    zsq_avg = np.mean(zisq,axis=0)
    # Compute the 75th. percentile for each column
    zsq_75 = np.percentile(zisq,75,axis=0)
    # Compute the 25th. percentile for each column
    zsq_25 = np.percentile(zisq,25,axis=0)
    # Compute the mean value in dbm 
    pmean_dBm=np.round(10*np.log10(zsq_avg)-10*np.log10(100)+30,decimals=1)
    # Compute the inter quartile range for each column
    iqr_dBm=np.round(10*np.log10(zsq_75)-10*np.log10(zsq_25),decimals=1)

    retval = {}
    retval["pmax_dbm"] = pmax_dbm
    retval["fpeak_mhz"] = np.round(fc_mhz,decimals=0)
    retval["pmean_dbm"] = pmean_dBm
    retval["iqr_dbm"] = iqr_dBm
    return retval




def compute_peak_stats(dataset_name,fname) :
    dataset = get_dataset(dataset_name)
    fmin = dataset['fmin']
    fmax = dataset['fmax']
    flo_mhz = dataset["flo_mhz"]
    sample_rate = dataset["sample_rate"]
    fft_size = dataset["fft_size"]
    gain = dataset["gain"]
    compute_peak_stats_worker(fname,fmin,fmax,flo_mhz,fft_size,sample_rate,gain)



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


def print_datasets():
    datasets = get_datasets()
    cur = datasets.find()
    for dataset in cur:
        del dataset["_id"]
        print json.dumps(dataset, indent=4)

def dump_db(dataset_name):
    cur = get_metadata(dataset_name).find()
    for metadata in cur:
        del metadata["_id"]
        print (json.dumps(metadata,indent = 4))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Setup the DB",
            add_help=False)
    subparsers = parser.add_subparsers()
    drop_parser = subparsers.add_parser('drop', help='drop the dataset')
    populate_parser = subparsers.add_parser('populate',
            help = 'populate dataset')
    print_parser = subparsers.add_parser('print', help = 'print all datasets')
    create_parser = subparsers.add_parser('create', help = 'create dataset')
    print_metadata_parser = subparsers.add_parser('print-metadata',help =
        "print metadata for a dataset")
    print_parser.set_defaults(action="print")
    populate_parser.set_defaults(action="populate")
    create_parser.set_defaults(action="create")
    print_metadata_parser.set_defaults(action="print-metadata")

    populate_parser.add_argument('-dir', type = str ,
            required=True,
            help =  "root directory for the"
            " data", default=None)

    populate_parser.add_argument('-dataset-name',
            required=True,
            type = str, help = "Dataset Name",
            default = None)

    drop_parser.add_argument('-dataset-name',
            required=True,
            type = str, help = "Dataset Name",
            default = None)

    print_metadata_parser.add_argument('-dataset-name',
            required=True,
            type = str, help = "Dataset Name",
            default = None)

    create_parser.add_argument('-lat', type = float,
            required=True,
            help = "latitude ", default=None)

    create_parser.add_argument('-lon', type = float,
            required=True,
            help = "longitude", default=None)

    create_parser.add_argument('-alt', type = float,
            required=True,
            help = "altitude (m)", default=None)

    create_parser.add_argument('-instrument-tz',
            required=True,
            type = str, help = "timezone ID for"
            "measurement system (e.g. America/Denver). "
            "Note: Do not use names such as EDT, MDT etc.", default = None)

    create_parser.add_argument('-gain', type = float,
            required=True,
            help = "net of front end gain, cable loss, splitter loss",
            default = None)

    create_parser.add_argument('-fmin', type = float,
            required=True,
            help = "Min frequency (MHz)",
            default = None)

    create_parser.add_argument('-fmax', type = float,
            required=True,
            help = "Max frequency (MHz)",
            default = None)

    create_parser.add_argument('-antenna', type = str,
            required=True,
            help = "Antenna type (string)",
            default = None)

    create_parser.add_argument('-flo-mhz', type = float,
            required=True,
            help = "local oscillator frequency in MHz",
            default = None)

    create_parser.add_argument("-reflevel-dbm", type = float,
            required=True,
            help = "reference level of VST (dBm)",
            default = None)

    create_parser.add_argument("-sample-rate", type=float,
            required=True,
            help = "sampling frequency in MHz",
            default = None)

    create_parser.add_argument("-fft-size", type = int,
            required=True,
            help = "fft size",
            default = None)

    args = parser.parse_args()
    action = args.action


    if action == "populate":
        root_dir = args.dir
        dataset_name = args.dataset_name
        prefix_list  = set([])
        recursive_walk_metadata(dataset_name,root_dir,prefix_list)
    elif action == "drop":
        dataset_name = args.dataset_name
        purge_dataset(dataset_name)
    elif action == "create":
        lat = float(args.lat)
        lon = float(args.lon)
        alt = float(args.alt)
        instrument_tz = args.instrument_tz
        gain = float(args.gain)
        minfreq = float(args.fmin)
        maxfreq = float(args.fmax)
        antenna = str(args.antenna)
        flo_mhz = float(args.flo_mhz)
        sample_rate = float(args.sample_rate)
        fft_size = int(args.fft_size)
        reflevel_dbm = float(args.reflevel_dbm)
        create_dataset(dataset_name=dataset_name,
                lat=lat,
                lon=lon,
                alt=alt,
                instrument_tz=instrument_tz,
                antenna=antenna,
                gain=gain,
                reflevel_dbm=reflevel_dbm,
                flo_mhz=flo_mhz,
                fmin=fmin,
                fmax=fmax,
                sample_rate=sample_rate,
                fft_size=fft_size)
    elif action == "print":
        print_datasets()
    elif action == "print-metadata":
        dataset_name = args.dataset_name
        dump_db(dataset_name)
    else:
        print("Invalid action specified")


