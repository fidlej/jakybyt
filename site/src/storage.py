
import os
import simplejson
import time

from src import disk

STORAGE_PATH = "storage"
CONTENT_BASENAME = "content.html.gz"
ANALYSIS_BASENAME = "analysis.json"
URL_BASENAME = "url.txt"

STATUS_BASENAME_TEMPLATE = "status-%s"
MAX_DOC_TAIL = 30

def _getDocId(url):
    lastSlash = url.rfind("/")
    lastSlash += 1
    lastSlash = max(lastSlash, len(url) - MAX_DOC_TAIL)
    return str(abs(hash(url))) + "-" + url[lastSlash:]

def _getStoragePath(url, basename):
    docId = _getDocId(url)
    return os.path.join(STORAGE_PATH, docId, basename)

def _storeData(url, basename, data):
    path = _getStoragePath(url, basename)
    disk.storeAtomicData(path, data)

def _fetchDataFile(url, basename):
    path = _getStoragePath(url, basename)
    return disk.fetchDataFile(path)

def storeContent(url, page):
    _storeData(url, CONTENT_BASENAME, page.encode("utf-8"))
    _storeStatus(url, "DOWNLOADED")

def fetchContent(url):
    data = _fetchDataFile(url, CONTENT_BASENAME).read()
    return unicode(data, "utf-8")

def storeAnalysis(url, analysis):
    json = simplejson.dumps(analysis, indent=4, separators=(",", ": "))
    _storeData(url, ANALYSIS_BASENAME, json)
    _storeStatus(url, "ANALYSED")

def fetchAnalysis(url):
    fileobj = _fetchDataFile(url, ANALYSIS_BASENAME)
    return simplejson.load(fileobj)

def storeUrl(url):
    _storeData(url, URL_BASENAME, url)
    _storeStatus(url, "DISCOVERED")

def purge(url):
    path = _getStoragePath(url, '')
    disk.rmDirectory(path)

def _storeStatus(url, status):
    basename = STATUS_BASENAME_TEMPLATE % status
    timestamp = str(int(time.time()))
    _storeData(url, basename, timestamp)

def isDiscovered(url):
    return _isWithStatus(url, "DISCOVERED")

def isDownloaded(url):
    return _isWithStatus(url, "DOWNLOADED")

def isAnalysed(url):
    return _isWithStatus(url, "ANALYSED")

def _isWithStatus(url, status):
    basename = STATUS_BASENAME_TEMPLATE % status
    return os.path.exists(_getStoragePath(url, basename))

def getUrls():
    urls = []
    for entry in os.listdir(STORAGE_PATH):
        path = os.path.join(STORAGE_PATH, entry, URL_BASENAME)
        if os.path.exists(path):
            fp = disk.fetchDataFile(path)
            urls.append(fp.read())
    return urls

