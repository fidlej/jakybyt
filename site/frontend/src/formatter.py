# coding: utf-8

import urllib
import web
import simplejson
import time

from util import config, locality
from src import handler, localdate

RENDER = web.template.render("templates/", cache=not config.DEBUG)
web.template.Template.globals["render"] = RENDER

def page(pageName, title, type=""):
    """ Returns template
    to render given page inside shell.
    """
    if "withFilter" in type:
        handler.knowParsedFilter(web)

    def body(*args, **kwargs):
        body = getattr(RENDER, pageName)(*args, **kwargs)
        return RENDER.shell(body, title, type)
    return body

def install():
    web.template.Template.globals["formatPrice"] = formatPrice
    web.template.Template.globals["formatDate"] = formatDate
    web.template.Template.globals["formatAge"] = formatAge
    web.template.Template.globals["formatUtc"] = formatUtc
    web.template.Template.globals["isToday"] = isToday
    web.template.Template.globals["isYesterday"] = isYesterday
    web.template.Template.globals["jsnize"] = jsnize
    web.template.Template.globals["urlEncode"] = urlEncode
    web.template.Template.globals["separate"] = separate
    web.template.Template.globals["oddEven"] = oddEven
    web.template.Template.globals["oddEvenDiffs"] = oddEvenDiffs
    web.template.Template.globals["htmlLinkAttrs"] = htmlLinkAttrs
    web.template.Template.globals["ctxInfo"] = ctxInfo
    web.template.Template.globals["htmlOptionAttrs"] = htmlOptionAttrs
    web.template.Template.globals["htmlCheckedLoc"] = htmlCheckedLoc
    web.template.Template.globals["htmlFilteredLocalities"] = htmlFilteredLocalities
    web.template.Template.globals["htmlAnalysisRow"] = htmlAnalysisRow
    web.template.Template.globals["formatUsedFilter"] = formatUsedFilter

def formatPrice(value):
    if value is None:
        return value
    ornated = []
    separator = _(",")
    for i, c in enumerate(reversed(str(value))):
        if i > 0 and i % 3 == 0:
            ornated.insert(0, separator)
        ornated.insert(0, c)
    return ''.join(ornated)

def formatDate(strDate):
    year, month, day = strDate.split("-")
    return _("%(year)s-%(month)s-%(day)s") % locals()

def formatAge(strDate, now=None):
    ageDays = localdate.calcAgeDays(strDate, now)
    ungettext = _.im_self.ungettext
    return ungettext(u"%s day", u"%s days", ageDays) % ageDays

def formatUtc(timestamp):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(timestamp))

def isToday(strDate):
    return strDate == localdate.strDate()

def isYesterday(strDate):
    yesterday = localdate.beforeDays(1)
    return strDate == localdate.strDate(yesterday)

def jsnize(value):
    """ Converts value to a string representing a JS object."""
    return simplejson.dumps(value)

def urlEncode(value):
    if isinstance(value, unicode):
        value = value.encode("utf-8")
    return urllib.quote(value)

def separate(separator, collection):
    s = None
    for item in collection:
        yield s, item
        s = separator

def oddEven(collection):
    states = ("odd", "even")
    for index, item in enumerate(collection):
        yield states[index % 2], item

def oddEvenDiffs(collection, property):
    states = ("odd", "even")
    selected = 1
    lastValue = None
    for item in collection:
        if lastValue != item[property]:
            selected = 1 - selected
            lastValue = item[property]
        yield states[selected], item

def htmlLinkAttrs(href, fullOnly=False):
    attrs = 'href="%s"' % href
    matches = False
    if web.ctx.fullpath == href or (not fullOnly and web.ctx.path == href):
        attrs += ' class="current"'
    return attrs

def ctxInfo(key):
    return web.ctx[key]

def htmlOptionAttrs(filterName, value):
    """ Renders selected="selected" attribute
    when given filter value is in use.
    """
    result = 'value="%s"' % value
    if handler.isSelected(web, filterName, value):
        result += ' selected="selected"'
    return result

def htmlCheckedLoc(value):
    localities = handler.getFilteredLocalities(web)
    if value is None:
        if len(localities) == 0:
            return ' checked="checked"'
        else:
            return ""

    if value == -1:
        if len(localities) > 0:
            return ' checked="checked"'
        else:
            return ""

    if locality.LOCALITY_CHOICES[value] in localities:
        return ' checked="checked"'
    else:
        return ""

def htmlFilteredLocalities():
    localities = handler.getFilteredLocalities(web)
    return ", ".join(
            web.websafe(loc).replace(" ", "&nbsp;") for loc in localities)

def htmlAnalysisRow(analysis, onMap=False, rowClass="", showFloor=True, ageDisplay=None, mapUrl="/mapa"):
    """ Outputs utf-8 encoded HTML with the home analysis.
    Done inside code because of speed up (3-times faster than templetor).
    """
    model = {
        "rowClass": web.websafe(rowClass),
        "url": web.websafe(analysis["url"]),
        "rooms": web.websafe(analysis["rooms"]),
        "price": web.websafe(formatPrice(analysis["price"])),
        "unitPrice": web.websafe(formatPrice(analysis["unitPrice"])),
        "area": analysis["area"],
        "targetAttr": "",
        "extra": "",
    }

    if showFloor:
        model["extra"] = """<td class="n">%s</td>""" % (analysis.get("floor") or "-")
    if ageDisplay is not None:
        if ageDisplay:
            model["extra"] += "<td>%s</td>" % web.websafe(formatAge(analysis["createdDate"]))
        else:
            model["extra"] += "<td></td>"

    if onMap:
        model["targetAttr"] = ' target="_blank"'
    else:
        model["extra"] += """<td class="address"><a href="%s?byt=%s">%s</a></td>""" % (
            web.websafe(mapUrl),
            web.websafe(urlEncode(analysis["url"])),
            web.websafe(analysis["locality"]))


    return """\
<tr class="%(rowClass)s"><td><a href="%(url)s"%(targetAttr)s>%(rooms)s</a></td><td class="n">%(price)s Kč</td><td class="n"><b>%(unitPrice)s Kč/m²</b></td><td class="n">%(area)s m²</td>%(extra)s</tr>
""" % model

def formatUsedFilter():
    params = handler.getUsedFilterParams(web)
    #TODO: use ungettext for days
    #TODO: use better format for building type
    formats = {
            "maxPrice": _(u"max. %s CZK"),
            "maxUnitPrice": _(u"max. %s CZK/m²"),
            "minArea": _(u"min. %s m²"),
            "minFloor": _(u"min. %s floor"),
            "b": _(u"stavba %s"),
            "days": _(u"max. %s days old"),
        }

    parts = []
    keys = params.keys()
    if "loc" in keys:
        keys.remove("loc")

    keys.sort()
    for key in keys:
        part = formats.get(key, "%s") % params[key]
        parts.append(part)

    if "loc" in params:
        parts += handler.getFilteredLocalities(web)
    return ", ".join(parts)

