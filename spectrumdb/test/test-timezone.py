import sys
sys.path.append("../")
import unittest
import json
import timezone
import math
import os
import argparse
import datetime
import time

class TimezoneTest(unittest.TestCase):
    def setUp(self):
        pass

    def testGetDayBoundaryOffset(self):
        global tzId
        t = timezone.getLocalUtcTimeStamp()
        startOfToday = timezone.getDayBoundaryTimeStampFromUtcTimeStamp(t, tzId)
        self.assertTrue(t > startOfToday)
        delta = t - startOfToday
        now = datetime.datetime.now()
        hourOffset = now.hour
        minOffset = now.minute
        secondOffset = now.second
        newDelta = hourOffset*60*60 + minOffset*60 + secondOffset
        self.assertTrue(abs(newDelta -delta ) < 2)


    def testGetTimezoneIdAtLocation(self):
        global lat, lon,tzId
        now = time.time()
        testTzId,testTzName = timezone.getLocalTimeZoneFromGoogle(now,lat,lon)
        self.assertTrue(testTzId == tzId)

    def testTimeOffset(self):
        destTz = "America/Denver"
        sourceTz = "America/New_York"
        here = datetime.datetime.now()
        there = timezone.translateTime(here,sourceTz,destTz)
        hereTimeStamp = time.mktime(here.timetuple())
        thereTimeStamp = time.mktime(there.timetuple())
        self.assertTrue(hereTimeStamp - thereTimeStamp == 2*60*60)

    def testGetUniversalTimeAtLocation(self):
        now = int(time.time())
        global lat,lon,tzId,delta
        utc = timezone.getUniversalTimeAtLocation(now,
                lat,lon)
        testDelta = int(utc - now) 
        self.assertTrue( testDelta == delta)

    def testGetLocalTimeFromUniversalTime(self):
        utc = timezone.getLocalUtcTimeStamp()
        localtime, tzName = timezone.getLocalTime(utc,tzId)
        now = time.time()
        self.assertTrue(abs(now - localtime) < 2)




if __name__ == "__main__":
     global tzId
     parser = argparse.ArgumentParser(description="Process command line args")
     parser.add_argument("-expected-delta", help = "Expected time difference"
     " between where you run this and UTC time -ve value if you are behind")
     parser.add_argument("-tzId", help = "expected TzId")
     parser.add_argument("-lon", help = "Longitude")
     parser.add_argument("-lat", help = "Latitude")
     args = parser.parse_args()
     tzId = args.tzId
     global lat, lon,delta
     lat = float(args.lat)
     lon = float(args.lon)
     delta = float(args.expected_delta)
     suite = unittest.TestLoader().loadTestsFromTestCase(TimezoneTest)
     unittest.TextTestRunner(verbosity=2).run(suite)

