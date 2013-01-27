
import logging
import operator
import cgi, urllib

from util import report, config, locality
from src import localdate

FILTERS = ("minFloor", "minArea", "maxUnitPrice", "maxPrice", "days", "loc", "b")
DEFAULT_FILTER = "minFloor=2"
FILTER_COOKIE = "filter"
CONTEXT_FILTER_NAME = "analysisFilter"

def validPoint(value):
    try:
        a, b = value.split(",")
        return float(a), float(b)
    except ValueError:
        _stopRequest()

def validN(value):
    try:
        return max(0, int(value))
    except ValueError:
        return 0

def validBool(value):
    return value in (True, 1, "1", "true", "on", "yes")

def validBounds(swValue, neValue):
    #TODO: it would not work above North Pacific where sw[0] > ne[0]
    sw = validPoint(swValue)
    ne = validPoint(neValue)
    if not (sw[0] < ne[0] and sw[1] < ne[1]):
        logging.warn("invalid sw < ne: %s, %s", sw, ne)
        _stopRequest()
    return sw, ne

def filteredAnalyses(web, limit=None):
    analyses = report.fetchCachedReport()
    if limit is None:
        limit = len(analyses)

    params = parseFilter(web)
    rules = []
    for name in FILTERS:
        if name not in params:
            continue
        value = params[name]

        op = None
        if name == "days":
            op = operator.ge
            value = _getStrDateBeforeDays(value)
            propertyName = "createdDate"
        elif name == "loc" and value > 0:
            propertyName = "locality"
            op = lambda x, container: locality.NAME_TO_CHOICE_MAPPING.get(x, x) in container
            value = frozenset(_getLocalities(value))
        else:
            if name.startswith("max"):
                propertyName = _detitle(name[3:])
                op = operator.le
            elif name.startswith("min"):
                propertyName = _detitle(name[3:])
                op = operator.ge
            else:
                propertyName = name
                op = operator.eq

        rules.append((propertyName, op, value))

    return _filterAnalyses(analyses, rules, limit)

def _getLocalities(locBits):
    localities = []
    for i, localityName in enumerate(locality.LOCALITY_CHOICES):
        if 2**i & locBits:
            localities.append(localityName)
    return localities

def getFilteredLocalities(web):
    locBits = getUsedFilterParams(web).get("loc", 0)
    return _getLocalities(locBits)

def _detitle(name):
    """ Lowers the first letter.
    """
    return name[0:1].lower() + name[1:]

def _getStrDateBeforeDays(days):
    timestamp = localdate.beforeDays(days)
    return localdate.strDate(timestamp)

def _parseFilterParams(query):
    """ Returns filter as dict with "name":number pairs.
    """
    params = cgi.parse_qs(query)
    for key, found in params.iteritems():
        params[key] = found[0]
    return _validFilterParams(params)

def _validFilterParams(params):
    valid = {}
    for key in FILTERS:
        strValue = params.get(key)
        if strValue:
            valid[key] = validN(strValue)
    return valid

def _filterAnalyses(analyses, rules, limit):
    """ Returns analyses where all rules passed.
    """
    filtered = []
    if limit == 0:
        return filtered

    for analysis in analyses:
        for name, op, value in rules:
            if not op(analysis.get(name), value):
                # optimization for sorted by createdDate
                if name == "createdDate":
                    return filtered
                break
        else:
            filtered.append(analysis)
            limit -= 1
            if limit <= 0:
                return filtered
    return filtered

def setFilterCookie(web, input):
    cookie = _prepareFilterCookie(web.cookies(), input)
    logging.debug("setting filter: %r", cookie)
    web.setcookie(FILTER_COOKIE, cookie, expires=20*365*24*3600)

def _prepareFilterCookie(existingCookies, input):
    params = []
    locBits = _prepareLocality(existingCookies, input)
    if locBits:
        params.append(("loc", str(locBits)))

    for name in FILTERS:
        if name == "loc":
            continue
        if input.get(name):
            params.append((name, input[name]))
    return urllib.urlencode(params)

def _prepareLocality(existingCookies, input):
    """ Parses locality settings from input and existing cookies.
    Returns 0 for no locality selection,
    or a locality bit set number.
    """
    existingParams = _parseFilterCookie(existingCookies)
    local = input.get("local", None)
    if local is None:
        return existingParams.get("loc", 0)
    if not validBool(local):
        return 0

    bits = 0
    for choice in input.get("loc", []):
        choice = validN(choice)
        if choice < len(locality.LOCALITY_CHOICES):
            bits |= 2**validN(choice)
        else:
            logging.error("Invalid locality number: %s", choice)
    return bits

def parseFilter(web):
    input = web.input()
    if _isFilterUsed(input):
        params = _validFilterParams(input)
    else:
        # Cookies are used, don't cache the response.
        # "no-store" is not used, because Back and Forward is OK.
        web.header("Cache-Control", "no-cache", unique=True)
        cookies = web.cookies()
        params = _parseFilterCookie(cookies)

    web.ctx[CONTEXT_FILTER_NAME] = params
    return params

def _parseFilterCookie(cookies):
    return _parseFilterParams(cookies.get(FILTER_COOKIE, DEFAULT_FILTER))

def knowParsedFilter(web):
    if CONTEXT_FILTER_NAME not in web.ctx:
        parseFilter(web)

def _isFilterUsed(params):
    for filterName in FILTERS:
        if filterName in params:
            return True
    return False

def getUsedFilterParams(web):
    return web.ctx.get(CONTEXT_FILTER_NAME, {})

def isSelected(web, filterName, value):
    return value == getUsedFilterParams(web).get(filterName)

def _stopRequest():
    import web
    logging.warn("invalid input: %s", web.ctx.fullpath)
    web.badrequest()
    raise StopIteration

