#!/usr/bin/env python
"""
Extracts interesting URLs from a online source.
"""

import re

import crawl
from src import locality

#LINK_PATTERN = re.compile(r"""<a href="([^"]*)" class="title-adv"\s*>""")
LINK_PATTERN = re.compile(r"""<link>(http://sreality.cz/detail/prodej/byt/[^<]*)</link>""")


def _getPage(pageIndex):
    url = locality.HOME_LIST_URL_TEMPLATE % (pageIndex + 1)
    return crawl.getUrlContent(url)

def _getLinks(baseUrl, page):
    links = LINK_PATTERN.findall(page, re.DOTALL)
    base = baseUrl + "/"
    urls = []
    for link in links:
        if link.startswith("http"):
            urls.append(link)
        else:
            urls.append(base + link)
    return urls

def collectUrls(index):
    baseUrl, rest = locality.HOME_LIST_URL_TEMPLATE.rsplit("/", 1)
    page = _getPage(index)
    return _getLinks(baseUrl, page)

def main():
    urls = collectUrls(0)
    for url in urls:
        print url

if __name__ == "__main__":
    main()

