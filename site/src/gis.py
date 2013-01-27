
def extendBounds(bounds):
    #TODO: care about overflow of degrees
    sw, ne = bounds
    dy = (ne[0] - sw[0]) * 0.1
    dx = (ne[1] - sw[1]) * 0.1
    return ((sw[0] - dy, sw[1] - dx),
            (ne[0] + dy, ne[1] + dx))

def containsLatLng(bounds, geo):
    """ Check that geo is inside bounds (inclusive).
    Bounds are defined by [southWest, northEast] corners.
    The southWest has the smallest values,
    the northEast has the biggest values (like on a graf).
    """
    #TODO: fix it when crossing the 180 degrees meridian
    sw, ne = bounds
    return (sw[0] <= geo[0] <= ne[0]
            and sw[1] <= geo[1] <= ne[1])


