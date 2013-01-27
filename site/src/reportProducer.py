# coding: utf-8
import logging

import localgeocoder
import report
import storage
import AntiFraud

MAX_PRICE = 15*10**6
MIN_UNIT_PRICE = 18000
MAX_UNIT_PRICE = 200000
UNWANTED_BUILD_TYPE = u"panelová"

def produceReport(newUrls, cleanStart=False):
    newUrlsSet = frozenset(newUrls)
    newAnalyses = _getEnhancedAnalyses(newUrlsSet)
    if cleanStart:
        analyses = []
    else:
        analyses = report.fetchReport()
    oldLen = len(analyses)
    _keepUniqueAndNewer(analyses, newUrlsSet, newAnalyses)

    def analysisCmp(a1, a2):
        c = cmp(a1["createdDate"], a2["createdDate"])
        return c or -cmp(a1["unitPrice"], a2["unitPrice"])

    analyses.sort(cmp=analysisCmp, reverse=True)
    report.storeReport(analyses)
    logging.info("Advanced from %s to %s analyses", oldLen, len(analyses))

def _keepUniqueAndNewer(existing, newUrlsSet, newAnalyses):
    urlToIndexMap = {}
    for index, analysis in enumerate(existing):
        urlToIndexMap[analysis["url"]] = index

    existingUrlsSet = frozenset([a["url"] for a in existing])
    urlsIntersection = existingUrlsSet & newUrlsSet
    logging.info("Reanalysed urls: %s", len(urlsIntersection))

    for new in newAnalyses:
        url = new["url"]
        if url in urlsIntersection:
            existing[urlToIndexMap[url]] = new
        else:
            existing.append(new)

def _getEnhancedAnalyses(newUrls):
    analyses = []
    geoResolver = localgeocoder.GeoResolver()
    antifraud = AntiFraud.AntiFraud()
    for url in newUrls:
        analysis = storage.fetchAnalysis(url)
        if _enhanceAnalysis(url, analysis):
            if _addGeoPoint(analysis, geoResolver):
                _numerizeBuildType(analysis)
                analysis["createdDate"] = antifraud.clarifyRealCreatedDate(
                        analysis)
                analyses.append(analysis)

    geoResolver.close()
    antifraud.save()
    logging.info("Enhanced %s/%s", len(analyses), len(newUrls))
    return analyses

def _enhanceAnalysis(url, analysis):
    if analysis.get("createdDate") is None:
        logging.debug("Ignoring unparsed: %s", analysis)
        return False
    if analysis.get("area") is None or analysis["area"] <= 0:
        #logging.debug("Ignoring without area: %s", analysis)
        return False
    if analysis.get("rooms") is None:
        #logging.debug("Ignoring without rooms: %s", analysis)
        return False
    if analysis.get("unitPrice") is None and analysis.get("price") is None:
        #logging.debug("Ignoring without price: %s", analysis)
        return False

    analysis["url"] = url
    if analysis.get("unitPrice") is None:
        analysis["unitPrice"] = analysis["price"] // analysis["area"]
    elif analysis.get("price") is None:
        analysis["price"] = analysis["unitPrice"] * analysis["area"]

    if analysis["unitPrice"] < MIN_UNIT_PRICE:
        #logging.debug("Ignoring too low unit price: %s", analysis)
        return False
    if analysis["unitPrice"] > MAX_UNIT_PRICE:
        #logging.debug("Ignoring too high unit price: %s", analysis)
        return False
    if analysis["price"] > MAX_PRICE:
        #logging.debug("Ignoring too high price: %s", analysis)
        return False

    # better title is the generated one
    del analysis["title"]
    return True

def _addGeoPoint(analysis, geoResolver):
    address = analysis.get("address")
    if address is None:
        logging.debug("Ignoring without address: %s", analysis["url"])
        return False

    if not geoResolver.isLocal(analysis["url"]):
        logging.info("Ignoring non-local: %s", analysis["url"])
        return False

    point, localityName = geoResolver.getGeoPointAndLocality(address)
    if point is None:
        #logging.debug("Ignoring without geo: %s", address)
        return False

    del analysis["address"]
    analysis["locality"] = localityName
    analysis["geo"] = point
    return True

def _numerizeBuildType(analysis):
    buildType = analysis.get("b")
    if buildType is not None:
        if UNWANTED_BUILD_TYPE == buildType.lower():
            analysis["b"] = 0
        else:
            analysis["b"] = 1

