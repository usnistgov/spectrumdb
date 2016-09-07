import os
import sys
import argparse
import nptdms
import pymongo
import json
import nptdms
from nptdms import TdmsFile




db = pymongo.MongoClient()




def drop_metadata(datasetName):
    get_metadata(datasetName).drop()
    db.metadata.drop_collection("metadata." + datasetName)


def get_metadata(datasetName):
    if "metadata." + datasetName in db.metadata.collection_names():
        return db.metadata["metadata." + datasetName]
    else:
        db.metadata.create_collection("metadata." + datasetName)
        return db.metadata["metadata." + datasetName]


def extract_prefix(filename, prefix):
    prefixLength = len(filename) - len(prefix)
    return filename[0:prefixLength]

def extract_timestamp(prefix):
    pos = prefix.index('_')
    ts = prefix[index+l, len(prefix)]
    return int(ts)




def recursive_walk_metadata(datasetName,folder,prefix_list):
    for folderName, subfolders, filenames in os.walk(folder):
           if subfolders:
               for subfolder in subfolders:
                 recursive_walk_metadata(datasetName,subfolder, prefix_list)

           for filename in filenames:
                pathname = os.path.abspath(folderName + "/" + subfolder + "/" +
                        filename)
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
                metadata = get_metadata(datasetName).find_one(query)
                if metadata is None:
                    metadata = {}
                    metadata["prefix"] = prefix
                    metadata[metadataType] = pathname
                    if metadataType == "tdms":
                        metadata["tdmsMetadata"] = tdmsMetadata
                    get_metadata(datasetName).insert(metadata)
                else:
                    metadata[metadataType] = pathname
                    if metadataType == "tdms":
                        metadata["tdmsMetadata"] = tdmsMetadata
                    get_metadata(datasetName).update({"prefix":prefix},
                            metadata, upsert = False)

                prefix_list.add(prefix)

def dump_db(datasetName):
    cur = get_metadata(datasetName).find()
    for metadata in cur:
        del metadata["_id"]
        print (json.dumps(metadata,indent = 4))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Args for populating "
            "the DB")
    parser.add_argument('-dir', type = str , help =  "root directory for the"
            " data")

    parser.add_argument('-datasetName', type = str, help = "Dataset Name")

    parser.add_argument('-action', type = str, help = "drop | populate",
            default = "populate")


    args = parser.parse_args()
    root_dir = args.dir
    datasetName = args.datasetName
    action = args.action
    if datasetName is None:
        print "Please specify dataset name"
        sys.exit()

    if action == "populate" and root_dir is None:
        print "Please specify root directory for the data set"
        sys.exit()

    prefix_list  = set([])
    if action == "populate":
        recursive_walk_metadata(datasetName,root_dir,prefix_list)
        print (prefix_list)
        dump_db(datasetName)
    elif action == "drop":
        drop_metadata(datasetName)
    else:
        print("Invalid action specified")


