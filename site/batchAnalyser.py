#!/usr/bin/env python

import logging
import optparse

from src import storage, analyser, tobe, disk, reportProducer, config
from src import warmer, report

def parseArgs():
    parser = optparse.OptionParser()
    parser.add_option("-f", "--fix", action="store_true",
            help="Force re-analysis of all.")
    parser.add_option("-c", "--clean", action="store_true",
            help="Don't use existing report.dat and analyses.")
    return parser.parse_args()

def updateReport(cleanStart=False):
    toReportUrls = tobe.getToBeReported()
    reportProducer.produceReport(toReportUrls, cleanStart)
    tobe.nothingToBeReported()

def _skipAnalysed(downloadedUrls):
    urls = []
    for url in downloadedUrls:
        if storage.isAnalysed(url):
            tobe.toReport(url)
        else:
            urls.append(url)
    return urls

def main():
    disk.getFileLockOrDie("locks/backend.pid")
    options, args = parseArgs()
    if options.fix:
        urls = [url for url in storage.getUrls() if storage.isDownloaded(url)]
        tobe.nothingToBeReported()
        if not options.clean:
            urls = _skipAnalysed(urls)
    else:
        urls = tobe.getToBeAnalysed()

    for url in urls:
        analysis = analyser.analyseUrl(url)
        storage.storeAnalysis(url, analysis)
        tobe.toReport(url)
    tobe.nothingToBeAnalysed()
    logging.info("Analysed %s urls", len(urls))

    cleanStart = options.fix or options.clean
    updateReport(cleanStart)
    warmer.updateWarmPicture()

if __name__ == "__main__":
    config.setLogging()
    main()
