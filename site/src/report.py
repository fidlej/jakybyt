
import cPickle
import os
import logging

import disk

REPORT_PATH = "data/report.dat"

class Holder:
    def __init__(self):
        self.mtime = 0
        self.analyses = []
CACHE = Holder()


def storeReport(analyses):
    data = cPickle.dumps(analyses, protocol=2)
    disk.storeAtomicData(REPORT_PATH, data)

def fetchReport():
    fp = disk.fetchDataFile(REPORT_PATH)
    return cPickle.load(fp)

def fetchCachedReport():
    if _wasModified():
        CACHE.analyses = tuple(fetchReport())
        logging.info("reloaded %s analyses, pid: %s", len(CACHE.analyses),
                os.getpid())
    return CACHE.analyses

def getMtime():
    return CACHE.mtime

def _wasModified():
    try:
        mtime = os.stat(REPORT_PATH).st_mtime
        if CACHE.mtime < mtime:
            CACHE.mtime = mtime
            return True
        return False
    except (OSError, IOError), e:
        logging.warn("cannot stat the report: %s", e)
        return False


