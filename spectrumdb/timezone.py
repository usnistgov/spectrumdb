import os
import pytz
import datetime
import calendar
import time
import json
import argparse
import sys
import httplib
import traceback
from dateutil import tz
from datetime import timedelta

timeZoneMap = {}

SECONDS_PER_DAY = 24 * 60 * 60

"""
Time conversion routines to go from local to univesal time and vice versa.
You need a Google API key for the timezone API (this is free). You can get it
from your API console.
"""


def parseTime(timeString, timeZone):
    """
    Parse a time string given a timezone name and time string.
    """
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

def translateTime(datetime,tzStart,tzTarget):
    return pytz.timezone(tzStart).localize(datetime).astimezone(pytz.timezone(tzTarget))


def is_dst(localTime, zonename):
    """
    Reutrn True if the given time is in the daylight savings time.
    """
    tz = pytz.timezone(zonename)
    now = pytz.utc.localize(datetime.datetime.fromtimestamp(localTime))
    return now.astimezone(tz).dst() != timedelta(0)


def getDateTimeFromLocalTimeStamp(ts):
    """
    Get a datetime structure from a timestamp.
    """
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
    Short format timestamp only year month and day timestamp.
    """
    dt = datetime.datetime.fromtimestamp(float(timeStamp))
    return dt.strftime('%Y-%m-%d')

def getApiKey():
    """
    Get the google timezone API key. This should be setup
    in your environment as an environment variable.
    """
    return os.environ.get("GOOGLE_TIMEZONE_API_KEY")


def formatTimeStampLong(timeStamp, timeZoneName):
    """
    format timestamp given a timezone name and a timestamp.
    """
    localTimeStamp, tzName = getLocalTime(timeStamp, timeZoneName)
    dt = datetime.datetime.fromtimestamp(float(localTimeStamp))
    return str(dt) + " " + tzName


def getLocalTimeZoneFromGoogle(time, lat, lon):
    """
    Get the timezone ID and timezone name from google
    given a timestamp and lat lon 
    """
    key = str(lat) + "/" + str(lon)
    if key in timeZoneMap:
        jsonData = timeZoneMap[key]
        return (jsonData["timeZoneId"], jsonData["timeZoneName"])
    try:
        conn = httplib.HTTPSConnection("maps.googleapis.com")
        conn.request("POST", "/maps/api/timezone/json?location=" +
                     str(lat) + "," + str(lon) + "&timestamp=" +
                     str(time) + "&sensor=false&key=" + getApiKey(), "",
                     {"Content-Length":0})
        res = conn.getresponse()
        if res.status == 200:
            data = res.read()
            jsonData = json.loads(data)
            if "errorMessage" not in jsonData and jsonData["status"] == "OK" :
                timeZoneMap[key] = jsonData
                return (jsonData["timeZoneId"], jsonData["timeZoneName"])
            else:
                print "google returned " , json.dumps(jsonData, indent = 4)
                raise Exception("Error communicating with google")
        else:
            print "Status ", res.status, res.reason
            raise Exception("Error communicating with google: " + res.reason)
    except:
        traceback.print_exc()
        print sys.exc_info()[0]
        raise



def getTimeOffsetFromGoogle(time,lat, lon):
    """"
    Get the timeoffset from a local timestamp and time coordinates given by lat
    and lon.
    """
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
            if "errorMessage" not in jsonData and jsonData["status"] == "OK":
                offset = jsonData["rawOffset"] + jsonData["dstOffset"]
                return offset
            else:
                raise Exception("Error communicating with google")
        else:
            raise Exception("Error communicating with google")
    except:
        traceback.print_exc()
        print sys.exc_info()[0]
        raise


def getLocalUtcTimeStamp():
    """
    Get the universal timestamp for this machine.
    """
    t = time.mktime(time.gmtime())
    isDst = time.localtime().tm_isdst
    return t - isDst * 60 * 60

def getUniversalTimeAtLocation(timestamp,lat,lon):
    """
    Get the universal time given a local unix timestamp and lat,lon coordinates
    where the time was measured.
    """
    offset = getTimeOffsetFromGoogle(timestamp,lat,lon)
    return timestamp - offset



