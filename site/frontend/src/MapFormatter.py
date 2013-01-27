#coding: utf-8

import time
from xml.sax.saxutils import escape

import formatter
from src import localdate

# Marker shade steps.
# Shade 1 is the min value used,
# when 0 was used, the chart API ignored the color.
SHADES = [255, 192, 192, 128, 128, 128, 64, 64, 64, 64, 1]

def enhanceClusterModel(markers):
    MapFormatter().enhanceClusterModel(markers)

class MapFormatter:
    def __init__(self):
        pass

    def enhanceClusterModel(self, model):
        model["info"] = self._produceInfo(model)
        self._enhanceMarkers(model["markers"])

    def _produceInfo(self, model):
        count = model["count"]
        if count == 0:
            return "&nbsp;"

        ageStr = formatter.formatAge(model["lastDate"])
        ungettext = _.im_self.ungettext
        infoTemplate = ungettext(
                u"""Marked <b>one</b> <a href="#">eligible home</a>, newer then %(age)s.""",
                u"""Marked <b>%(count)s</b> <a href="#">eligible homes</a>, all newer then %(age)s.""",
                count)
        return infoTemplate % {
                "count": count,
                "age": ageStr,
                }

    def _enhanceMarkers(self, markers):
        now = time.time()
        for marker in markers:
            marker["newestHtml"] = self._formatNewestHtml(marker["newest"])

            ageDays = localdate.calcAgeDays(marker["newest"][0]["createdDate"], now)
            shadeIndex = min(ageDays // 4, len(SHADES) - 1)
            shade = SHADES[shadeIndex]
            marker["color"] = "%02x%02x%02x" % (shade, shade, shade)

            del marker["newest"]

    def _formatNewestHtml(self, newest):
        return formatter.RENDER.newest_info(newest)

    def _htmlStuff(self, text, minLen):
        stuffLen = max(0, minLen - len(text))
        return "&nbsp;" * stuffLen


def createSight(analysis):
    zoomInBody = formatter.RENDER.zoom_in()
    sight = {
            "geo": analysis["geo"],
            "infoHtml": formatter.RENDER.sight_info(analysis, zoomInBody),
            }
    return sight

