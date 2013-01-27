#!/usr/bin/env python

import time
import simplejson

from src import report, examiner, disk, AntiFraud

EXPORT_AVGS_PATH = "exports/avgs.txt"
EXPORT_DAY_AVGS_PATH = "exports/day_avgs.txt"

def _exportData(data, path):
    disk.preparePath(path)
    output = file(path, "a")
    output.write(data)
    output.close()

def _serializeAvgs(dateStr, groups):
    lines = []
    keys = groups.keys()
    keys.sort()

    for key in keys:
        group = groups[key]
        line = dateStr
        line += "," + simplejson.dumps(key)
        for value in group:
            line += "," + str(value)

        lines.append(line)

    return "\n".join(lines) + "\n"

def _exportAvgs(dateStr, analyses, path):
    groups = examiner.calcGroupAvgs(analyses)
    data = _serializeAvgs(dateStr, groups)
    _exportData(data, path)
    return data

def exportAll(analyses):
    """ Export avgs over all analyses.
    """
    dateStr = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    _exportAvgs(dateStr, analyses, EXPORT_AVGS_PATH)

def exportLastDay(analyses):
    """ Export avgs only from the last whole day.
    """
    timestamp = time.time() - 24*3600
    dateStr = time.strftime("%Y-%m-%d", time.gmtime(timestamp))
    analyses = [a for a in analyses if a["createdDate"] == dateStr]
    data = _exportAvgs(dateStr, analyses, EXPORT_DAY_AVGS_PATH)
    print "exported:\n" + data

def main():
    analyses = report.fetchReport()
    exportAll(analyses)
    analyses = AntiFraud.getWithoutDuplicities(analyses)
    exportLastDay(analyses)

if __name__ == "__main__":
    main()

