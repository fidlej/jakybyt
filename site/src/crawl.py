
CRAWL_DELAY_SECONDS = 2
HEADERS = {
        "User-Agent": "Mozilla/5.0 (compatible; RssReader/2.2; http://jakybyt.cz/info)",
        }

import time

from pylib import htmlSource

def getUrlContent(url):
    time.sleep(CRAWL_DELAY_SECONDS)
    return htmlSource.getUrlContent(url, headers=HEADERS)

