# coding: utf-8
"""
Geocoder for locality street addresses.
"""

import re
import logging
import optparse
import operator

import geocoder
import gis
from src import locality, PersistentMap

from pylib import textUtils

REPLACES = (
        (u"Kpt.", u"Kapitána"),
        (u"nám.", u"náměstí"),
        (u"Nám.", u"Náměstí"),
        (u"Dr.", u"Doktora"),
        (u"dr.", u"doktora"),
        )

LOCALITY_REPLACES = (
        (u"Prague", u"Praha"),
        )

GEOCODER_OPTIONS = {
        "gl": "cz",
        "ll": "%s,%s" % locality.CENTRAL_POINT,
        "spn": "%s,%s" % locality.SPAN,
        }
CITY_LEVEL_ACCURACY = 4

PSC_PATTERN = re.compile("(\d+ *\d*)[ .]*$")

DISTRICS = textUtils.deaccent(locality.DISTRICS).lower().replace(" ", "-")
DISTRICS = frozenset(DISTRICS.split(",-"))
assert len(DISTRICS) == locality.N_DISTRICS

NOTHING = (None, None)
KNOWN_GEO_PATH = "data/known_geo.dat"

class GeoResolver:
    def __init__(self):
        self.geoResolver = geocoder.DelayedGeoCoder(GEOCODER_OPTIONS)
        self.cache = PersistentMap.PersistentMap(KNOWN_GEO_PATH)
        self.cache.setLazySave(True)
        self.unsaved_counter = 0

        self.choicesByLength = list(locality.LOCALITY_CHOICES)
        def key(choice):
            return len(choice)
        self.choicesByLength.sort(key=key, reverse=True)
        self.choicePatterns = [re.compile(r"\b%s\b" % a) for a in self.choicesByLength]

    def close(self):
        self.cache.save()

    def getGeoPointAndLocality(self, address):
        address = self._clarifyAddress(address)

        if address in self.cache:
            return self.cache[address]

        result = self._getGeoPointAndLocality(address)
        self.cache[address] = result
        self.unsaved_counter += 1
        if self.unsaved_counter >= 100:
            self.unsaved_counter = 0
            self.cache.save()
        return result

    def _getGeoPointAndLocality(self, address):
        placemark = self.geoResolver.getPlacemark(address)
        if placemark is None:
            return NOTHING

        if not _isLocalPlacemark(address, placemark):
            return NOTHING

        coordinates = placemark["Point"]["coordinates"]
        point = coordinates[1], coordinates[0]

        country = placemark["AddressDetails"]["Country"]
        localityName = _getLocalityName(country)
        return point, localityName

    def _clarifyAddress(self, origAddress):
        psc = self._getPsc(origAddress)
        address = origAddress.split(",", 1)[0]
        address = _apply_replaces(address, REPLACES)
        if psc is not None:
            address += ", %s" % psc

        for pattern, choice in zip(self.choicePatterns, self.choicesByLength):
            if pattern.search(origAddress):
                #choice = _apply_replaces(choice, LOCALITY_REPLACES, reverse=True)
                address += ", " + choice
                break

        address += locality.ADDRESS_SUFFIX
        return address

    def isLocal(self, url):
        url = url.rsplit("/", 2)[-2]
        for name in DISTRICS:
            if name in url:
                return True

        return False

    def _getPsc(self, address):
        """ Extracts PSC from address.
        Returns numeric PSC or None.
        """
        try:
            match = PSC_PATTERN.search(address)
            if not match:
                return None

            psc = match.group(1)
            psc = psc.replace(" ", "")
            if len(psc) < 5:
                psc += "00"
            psc = int(psc)
            if psc not in locality.PSC_SET:
                return None
            return psc
        except ValueError:
            return None


def _isLocalPlacemark(address, placemark):
    """Ensures that propor AdministrativeAreaName or LocalityName is present.
    """
    addressDetails = placemark.get("AddressDetails")
    if addressDetails is None:
        return False

    if addressDetails.get("Accuracy", -1) <= CITY_LEVEL_ACCURACY:
        return False

    country = addressDetails.get("Country")
    if country is None:
        logging.debug("Geo: missing country: %s", address)
        return False

    area = country.get("AdministrativeArea")
    if area:
        areaName = area.get("AdministrativeAreaName")
        if areaName not in locality.AREA_NAMES:
            logging.info("Geo: bad area name: %r, %s", areaName, address)
            return False
    else:
        loc = country.get("Locality")
        if loc is None:
            logging.debug("Geo: missing locality: %s", address)
            return False

        localityName = loc.get("LocalityName")
        if localityName not in locality.LOCALITY_NAMES:
            logging.info("Geo: bad locality name: %r, %s",
                    localityName, address)

    return True

def _apply_replaces(value, replaces, reverse=False):
    for old, new in replaces:
        if reverse:
            new, old = old, new
        value = value.replace(old, new)
    return value

def _getLocalityName(country):
    return _apply_replaces(_getRawLocalityName(country), LOCALITY_REPLACES)

def _getRawLocalityName(country):
    loc = country.get("Locality")
    if not loc:
        area = country["AdministrativeArea"]
        loc = area.get("Locality")
        if not loc:
            subarea = area.get("SubAdministrativeArea")
            if not subarea:
                return area["AdministrativeAreaName"]

            loc = subarea.get("Locality")
            if not loc:
                return subarea["SubAdministrativeAreaName"]

    depLocality = loc.get("DependentLocality")
    if not depLocality:
        return loc["LocalityName"]

    while depLocality.get("DependentLocality"):
        depLocality = depLocality["DependentLocality"]
    localityName = depLocality["DependentLocalityName"]
    return locality.NAME_MAPPING.get(localityName, localityName)

