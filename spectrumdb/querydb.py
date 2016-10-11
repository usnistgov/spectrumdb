
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
import pymongo
import timezone
import time
import argparse

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

def find_radar1(datasetName=None, fc_mhz=3550, radar3='U',
        minSnr = 6, startDate='U', endDate = 'U'):
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
        raise Exception("Dataset not found")
    metadataCollection = populatedb.get_metadata(datasetName)
    if metadataCollection is None:
        return []

    measurementTimeZone = dataset["measurementTz"]

    if startDate != "U" and endDate == "U" or\
        startDate == "U" and endDate != "U":
        raise Exception("Malformed query start/end date")
    if startDate != 'U':
        #'%Y-%m-%d %H:%M:%S' format
        #print "startDate [", startDate, "]"
        startTimeStamp = time.mktime(time.strptime(startDate, '%Y-%m-%d %H:%M:%S'))
        endTimeStamp   = time.mktime(time.strptime(endDate, '%Y-%m-%d %H:%M:%S'))
        if startTimeStamp > endTimeStamp:
            raise Exception("Start timestamp exceeds end timestamp")
        if radar3 != 'U':
            query = {"$and": [{"RADAR1":{"$exists":True}},{"RADAR3":radar3},
                        {"measurementTimeStamp": {"$gte":startTimeStamp} },
                        {"measurementTimeStamp": {"$lte":endTimeStamp}} ]}
        else:
            query = {"$and": [{"RADAR1":{"$exists":True}},
                        {"measurementTimeStamp": {"$gte":startTimeStamp} },
                        {"measurementTimeStamp": {"$lte":endTimeStamp}} ]}
    else:
        if radar3 != 'U':
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



def main():
    parser = argparse.ArgumentParser(description = "query the DB",
            add_help=False)
    parser.add_argument("-dataset-name",type=str, default=None,required=True,
            help="Dataset Name")
    parser.add_argument("-fc-mhz",type=int, default=3550,required=False,
            help="Center frequency where you expect to find Radar")
    parser.add_argument("-radar3",type=str, default="N",required=False,
            help="Y/N specifies if radar3 is present")
    parser.add_argument("-min-snr",type=float, default=6,required=False,
            help="Min SNR")
    parser.add_argument("-start-date",type=str, default=None,required=False,
            help="start date in '%Y-%m-%d %H:%M:%S' format")
    parser.add_argument("-end-date",type=str, default=None,required=False,
            help="End date in '%Y-%m-%d %H:%M:%S' format")

    args = parser.parse_args()

    dataset_name = args.dataset_name
    fc = args.fc_mhz
    radar3 = args.radar3
    min_snr = args.min_snr
    start_date = args.start_date
    end_date = args.end_date
    print find_radar1(datasetName=dataset_name, fc_mhz=fc, radar3=radar3,
            startDate=start_date,endDate=end_date)


if __name__ == "__main__":
    main()

