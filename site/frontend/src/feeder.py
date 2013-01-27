
MIN_NUM_EXPORTED = 120
MIN_DAYS_EXPORTED = 2

def getExportable(analyses):
    lastDay = None
    ageDays = 0
    for i, analysis in enumerate(analyses):
        if analysis["createdDate"] != lastDay:
            lastDay = analysis["createdDate"]
            ageDays += 1
            if ageDays >= MIN_DAYS_EXPORTED and i >= MIN_NUM_EXPORTED:
                return analyses[:i]
    return analyses

