#!/usr/bin/env python
"""
Produces a PNG image
from an array of values.
Colores the warm zones by red.
"""

import logging
import cStringIO as StringIO

from common import png, ColorScale
from src import gis, locality, disk

IMAGE_SIZE = (186,146)
TRANSPARENT_COLOR = (0xFF,0x00,0xFF)
ALPHA = 128
OUTPUT_FILENAME = "data/warm.png"

def calcBounds(analyses):
    """ Returns bounds covering all the analyses.
    Returns (sw, ne).
    """
    minLat = min(a["geo"][0] for a in analyses)
    maxLat = max(a["geo"][0] for a in analyses)
    minLng = min(a["geo"][1] for a in analyses)
    maxLng = max(a["geo"][1] for a in analyses)
    return (minLat, minLng), (maxLat, maxLng)

def getGridData(analyses, gridSize, bounds, property="unitPrice"):
    """ Returns property values at fixed grid points.
    """
    w, h = gridSize
    (minLat, minLng), (maxLat, maxLng) = bounds
    latScale = h / float(maxLat - minLat)
    lngScale = w / float(maxLng - minLng)
    logging.debug("pixel size: %s, %s", 1.0/latScale, 1.0/lngScale)

    counts = [[0]*w for i in range(h)]
    data = [[None]*w for i in range(h)]
    for analysis in analyses:
        geo = analysis["geo"]
        if not gis.containsLatLng(bounds, geo):
            continue

        value = analysis[property]
        # latitude grows from the bottom
        py = int(h - (geo[0] - minLat) * latScale)
        px = int((geo[1] - minLng) * lngScale)
        # the point on the boundary is moved above it
        py = min(h - 1, py)
        px = min(w - 1, px)

        count = counts[py][px]
        if count > 0:
            data[py][px] = (data[py][px] * count + value)//(count + 1)
        else:
            data[py][px] = value
        counts[py][px] += 1
    return data

def _getPixels(gridData):
    """ Returns sequence of pixels.
    """
    w = len(gridData[0])
    pixels = [TRANSPARENT_COLOR]*(len(gridData)*w)
    scale = ColorScale.unitPriceScale

    index = 0
    for row in gridData:
        for point in row:
            if point is not None:
                pixels[index] = scale.getRgb(point)

            index += 1
    return pixels

def _createPng(outfile, size, pixels, has_alpha=False):
    def toScanlines(pixels):
        """ Expands sequence of 3-tuples into sequence of rows with bytes.
        """
        array = []
        count = 0
        for pixel in pixels:
            array += pixel
            if has_alpha:
                if pixel == TRANSPARENT_COLOR:
                    array.append(0)
                else:
                    array.append(ALPHA)
            count += 1
            if count == size[0]:
                yield array
                array = []
                count = 0

    transparent = TRANSPARENT_COLOR
    if has_alpha:
        transparent=None
    writer = png.Writer(size[0], size[1],
            has_alpha=has_alpha, transparent=transparent)
    writer.write(outfile, toScanlines(pixels))

def createWarmPicture(analyses):
    bounds = locality.GEO_BOUNDS
    gridData = getGridData(analyses, IMAGE_SIZE, bounds)
    pixels = _getPixels(gridData)

    buffer = StringIO.StringIO()
    _createPng(buffer, IMAGE_SIZE, pixels, has_alpha=True)
    disk.storeAtomicData(OUTPUT_FILENAME, buffer.getvalue())

def updateWarmPicture():
    from src import report, AntiFraud
    analyses = report.fetchReport()
    analyses = AntiFraud.getWithoutDuplicities(analyses)
    createWarmPicture(analyses)
    #print "effective bounds:", calcBounds(analyses)

def main():
    updateWarmPicture()

if __name__ == "__main__":
    logging.root.setLevel(logging.DEBUG)
    main()

