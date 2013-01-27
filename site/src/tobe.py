
import os

import disk

TO_DOWNLOAD_PATH = "tobe/todownload.txt"
TO_ANALYSE_PATH = "tobe/toanalyse.txt"
TO_REPORT_PATH = "tobe/toreport.txt"

def getToBeDownloaded():
    return _getUrls(TO_DOWNLOAD_PATH)

def getToBeAnalysed():
    return _getUrls(TO_ANALYSE_PATH)

def getToBeReported():
    return _getUrls(TO_REPORT_PATH)

def _getUrls(path):
    if os.path.exists(path):
        return [line.rstrip() for line in file(path)]
    else:
        return []

def toDownload(url):
    _appendLine(TO_DOWNLOAD_PATH, url)

def toAnalyse(url):
    _appendLine(TO_ANALYSE_PATH, url)

def toReport(url):
    _appendLine(TO_REPORT_PATH, url)

def _appendLine(path, data):
    disk.preparePath(path)
    fp = file(path, "a")
    fp.write(data)
    fp.write("\n")
    fp.close()

def nothingToBeDownloaded():
    _unlink(TO_DOWNLOAD_PATH)

def nothingToBeAnalysed():
    _unlink(TO_ANALYSE_PATH)

def nothingToBeReported():
    _unlink(TO_REPORT_PATH)

def _unlink(path):
    if os.path.exists(path):
        os.unlink(path)

