#!/usr/bin/env python

import operator
import time

COUNT_INDEX = 0
PRICE_INDEX = 1
UNIT_PRICE_INDEX = 2
AREA_INDEX = 3

DAY_SECONDS = 24*3600

def groupByRooms(analyses):
    groups = {}
    for analysis in analyses:
        rooms = analysis["rooms"]
        if rooms not in groups:
            groups[rooms] = [analysis]
        else:
            groups[rooms].append(analysis)
    return groups

def getMinMax(analyses, property, unit):
    if len(analyses) == 0:
        return 0, 0
    minValue = min(a[property] for a in analyses)
    minValue -= minValue % unit
    maxValue = max(a[property] for a in analyses)
    maxValue += unit - maxValue % unit
    return minValue, maxValue

def calcHistogram(analyses, property, minValue, maxValue, unit=1):
    """ Calcs value histogram for given min,max range.
    """
    nbars = (maxValue - minValue) // unit + 1
    counts = [0] * nbars
    for analysis in analyses:
        value = analysis[property]
        barIndex = (value - minValue) // unit
        if 0 <= barIndex < len(counts):
            counts[barIndex] += 1
    return counts

def calcGroupAvgs(analyses):
    """ Returns avgs groupes by rooms.
    Format:
    {
        groupName: [count, avgPrice, avgUnitPrice, avgArea],
        ...
    }
    """
    groups = {}
    for analysis in analyses:
        rooms = analysis["rooms"]
        if rooms not in groups:
            # price, unitPrice, area, count
            groups[rooms] = [0, 0, 0, 0]
        group = groups[rooms]
        group[COUNT_INDEX] += 1
        group[PRICE_INDEX] += analysis["price"]
        group[AREA_INDEX] += analysis["area"]
        group[UNIT_PRICE_INDEX] += analysis["unitPrice"]

    for group in groups.itervalues():
        count = group[COUNT_INDEX]
        group[PRICE_INDEX] //= count
        group[AREA_INDEX] //= count
        group[UNIT_PRICE_INDEX] //= count

    return groups

def calcAgeHistogram(analyses):
    ages = [0] * 400
    for analysis in analyses:
        days = _calcDaysBeforeNow(analysis["createdDate"])
        ages[min(days, len(ages) - 1)] += 1
    return ages

def _calcDaysBeforeNow(createdDate):
    timestamp = time.mktime(time.strptime(createdDate, "%Y-%m-%d"))
    now = time.time()
    days = int(now - timestamp) // DAY_SECONDS
    return days

def _showAgeHistogram(analyses):
    ages = calcAgeHistogram(analyses)
    for age, count in enumerate(ages):
        print "%3s: %3s %s" % (age, count, "*" * (count // 10))

def _showRecords(analyses):
    properties = ("createdDate", "unitPrice", "price", "area")
    for property in properties:
        minItem = min(analyses, key=operator.itemgetter(property))
        maxItem = max(analyses, key=operator.itemgetter(property))
        print "%s min: %s" % (property, minItem[property])
        print "%s max: %s" % (property, maxItem[property])

def _showAvgs(analyses):
    groups = calcGroupAvgs(analyses)
    keys = groups.keys()
    keys.sort()

    print "avgs: GROUP [COUNT, PRICE, UNIT_PRICE, AREA]"
    for key in keys:
        group = groups[key]
        print "avgs:", key, group

def main():
    import report
    analyses = report.fetchReport()
    _showAgeHistogram(analyses)
    print
    _showRecords(analyses)
    print
    _showAvgs(analyses)
    if len(analyses) > 0:
        print
        print "newest: ", analyses[0]

if __name__ == "__main__":
    import sys, codecs, locale
    sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
    main()
