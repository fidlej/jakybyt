#!/usr/bin/env python
# coding: utf-8
import logging
from src import localgeocoder

address = u"Högerova 11, 15200, Praha 5, Czech Republic"
address = u"Štětínská, Praha 8 - Bohnice, 181 00"
address = u"Nad Malovankou, Praha 6, 169 00"
address = u"Hnězdenská, 18100, Praha 4"
#address = u"Hnězdenská 767/4, 18100, Praha 8"
#address = u"Hnězdenská, Praha 8, 181 00"
address = u"Zlešická, 14900, Praha 4, Praha, Czech Republic"

def main():
    logging.root.setLevel(logging.DEBUG)

    resolver = localgeocoder.GeoResolver()
    resolver.cache = {}
    result = resolver.getGeoPointAndLocality(address)
    print "result:", result

    #resolver.close()

main()
