
import time

from util import examiner

MIN_GROUP_SIZE = 10

def getTimeline(analyses):
    """ Returns:
    [
        (timePoint, [
                [groupName, count, avgPrice, avgUnitPrice, avgArea],
                [groupName, count, avgPrice, avgUnitPrice, avgArea],
                ...
            ]
        ),
        ...
    ]
    """
    timeline = []
    year = time.localtime().tm_year
    rows = []

    # only significant group are displayed
    minGroupSize = min(MIN_GROUP_SIZE, len(analyses) // 100)
    avgs = examiner.calcGroupAvgs(analyses)
    keys = avgs.keys()
    keys.sort()
    for key in keys:
        if avgs[key][0] < minGroupSize:
            continue
        row = [key]
        row += avgs[key]
        rows.append(row)

    timeline.append((year, rows))
    return timeline

