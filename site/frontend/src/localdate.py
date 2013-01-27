"""
The localdate module provides functions
to get human readable local date from a configured time zone.

No local times should be used for arithmetic.
"""

import os
import time
import datetime
import pytz


def changeTz(timezone):
    """ Changes local timezone.
    This setting is a global one,
    because mktime() does not take a TZ parameter.
    """
    global TZ
    TZ = TZ = pytz.timezone(timezone)
    os.environ['TZ'] = timezone
    time.tzset()

DATE_FORMAT = "%Y-%m-%d"
TIME_ZONE = "Europe/Prague"
changeTz(TIME_ZONE)


def now():
    return time.time()

def beforeDays(days):
    """ Returns timestamp before given number of days.
    """
    # unix day is always 86400 seconds long
    return now() - days*24*3600

def strDate(timestamp=None):
    """ Returns "year-month-day" from the configured timezone.
    """
    if timestamp is None:
        timestamp = now()
    return time.strftime(DATE_FORMAT, _localtuple(timestamp))

def parseDate(strDate):
    """ Returns timestamp from given "year-month-day" local date.
    """
    year, month, day = [int(x) for x in strDate.split("-", 3)]
    dt = datetime.date(year, month, day)
    t = dt.timetuple()
    return time.mktime(t)

def calcAgeDays(dateStr, nowTimestamp=None):
    """ Returns number of days between given "year-month-day" local date
    and the nowTimestamp.
    """
    if nowTimestamp is None:
        nowTimestamp = now()
    timestamp = parseDate(dateStr)
    return int(max(0, nowTimestamp - timestamp)) // (24*3600)

def _localtuple(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp, TZ)
    return dt.timetuple()

