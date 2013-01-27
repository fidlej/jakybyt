#!/usr/bin/env python

import logging
import time
import optparse
import urllib2

from src import storage, tobe, disk, crawl, config

def parseArgs():
    parser = optparse.OptionParser()
    parser.add_option("-f", "--fix", action="store_true",
            help="Download of all not yet downloaded.")
    return parser.parse_args()


def _try_download(url, n_tries=3):
    """Returns the URL content or None.
    """
    for attempt_index in xrange(n_tries):
        try:
            return crawl.getUrlContent(url)
        except urllib2.HTTPError, e:
            if 400 <= e.code < 600:
                logging.info("Skipping wrong URL %s: %s", url, e)
                return None
            else:
                raise
        except urllib2.URLError, e:
            logging.warn("Download error on %s (attempt %s/%s): %s", url,
                    attempt_index + 1, n_tries, e)
            time.sleep(2**attempt_index)
    return None


def main():
    disk.getFileLockOrDie("locks/backend.pid")

    options, args = parseArgs()
    if options.fix:
        urls = [url for url in storage.getUrls() if not storage.isDownloaded(url)]
    else:
        urls = tobe.getToBeDownloaded()

    logging.info("Downloading %s urls", len(urls))
    for url in urls:
        content = _try_download(url)
        if content is not None:
            storage.storeContent(url, content)
            tobe.toAnalyse(url)

    tobe.nothingToBeDownloaded()
    logging.info("Downloaded %s urls", len(urls))

if __name__ == "__main__":
    config.setLogging()
    main()
