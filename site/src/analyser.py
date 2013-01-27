#!/usr/bin/env python
# coding: utf-8

import sys
import logging
import re
import time

from src import storage

#TODO: support "EUR za ..."
PRICE_TYPE = ur"(\d*(?: \d*)*)\s*(?:,-)?\s*Kč"

TITLE_PATTERN = re.compile(ur"""<h2 class="fn">([^<]*)</h2>""")
PRICE_PATTERN = re.compile(ur"""<span class="price">\s*%s\s*""" % PRICE_TYPE)
#TODO: get a unit price example
UNIT_PRICE_PATTERN = re.compile(ur"""<span class="price">\s*%s\s*za m<sup>2</sup>""" % PRICE_TYPE)
AREA_PATTERN = re.compile(ur"""<h2 class="fn">Prodej, byt (?:[^,]*), (\d*) m²""")
ROOMS_PATTERN = re.compile(ur"""<h2 class="fn">Prodej, byt ([^,]*),""")
FLOOR_PATTERN = re.compile(ur"""<strong>Podlaží umístění:</strong></span>\s*<span>(\d*)\.\s*podlaží""")
CREATED_DATE_PATTERN = re.compile(ur"""<span class="id">(\d{2}\.\d{2}\.\d{4})</span>""")
ADDRESS_PATTERN = re.compile(ur"""<strong>Adresa:</strong></span>\s*<span class="address">\s*<span class="street-address">([^<]*)</span>(,[^<]*)(?:<span class="locality">([^<]*)</span>)?""")
BUILD_PATTERN = re.compile(ur"""<strong>Budova:</strong></span>\s*<span>([^<]*)</span>""")

def _findFirst(pattern, content, converter=None):
    value = None
    match = pattern.search(content, re.DOTALL)
    if match:
        value = ''.join(match.groups(''))
        if converter is not None:
            value = converter(value)
    return value

def normalizeDate(value):
    day, month, year = value.split('.')
    return "%d-%02d-%02d" % (int(year), int(month), int(day))

def normalizePrice(value):
    return int(value.replace(" ", "").replace("&nbsp;", ""))

def stripExtraSpaces(value):
    value = value.strip()
    return " ".join(value.split())

def _analyse(content):
    analysis = {
            "title": _findFirst(TITLE_PATTERN, content, stripExtraSpaces),
            "price": _findFirst(PRICE_PATTERN, content, normalizePrice),
            "unitPrice": _findFirst(UNIT_PRICE_PATTERN, content, normalizePrice),
            "area": _findFirst(AREA_PATTERN, content, int),
            "rooms": _findFirst(ROOMS_PATTERN, content, stripExtraSpaces),
            "floor": _findFirst(FLOOR_PATTERN, content, int),
            "address": _findFirst(ADDRESS_PATTERN, content, stripExtraSpaces),
            "b": _findFirst(BUILD_PATTERN, content, stripExtraSpaces),
            "createdDate": _findFirst(CREATED_DATE_PATTERN, content, normalizeDate),
    }
    if analysis["createdDate"] is None:
        analysis["createdDate"] = time.strftime("%Y-%m-%d")
    return analysis

def analyseUrl(url):
    content = storage.fetchContent(url)
    analysis = _analyse(content)
    return analysis

def main():
    for url in sys.argv[1:]:
        print analyseUrl(url)

if __name__ == "__main__":
    logging.root.setLevel(logging.DEBUG)
    main()

