
import time
import simplejson

from util import examiner

#AVGS_FILENAME = "data/avgs.txt"
AVGS_FILENAME = "../../collected/exports/day_avgs.txt"


def getGroupCounts(analyses):
    groupMap = examiner.groupByRooms(analyses)
    keys = groupMap.keys()
    keys.sort()
    groupCounts = []
    for key in keys:
        groupCounts.append((key, len(groupMap[key])))

    return groupCounts

def getHistogramDataJs(analyses, property, unit, legend="", minMax=None):
    #TODO: calc the histogram values in the middle of the intervals
    if minMax is None:
        minValue, maxValue = examiner.getMinMax(analyses, property, unit)
    else:
        minValue, maxValue = minMax

    values = [v for v in xrange(minValue, maxValue + 1, unit)]
    values = ["%.1f M" % (float(v) / 10**6) for v in values]
    rows = [[v, 0, 0] for v in values]
    counts = examiner.calcHistogram(
            analyses, property, minValue, maxValue, unit)
    for rowId, value in enumerate(counts):
        if rowId % 10 == 0:
            rows[rowId][2] = value
        else:
            rows[rowId][1] = value

    cols = (
            ("string", property),
            ("number", ""),
            ("number", legend),
            )
    return _prepareDataJs(cols, rows), max(counts)

def getTimeAvgsDataJs(showCounts=False):
    """ Provides timeline data.
    Returns JS data and counts for the last smooth unit.
    """
    #whatToDisplay = examiner.UNIT_PRICE_INDEX
    whatToDisplay = examiner.PRICE_INDEX
    if showCounts:
        whatToDisplay = examiner.COUNT_INDEX
    valueIndex = whatToDisplay + 1
    displayPrefixes = ("1+", "2+", "3+")
    #TODO: report just weekly values to make it sorter
    SMOOTHING = 7

    avgs = _parseExportedAvgs(AVGS_FILENAME)

    # the first row is just a filler
    rows = [[0] * (1 + len(displayPrefixes))]
    rowsRoomCounts = []
    lastTimestamp = None
    for timestamp, group in avgs:
        if timestamp != lastTimestamp:
            lastTimestamp = timestamp
            if whatToDisplay == examiner.COUNT_INDEX:
                rows.append([timestamp] + [0] * len(displayPrefixes))
            else:
                # the previous avgs serve as defaults
                rows.append([timestamp] + rows[-1][1:])
            rowsRoomCounts.append([0] * len(displayPrefixes))

        rooms = group[0]
        for i, prefix in enumerate(displayPrefixes):
            if rooms.startswith(prefix):
                rowsRoomCounts[-1][i] = group[1 + examiner.COUNT_INDEX]
                rows[-1][1 + i] = group[valueIndex]
                # counts are displayed as for the SMOOTHING period
                if whatToDisplay == examiner.COUNT_INDEX:
                    rows[-1][1 + i] *= SMOOTHING
                break

    # remove the bogus first row
    rows = rows[1:]
    if whatToDisplay == examiner.COUNT_INDEX:
        rows = _smoothTimeLine(rows, SMOOTHING, None)
    else:
        rows = _smoothTimeLine(rows, SMOOTHING, rowsRoomCounts)

    # sums counts in the last rows
    rowsRoomCounts = rowsRoomCounts[-SMOOTHING:]
    lastCounts = [0] * len(displayPrefixes)
    for i in range(len(lastCounts)):
        lastCounts[i] = sum(roomCounts[i] for roomCounts in rowsRoomCounts)

    cols = [("date", _(u"Date"))]
    cols += [("number", "") for key in displayPrefixes]
    return _prepareDataJs(cols, rows), lastCounts


def _smoothTimeLine(rows, packSize, rowsRoomCounts=None, aggregateSize=2):
    """ Smooths timeline data.
    Returns list of rows with packSize rows smoothed together.
    Params:
        rows ... data rows
            The first column is the timestamp.
            The other columns are the values.
        packSize ... num of rows to pack together
        rowsRoomCounts ... weights of different columns in the rows
    """
    if len(rows) == 0:
        return []

    if rowsRoomCounts is None:
        numRoomCols = len(rows[0]) - 1
        rowsRoomCounts = [[1] * numRoomCols] * len(rows)

    packedRows = []
    for i in xrange(0, len(rows), aggregateSize):
        packRows = rows[i:i+packSize]
        packRoomCounts = rowsRoomCounts[i:i+packSize]

        avgRow = _calcAvgRow(packRows, packRoomCounts)
        packedRows.append(avgRow)

    return packedRows

def _calcAvgRow(rows, rowsRoomCounts):
    """ Averages the rows together.
    Calculates weighted average with rowsRoomCounts serving as the weights.
    Returns [avgTimestamp, avgCol1, avgCol2, ...]
    """
    firstRow = rows[0]
    avgRow = [0] * len(firstRow)

    for c in range(len(firstRow)):
        num = 0
        for row, roomCounts in zip(rows, rowsRoomCounts):
            if c == 0:
                count = 1
            else:
                count = roomCounts[c - 1]
            avgRow[c] += row[c] * count
            num += count
        avgRow[c] //= max(1, num)

    return avgRow

def _parseExportedAvgs(filename):
    """ Exports:
    timestamp, (rooms, count, avgPrice, avgUnitPrice, avgArea)
    """
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    DATE_FORMAT = "%Y-%m-%d"
    items = []
    for line in file(filename):
        line = line.strip()
        if len(line) == 0 or line.startswith("#"):
            continue
        dateStr, rest = line.split(",",1)
        format = DATETIME_FORMAT
        if len(dateStr) == 10:
            format = DATE_FORMAT

        timestamp = time.mktime(time.strptime(dateStr, format))
        timestamp = int(timestamp)
        group = simplejson.loads("[%s]" % rest)
        items.append((timestamp, group))
    return items

def _prepareDataJs(cols, rows):
    return simplejson.dumps(locals(), separators=(',', ':'))

