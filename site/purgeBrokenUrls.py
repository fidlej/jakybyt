#!/usr/bin/env python

import logging
import time
import sys
import optparse

from src import urlCollector, config
from src import storage, tobe, disk

def getValidUrls():
    allUrls = set()
    for index in xrange(10**6):
        lastSize = len(allUrls)
        urls = urlCollector.collectUrls(index)
        allUrls.update(urls)
        if len(allUrls) == lastSize:
            return allUrls

def discoverUnknownUrls(urls):
    logging.info("Discovering %s new urls", len(urls))
    for url in urls:
        storage.storeUrl(url)
        tobe.toDownload(url)

def main():
    disk.getFileLockOrDie("locks/backend.pid")
    storedUrlsSet = frozenset(storage.getUrls())
    logging.info("Got %s stored urls", len(storedUrlsSet))

    validUrlsSet = frozenset(getValidUrls())
    if len(validUrlsSet) == 0:
        logging.error("No valid URL found")
        sys.exit(1)

    logging.info("Found %s valid urls", len(validUrlsSet))
    invalidUrlsSet = storedUrlsSet - validUrlsSet
    for url in invalidUrlsSet:
        storage.purge(url)

    discoverUnknownUrls(validUrlsSet - storedUrlsSet)

if __name__ == "__main__":
    config.setLogging()
    main()
