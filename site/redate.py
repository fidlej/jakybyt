#!/usr/bin/env python
"""
Changes hashes inside the real_dates.dat
"""

import cPickle
import logging

from src import report, disk, AntiFraud

def getOldHashKey(analysis):
    hashKey = dict(analysis)
    assert "title" not in hashKey
    del hashKey["url"]
    del hashKey["createdDate"]
    del hashKey["locality"]
    return tuple(sorted(hashKey.items()))


def load(path):
    fp = disk.fetchDataFile(path)
    map = cPickle.load(fp)
    fp.close()
    return map

def save(map, path):
    data = cPickle.dumps(map, protocol=2)
    disk.storeAtomicData(path, data)

def main():
    disk.getFileLockOrDie("locks/backend.pid")

    newMap = {}
    oldMap = load(AntiFraud.REAL_DATES_PATH)
    analyses = report.fetchReport()
    for analysis in analyses:
        oldHashKey = getOldHashKey(analysis)
        newHashKey = AntiFraud._getHashKey(analysis)
        createdDate = oldMap.get(oldHashKey)
        if createdDate is not None:
            olderDate = min(newMap.get(newHashKey, "3000"), createdDate)
            newMap[newHashKey] = olderDate
            logging.debug("Found date %s for %s", olderDate, newHashKey)

    if len(newMap) == 0:
        raise Exception("No dates found.")
    save(newMap, AntiFraud.REAL_DATES_PATH)

if __name__ == "__main__":
    logging.root.setLevel(logging.DEBUG)
    main()

