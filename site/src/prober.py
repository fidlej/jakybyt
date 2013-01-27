#!/usr/bin/env python

import optparse

def parseArgs():
    parser = optparse.OptionParser()
    parser.add_option("-u", "--url", type="string",
            help="Search by URL.")
    return parser.parse_args()

def showAnalysis(analysis):
    print analysis

def main():
    import report
    analyses = report.fetchReport()

    options, args = parseArgs()
    if options.url:
        for analysis in analyses:
            if analysis["url"] == options.url:
                showAnalysis(analysis)
                return

if __name__ == "__main__":
    main()
