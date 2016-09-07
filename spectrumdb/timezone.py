import os
import pytz
import datetime
import calendar
import time
import json
import argparse
import sys
import httplib
from dateutil import tz
from datetime import timedelta

SECONDS_PER_DAY = 24 * 60 * 60


def parseTime(timeString, timeZone):
    ts = time.mktime(time.strptime(timeString, '%Y-%m-%d %H:%M:%S'))
    (localTime, tzName) = getLocalTime(ts, timeZone)
    return localTime


def getLocalTime(utcTime, timeZone):
    """
    get the local time from a utc timestamp given the timezone
    """
    to_zone = tz.gettz(timeZone)
    utc = datetime.datetime.utcfromtimestamp(utcTime)
    from_zone = tz.gettz('UTC')
    utc = utc.replace(tzinfo=from_zone)
    todatetime = utc.astimezone(to_zone)
    localTime = calendar.timegm(todatetime.timetuple())
    return (localTime, todatetime.tzname())


def is_dst(localTime, zonename):
    tz = pytz.timezone(zonename)
    now = pytz.utc.localize(datetime.datetime.fromtimestamp(localTime))
    return now.astimezone(tz).dst() != timedelta(0)


def getDateTimeFromLocalTimeStamp(ts):
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return st


def getDayBoundaryTimeStampFromUtcTimeStamp(timeStamp, timeZoneId):
    """
    get to the day boundary given a local time in the UTC timeZone.
    ts is the local timestamp in the UTC timeZone i.e. what you would
    get from time.time() on your computer + the offset betwen your
    timezone and UTC.
    """
    (ts, tzName) = getLocalTime(timeStamp, timeZoneId)
    timeDiff = timeStamp - ts
    dt = datetime.datetime.fromtimestamp(float(ts))
    dt1 = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    #isDst = is_dst(ts, timeZoneId)
    dbts = time.mktime(dt1.timetuple())
    return dbts + timeDiff


def formatTimeStamp(timeStamp):
    """
    only year month and day timestamp.
    """
    dt = datetime.datetime.fromtimestamp(float(timeStamp))
    return dt.strftime('%Y-%m-%d')

def getApiKey():
    return os.environ.get("GOOGLE_TIMEZONE_API_KEY")


def formatTimeStampLong(timeStamp, timeZoneName):
    """
    lon format timestamp.
    """
    localTimeStamp, tzName = getLocalTime(timeStamp, timeZoneName)
    dt = datetime.datetime.fromtimestamp(float(localTimeStamp))
    return str(dt) + " " + tzName


def getLocalTimeZoneFromGoogle(time, lat, lon):
    try:
        conn = httplib.HTTPSConnection("maps.googleapis.com")
        conn.request("POST", "/maps/api/timezone/json?location=" +
                     str(lat) + "," + str(lon) + "&timestamp=" +
                     str(time) + "&sensor=false&key=" + getApiKey(), "",
                     {"Content-Length":0})
        res = conn.getresponse()
        if res.status == 200:
            data = res.read()
            print data
            jsonData = json.loads(data)
            return (jsonData["timeZoneId"], jsonData["timeZoneName"])
        else:
            print "Status ", res.status, res.reason
            return (None, None)
    except:
        print sys.exc_info()[0]
        return (None, None)


def getTimeOffsetFromGoogle(time,lat, lon):
    try:
        API_KEY = getApiKey()
        conn = httplib.HTTPSConnection("maps.googleapis.com")
        conn.request("POST", "/maps/api/timezone/json?location=" +
                     str(lat) + "," + str(lon) + "&timestamp=" +
                     str(time) + "&sensor=false&key=" + API_KEY, "",
                     {"Content-Length":0})
        res = conn.getresponse()
        if res.status == 200:
            data = res.read()
            jsonData = json.loads(data)
            if "errorMessage" not in jsonData:
                offset = jsonData["rawOffset"] + jsonData["dstOffset"]
                return offset
            else:
                raise Exception("Error communicating with google")
        else:
            raise Exception("Error communicating with google")
    except:
        raise


def getLocalUtcTimeStamp():
    t = time.mktime(time.gmtime())
    isDst = time.localtime().tm_isdst
    return t - isDst * 60 * 60



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process command line args')
    parser.add_argument('-t', help='current global time')
    parser.add_argument('-tz', help='time zone')
    args = parser.parse_args()
    print "googleTimeOffset", getTimeOffsetFromGoogle(time.time(),39, -77)

    if args.t is not None:
        t = int(args.t)
    else:
        t = getLocalUtcTimeStamp()

    if args.tz is not None:
        tzId = args.tz
    else:
        tzId = "America/New_York"
    print "-----------------------------------"
    print tzId
    print formatTimeStampLong(t, tzId)
    startOfToday = getDayBoundaryTimeStampFromUtcTimeStamp(t, tzId)
    print "startOfToday", startOfToday
    print "Day Boundary Long Formatted TimeStamp for start of the day", formatTimeStampLong(
        startOfToday, tzId)
    (localtime, tzname) = getLocalTime(startOfToday, tzId)
    delta = startOfToday - localtime
    print "dayBoundaryTimeStamp = ", startOfToday, \
          "getLocalTime(startOfToday,tzId) = ", localtime, " Delta  =  ", delta / 60 / 60, " Hours"
    print "getDayBoundaryTimeStampFromUtcTimeStamp returned ", startOfToday
    print "Computed time ahead of midnight " + str(float(t - startOfToday) /
                                                   float(3600)), " Hours"
    print "Current offset from gmt ", int((parseTime(
          getDateTimeFromLocalTimeStamp(time.time()), "America/New_York") - time.time()) / (60 * 60))
