
import os
import sys
import fcntl
import errno
import gzip
import logging

def preparePath(path):
    head, tail = os.path.split(path)
    if len(head) == 0:
        return
    try:
        os.makedirs(head)
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise

def storeAtomicData(path, data):
    preparePath(path)
    tmpPath = path + ".tmp"
    if path.endswith(".gz"):
        output = gzip.GzipFile(tmpPath, "wb")
    else:
        output = file(tmpPath, "wb")
    output.write(data)
    output.flush()
    os.fsync(output.fileno())
    output.close()
    os.rename(tmpPath, path)

def fetchDataFile(path):
    if path.endswith(".gz"):
        output = gzip.GzipFile(path)
    else:
        output = file(path)
    return output

def rmDirectory(path):
    """ Removes one directory and its files.
    Does not go deeper, to prevent big harm on misuse.
    """
    if not os.path.exists(path):
        return
    logging.info("removing all under: %s", path)
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        # the dirs are not deleted, there should be none
    os.rmdir(path)

def getFileLockOrDie(lockfile):
    """ Locks the file or dies.
    Returns file descriptor for the lock file.
    Call os.close(fd) on it when the lock is not needed anymore.
    """
    try:
        # os.open is used to prevent truncation
        fd = os.open(lockfile, os.O_WRONLY| os.O_CREAT)
        try:
            fcntl.lockf(fd, fcntl.LOCK_NB|fcntl.LOCK_EX)
            os.write(fd, "%d\n" % os.getpid())
            os.fsync(fd)
            return fd
        except IOError, e:
            if e.errno in (errno.EACCES, errno.EAGAIN):
                logging.error("File is locked: '%s'" % lockfile)
                sys.exit(1)
            raise
    except IOError, e:
        logging.error("IO error on: '%s': %s" % (lockfile, e.stderror))
        sys.exit(2)

