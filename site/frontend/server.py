#!/usr/bin/env python

import os
import sys
import time
import web
import simplejson
import logging

from util import config

if len(sys.argv) <= 1:
    web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    # mod_rewrite rewrites path/to/server.py to ""
    os.environ["REAL_SCRIPT_NAME"] = ""
else:
    config.DEBUG = True

from util import locality
from src import messages
from src import lister, mapper, charter, viewer
from src import handler, formatter, MapFormatter
from src import emailerror
from pylib.webapi import monitor
from common import ColorScale

urls = (
        '/', 'index',
        '/byty', 'homes',
        '/feedme', 'feedme',
        '/feed', 'feed',
        '/mapa', 'map',
        '/graf', 'chart',
        '/vyvoj', 'view',
        '/histogram', 'histogram',
        '/info', 'info',
        '/scale', 'scale',
        '/filter', 'filter',
        '/nastaveni', 'preferences',
        '/version', 'version',
        '/compute', 'compute',
        '/ajax/cluster', 'ajaxCluster',
        '/ajax/filter', 'ajaxFilter',
        '/showtrace/([a-f0-9]+)', 'src.emailerror.showtrace',
        #'/run/([a-zA-Z.]+)', 'src.webrunner.run',
)

class index:
    def GET(self):
        print formatter.page("index", _(u"Search for preferred home in Prague"))()

class homes:
    def GET(self):
        input = web.input(limit=100)
        limit = handler.validN(input.limit)
        analyses = handler.filteredAnalyses(web, limit)
        days = lister.getListingByDays(analyses)

        ungettext = _.im_self.ungettext
        counting = ungettext(u"Showing one home.", u"Showing %(count)s homes.",
                    len(analyses)) % {"count": len(analyses)}
        print formatter.page("item_list", _(u"Latest home offers in Prague"),
                type="withFilter")(days, counting)
class feedme:
    def GET(self):
        from pylib import htmlSource
        params = handler.parseFilter(web)
        for key, value in params.iteritems():
            params[key] = str(value)
        url = htmlSource.prepareUrl("/feed", params)
        web.seeother(url)

class feed:
    def GET(self):
        from util import report
        from src import feeder
        web.header("Content-Type", "application/atom+xml; charset=utf-8")
        analyses = handler.filteredAnalyses(web)
        analyses = feeder.getExportable(analyses)

        url = "http://jakybyt.cz" + web.ctx.fullpath
        print formatter.RENDER.feed(analyses, report.getMtime(), url)

class map:
    def GET(self):
        sight = None
        input = web.input()
        homeUrl = input.get("byt")
        if homeUrl:
            homeUrl = homeUrl.replace(" ", "+")
            analyses = handler.filteredAnalyses(web)
            for analysis in analyses:
                if analysis["url"] == homeUrl:
                    sight = MapFormatter.createSight(analysis)
                    break
            else:
                logging.info("No such home: %r", homeUrl)

        print formatter.page("map", _(u"Map of Prague homes"),
                type="withFilter toggleFilter")(
                        config.MAP_KEY, locality.GEO_BOUNDS, sight)

class chart:
    def GET(self):
        from util import AntiFraud
        analyses = handler.filteredAnalyses(web)
        analyses = AntiFraud.getWithoutDuplicities(analyses)
        timeline = charter.getTimeline(analyses)
        motionDataJs = formatter.RENDER.motionData(timeline)

        print formatter.page("chart", _(u"Chart of home prices in Prague"),
            type="withFilter")(motionDataJs)

class histogram:
    def GET(self):
        from util import AntiFraud
        input = web.input()
        rooms = input.get("rooms", "")
        rooms = rooms.replace(" ", "+")

        analyses = handler.filteredAnalyses(web)
        analyses = AntiFraud.getWithoutDuplicities(analyses)

        longLegend = "(%s)" % len(analyses)
        legend = ""
        if rooms:
            analyses = [a for a in analyses if a["rooms"].startswith(rooms)]
            groupCounts = viewer.getGroupCounts(analyses)
            longLegend = ", ".join("%s (%s)" % pair for pair in groupCounts)
            legend = ", ".join(pair[0] for pair in groupCounts)

        property = "price"
        unit = 100000
        minMax = (1*10**6, 4*10**6)
        dataJs1, maxCount1 = viewer.getHistogramDataJs(analyses, property,
                unit, legend=legend, minMax=minMax)

        minMax = (4*10**6, 7*10**6)
        dataJs2, maxCount2 = viewer.getHistogramDataJs(analyses, property,
                unit, legend=legend, minMax=minMax)

        maxCount = max(10, maxCount1, maxCount2)
        print formatter.page("histogram", _(u"Histogram of Prague Homes"),
            type="withFilter")(dataJs1, dataJs2, maxCount, longLegend)

class view:
    def GET(self):
        from util import saver
        print saver.serve("static/generated/view.html", self._producePage)

    def _producePage(self):
        dataJs1, lastCounts = viewer.getTimeAvgsDataJs()
        dataJs2, lastCounts = viewer.getTimeAvgsDataJs(showCounts=True)
        return formatter.page("view", _(u"Exploratory Visualization")
                )(dataJs1, dataJs2, lastCounts)

class info:
    def GET(self):
        print formatter.page("info", _(u"About the website"))()

class scale:
    def GET(self):
        scale = ColorScale.unitPriceScale
        colors = []
        for x in range(ColorScale.UNIT_PRICE_SCALE_MAX,
                ColorScale.UNIT_PRICE_SCALE_MIN - 1, -10000):
            name = str(x)
            colors.append((name, "%02x%02x%02x" % scale.getRgb(x)))
        print formatter.page("scale", _(u"Color scale of prices"))(colors)

class filter:
    def POST(self):
        input = web.input("path", loc=[])
        path = input.path
        handler.setFilterCookie(web, input)
        web.seeother(path)

class preferences:
    def GET(self):
        input = web.input(path="/byty")
        path = input.path
        handler.knowParsedFilter(web)

        perColumn = 5
        localityColumns = []
        index = 0
        ncols = len(locality.LOCALITY_CHOICES) // perColumn
        if len(locality.LOCALITY_CHOICES) % perColumn != 0:
            ncols += 1
        for col in range(ncols):
            localityColumns.append([])
            for choice in locality.LOCALITY_CHOICES[index:index+perColumn]:
                localityColumns[-1].append((index, choice))
                index += 1

        print formatter.page("preferences", _(u"Preferences"))(
                path, localityColumns)

class version:
    def GET(self):
        web.header('Content-Type', "text/plain; charset=utf-8")
        print "--------------"
        print "file:", __file__
        mtime = os.stat(__file__).st_mtime
        print "mtime:", time.strftime("%Y-%m-%dT%H:%M:%SZ",
                time.gmtime(mtime))
        print "cwd:", os.getcwd()

class compute:
    def GET(self):
        import urllib
        stream = urllib.urlopen("http://lever.appspot.com/compute")
        web.header('Content-Type', "text/plain; charset=utf-8")
        print "Response:", stream.read()

class ajaxCluster:
    def GET(self):
        web.header('Content-Type', "text/javascript; charset=utf-8")
        input = web.input("sw", "ne", "zoom");
        bounds = handler.validBounds(input.sw, input.ne)
        zoom = handler.validN(input.zoom)

        model = mapper.getClusterModel(handler.filteredAnalyses(web),
                zoom, bounds)
        MapFormatter.enhanceClusterModel(model)
        dumpJson(model)

class ajaxFilter:
    def GET(self):
        input = web.input()
        handler.setFilterCookie(web, input)
        dumpJson("OK")

def dumpJson(model):
    web.header('Content-Type', "text/javascript; charset=utf-8", unique=True)
    if config.DEBUG:
        kw = {"indent": True}
    else:
        kw = {"separators": (',', ':')}
    print simplejson.dumps(model, **kw)

if __name__ == "__main__":
    config.setLogging()
    messages.install("cs")
    os.umask(0)

    def _init():
        """ Call functions from their possibly reloaded modules.
        """
        formatter.install()
        web.webapi.internalerror = emailerror.internalerror
    web.loadhooks["init"] = _init
    if config.DEBUG:
        web.run(urls, globals(), web.reloader, monitor.monitor)
    else:
        #web.run(urls, globals(), monitor.monitor, monitor.apachelog)
        web.run(urls, globals(), monitor.monitor)

