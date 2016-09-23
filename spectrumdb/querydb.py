import pymongo

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


