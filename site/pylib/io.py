
import os
import errno
import time
import logging

FILENAME_TEMPLATE = "%s-%s.log"
TIMESTAMP_FORMAT = "%Y%m%d-%H%M-%S"

def createUniqueFile(prefix, filenameTemplate=FILENAME_TEMPLATE):
    """ Creates uniquely named file.
    Tries until the name is really unique.
    Return the created opened file.
    """
    while True:
        filename = _getUniqueName(prefix, filenameTemplate)
        ensureDirs(filename)

        try:
            fd = os.open(filename, os.O_WRONLY|os.O_CREAT|os.O_EXCL)
            return os.fdopen(fd, "w")
        except OSError, e:
            if e.errno == errno.EEXIST:
                logging.warn("file exists: %r", filename)
                time.sleep(0.1)
                continue
            raise

def _getUniqueName(prefix, filenameTemplate=FILENAME_TEMPLATE):
    now = time.time()
    timestamp = time.strftime(TIMESTAMP_FORMAT, time.localtime(now))
    timestamp += "%03d" % (long(now * 1000) % 1000)
    return filenameTemplate % (prefix, timestamp)

def ensureDirs(filename):
    head, tail = os.path.split(filename)
    try:
        os.makedirs(head)
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise

