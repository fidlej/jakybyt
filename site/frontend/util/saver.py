"""
Serves generated pages from disk
or saves them on disk if there are not there.
"""

import os
import time
import logging

import web
import disk

def serve(path, producer, maxAgeSeconds=12*3600):
    """Returns prepared page from disk or from the producer.
    The produced page will remain on the disk.
    """
    data = None
    try:
        if os.path.exists(path) and _getAgeSeconds(path) <= maxAgeSeconds:
            data = file(path).read()
    except (IOError, OSError), e:
        logging.error("Unable to read: %r, reason=%s", path, e)

    if data is None:
        logging.info("Producing: %r", path)
        data = producer()
        disk.storeAtomicData(path, data)

    web.header("Cache-Control", "max-age=%s" % maxAgeSeconds, unique=True)
    if path.endswith(".html"):
        web.header("Content-Type", "text/html; charset=utf-8", unique=True)
    return data

def _getAgeSeconds(path):
    mtime = os.stat(path).st_mtime
    return time.time() - mtime

