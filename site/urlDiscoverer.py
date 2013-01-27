#!/usr/bin/env python
"""
Stores newly discovered URLs into storage.
"""

import time
import logging

from src import urlCollector
from src import storage, tobe, disk, config

def main():
    disk.getFileLockOrDie("locks/backend.pid")
    num_found = 0
    for index in xrange(10**6):
        wasNew = False
        urls = urlCollector.collectUrls(index)
        num_found += len(urls)
        for url in urls:
            if not storage.isDiscovered(url):
                wasNew = True
                logging.info("Discovered new url: %s", url)
                storage.storeUrl(url)
                tobe.toDownload(url)
        if not wasNew:
            break

    if num_found == 0:
        logging.error("No valid URL discovered")

if __name__ == "__main__":
    config.setLogging()
    main()

