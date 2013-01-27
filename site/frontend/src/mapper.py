
import logging
import math

from util import gis
from src import localdate

def getClusterModel(analyses, zoom, bounds=None):
    """ Returns {count, lastDate, markers}.
    Args:
    zoom ... map zoom, used to reduce visible markers
    bounds ... points from (northEast, southWest) corners
    """
    return Clusterer().getClusterModel(analyses, zoom, bounds)

class Clusterer:
    """ Inspired by client side clusterer:
    http://www.acme.com/javascript/#Clusterer
    """
    def __init__(self):
        self.gridSizeFactor = 4
        self.maxNewest = 8
        self.minCount = 80

    def getClustered(self, analyses, zoom, bounds=None):
        """ Returns analyses clustered inside geo tiles.
        Returns {(tiledLng,tiledLng):[analysis,analysis,...], ...}.

        Considers only offers newer than maxAgeDays
        calculated from the zoom. This limits the number useless of markers
        on zoomed-out map.
        """
        clusters = {}
        latInc, lngInc = self._calcTileSize(zoom)
        if bounds:
            bounds = gis.extendBounds(bounds)
            bounds = self._gridizeBounds(bounds, latInc, lngInc)

        if zoom > 12:
            # The function could be tweaked at:
            # http://www.shodor.org/interactivate/activities/DataFlyer/
            maxAgeDays = int((1.5*zoom - 18)**2 + 2)
        else:
            maxAgeDays = 2

        ageDays = None
        self.count = 0
        self.lastDate = None
        for analysis in analyses:
            geo = analysis["geo"]
            if bounds is None or gis.containsLatLng(bounds, geo):
                if analysis["createdDate"] != self.lastDate:
                    ageDays = localdate.calcAgeDays(analysis["createdDate"])
                    if ageDays > maxAgeDays and self.count > self.minCount:
                        break
                    self.lastDate = analysis["createdDate"]
                lat, lng = geo
                tile = lat // latInc, lng // lngInc
                self._addToCluster(clusters, tile, analysis)

        return clusters

    def getClusterModel(self, analyses, zoom, bounds=None):
        clustered = self.getClustered(analyses, zoom, bounds)
        markers = self._createMarkers(clustered)
        return {
                "count": self.count,
                "lastDate": self.lastDate,
                "markers": markers,
                }

    def _calcTileSize(self, zoom):
        lngInc = 360.0 / (self.gridSizeFactor * 2**zoom)
        #TODO: adjust latInc according the city latitude
        latInc = lngInc / 1.5
        return latInc, lngInc

    def _gridizeBounds(self, bounds, latInc, lngInc):
        """ Aligns the bounds with the grid
        to include all or nothing from a cluster.
        """
        sw, ne = bounds
        sw = (sw[0] // latInc) * latInc, (sw[1] // lngInc) * lngInc
        ne = (ne[0] // latInc + 1) * latInc, (ne[1] // lngInc + 1) * lngInc
        return sw, ne

    def _createMarkers(self, clusters):
        markers = []
        for cluster in clusters.itervalues():
            latSum = 0.0
            lngSum = 0.0
            for analysis in cluster:
                lat, lng = analysis["geo"]
                latSum += lat
                lngSum += lng

            size = len(cluster)
            point = latSum / size, lngSum / size

            markers.append({
                "geo": point,
                "size": len(cluster),
                "newest": cluster[:self.maxNewest],
                })
        return markers

    def _addToCluster(self, clusters, tile, analysis):
        cluster = clusters.get(tile)
        if cluster is None:
            cluster = [analysis]
            clusters[tile] = cluster
        else:
            cluster.append(analysis)
        self.count += 1

