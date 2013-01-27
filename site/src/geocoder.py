#!/usr/bin/env python
# coding: utf-8

import sys
import logging
import time
import simplejson

from pylib import htmlSource
from src import config

GEO_URL = "http://maps.google.com/maps/geo?key=" + config.MAP_KEY

G_GEO_SUCESS = 200
G_GEO_MISSING_QUERY = 601
G_GEO_UNKNOQN_ADDRESS = 602
G_GEO_UNAVAILABLE_ADDRESS = 603
CACHEABLE_CODES = (
        G_GEO_SUCESS,
        G_GEO_MISSING_QUERY,
        G_GEO_UNKNOQN_ADDRESS,
        G_GEO_UNAVAILABLE_ADDRESS,
        )

def _getGeoResponse(query, format="csv", options={}):
    options["q"] = query
    options["output"] = format
    return htmlSource.getUrlContent(GEO_URL, options)

def _getCodeAndPlacemark(query, options={}):
    """ Returns found (latitude, longitude) or None.
    """
    response = _getGeoResponse(query, format="json", options=options)
    response = simplejson.loads(response)

    code = response["Status"]["code"]
    placemark = None
    if code == G_GEO_SUCESS:
        placemark = response["Placemark"][0]
    return code, placemark

def getPlacemark(query, options={}):
    """ Returns found (latitude, longitude) or None.
    """
    code, placemark = _getCodeAndPlacemark(query, options=options)
    return placemark

class DelayedGeoCoder:
    def __init__(self, options={}):
        self.options = options

    def getPlacemark(self, address):
        # let the google to survive
        time.sleep(0.2)
        code, placemark = _getCodeAndPlacemark(address, options=self.options)
        if code not in CACHEABLE_CODES:
            raise ValueError("Got error response: %s: %s", address, code)

        logging.info("Found new geo: %s: %s", address, placemark)
        return placemark

def main():
    # Example with two addresses: "Ujezd, 11800"
    address = ' '.join(sys.argv[1:])
    response = _getGeoResponse(address, "json")
    print response

    code, placemark = _getCodeAndPlacemark(address)
    print code, placemark

    from src import localgeocoder
    print localgeocoder._getRawLocalityName(placemark["AddressDetails"]["Country"])

if __name__ == "__main__":
    logging.root.setLevel(logging.DEBUG)
    main()

