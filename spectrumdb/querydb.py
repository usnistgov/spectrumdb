import pymongo
import timezone
import time

#The main query I have been thinking of is:
#
#   (Files which contain Radar-1 at 3550 MHz) & (Files with do not contain Radar-3)
#   & (Files with SNR above 6dB)

#I would also repeat this query with two other frequencies in the first clause;
#3520 MHz and 3600 MHz. These main queries would allow us to do the preliminary
#data analysis for upcoming reports. We would also, for the same report, want to
#pick subsets of data to analyze:
#
#    (Files which contain Radar-1 at 3550 MHz) & (Files with do not contain
#            Radar-3) & (Files with SNR above 6dB) & 
#           (Beginning date/time=X) & (Ending Date/time=Y)




import populatedb



# TODO: This should be encoded into a configuration setting so that you don't have to
# search to find where these values live.



enbw_dbHz = 53.8
cal_db = 1.6
# This table is incomplete.
refLevel = [-30, 5]
noiseFloor=[-168.3, -153.5]

DEFAULT_REFLVL = 5


db = pymongo.MongoClient()

def get_noise_floor_from_ref_level(ref):
    """
    Use linear interpolation (?) to get noise floor from ref level based on a
    table lookup.
    """
    for i in range (0,len(refLevel)-1):
        if ref == refLevel[i] :
            return noiseFloor[i]
        elif ref == refLevel[i+1] :
            return noiseFloor[i+1]
        else:
            slope = (noiseFloor[i+1] - noiseFloor[i])/(refLevel[i+1] -
                    refLevel[i])
            return (ref - refLevel[i])* slope + noiseFloor[i]
    raise Exception("cannot map refLevel to noise floor")


def get_peak_power_in_dbm_per_hz(peakPower):
    """
    Get the peak poer in db per Hz from the given peak power.
    """
    return peakPower - enbw_dbHz  + cal_db


def compute_snr(peak_power,ref_level = 5) :
    """
    Compute the SNR given the peak power and the ref level.
    Default ref level is 5
    """
    noiseFloor = get_noise_floor_from_ref_level(ref_level)
    peakPowerDbmPerHz = get_peak_power_in_dbm_per_hz(peak_power)
    return peak_power - noiseFloor

def find_radar1(datasetName=None, fc_mhz=3550, radar3=None, minSnr = 6, startDate=None,
        endDate = None):
    """
    Return a list of TDMS files having radar1 identified and satisfying the given constraints.

    Parameters:
        - datasetName : The name of the dataset
        - fc=the center frequency in mhz (default value = 3550)
        - radar3 (Y/N) whether or not to look for radar 3 (default is "N")
        - minSnr the minimum SNR value (default is 6)
        - startDate : The start date.'%Y-%m-%d %H:%M:%S' format
        - endDate : The end date '%Y-%m-%d %H:%M:%S' format

    Return:
        A list of TDMS files matching the query criteria.

    """
    dataset = populatedb.get_dataset(datasetName)
    if dataset is None:
        raise "Dataset not found"
    metadataCollection = populatedb.get_metadata(datasetName)
    if metadataCollection is None:
        return None

    measurementTimeZone = dataset["measurementTz"]

    if startDate is not None and endDate is None or\
        startDate is None and endDate is not None:
        raise "Malformed query start/end date"
    if startDate is not None:
        #'%Y-%m-%d %H:%M:%S' format
        startTimeStamp = time.mktime(time.strptime(startDate, '%Y-%m-%d %H:%M:%S'))
        endTimeStamp   = time.mktime(time.strptime(endDate, '%Y-%m-%d %H:%M:%S'))
        if radar3 is not None:
            query = {"$and": [{"RADAR1":{"$exists":True}},{"RADAR3":radar3},
                        {"measurementTimeStamp": {"$gte":startTimeStamp} },
                        {"measurementTimeStamp": {"$lte":endTimeStamp}} ]}
        else:
            query = {"$and": [{"RADAR1":{"$exists":True}},
                        {"measurementTimeStamp": {"$gte":startTimeStamp} },
                        {"measurementTimeStamp": {"$lte":endTimeStamp}} ]}
    else:
        if radar3 is not None:
            query = {"$and": [{"RADAR1":{"$exists":True}},{"RADAR3":radar3}] }
        else:
            query = {"RADAR1":{"$exists":True}}

    cur = metadataCollection.find( query )
    if cur is None or cur.count() == 0:
        return []
    retval = []
    for metadata in cur:
        radarRecs = metadata["RADAR1"]
        for radarRec in radarRecs:
            if radarRec["fc_mhz"] == fc_mhz:
                peakPower = radarRec["peakPowerDbm"]
                if "refLvl" in metadata :
                    refLvl = metadata["refLvl"]
                else:
                    # The default ref level
                    refLvl = 5
                snr = compute_snr(peakPower,refLvl)
                if snr > minSnr:
                    retval.append(metadata["tdms"])
    return retval



