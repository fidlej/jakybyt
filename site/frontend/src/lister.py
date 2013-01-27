
def getListingByDays(analyses):
    """ Outputs list of analyses
    grouped by createdDate days.
    Format:
    [
        (timePoint, [
                analysis,
                analysis,
                ...
            ]
        ),
    ]
    """
    days = []
    lastDate = None
    for analysis in analyses:
        if lastDate != analysis["createdDate"]:
            lastDate = analysis["createdDate"]
            days.append((lastDate, [analysis]))
        else:
            days[-1][1].append(analysis)
    return days

