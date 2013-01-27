
import logging
import PersistentMap

REAL_DATES_PATH = "data/real_dates.dat"

class AntiFraud:
    def __init__(self):
        self.map = PersistentMap.PersistentMap(REAL_DATES_PATH)
        self.map.setLazySave(True)

    def save(self):
        self.map.save()

    def clarifyRealCreatedDate(self, analysis):
        """ Stores or returns the real createdDate.
        """
        createdDate = analysis["createdDate"]
        hashKey = _getHashKey(analysis)

        realDate = self.map.get(hashKey)
        if realDate is not None:
            if realDate != createdDate:
                #logging.debug("Found faked createdDate: %s, %s, %s",
                #        realDate, createdDate, hashKey)
                pass
            return realDate

        self.map[hashKey] = createdDate
        return createdDate


def _getHashKey(analysis):
    return (analysis["area"], analysis.get("floor"), analysis["geo"],
            analysis["rooms"])


def getWithoutDuplicities(analyses):
    """ Returns analyses without detected duplicities.
    Only the cheapest offer is kept from the duplicated ones.
    Assumes that the analyses are sorted by (createdDate, unitPrice).
    """
    reduced = []
    seen = set()
    for analysis in analyses:
        hash = _getHashKey(analysis)
        if hash not in seen:
            seen.add(hash)
            reduced.append(analysis)

    logging.debug("reduced duplicities: %s -> %s", len(analyses), len(reduced))
    return reduced



