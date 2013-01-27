#!/usr/bin/env python

import os
import sys
import subprocess
import logging
import time

from util import report

class run:
    def GET(self, scriptName):
        import web
        web.header('Content-Type', 'text/plain; charset=utf-8')
        return runSiteScript(scriptName)

def runSiteScript(scriptName):
    """ Executes given site script.
    Returns generator of an artifical output while
    the script is running (to work around idle-timeout).
    """
    logging.info("Starting script %r", scriptName)
    popen = _forkSiteScript(scriptName)
    return _keepRunning(scriptName, popen)

def _keepRunning(scriptName, popen):
    counter = 0
    retcode = popen.poll()
    while retcode is None:
        yield "%s\n" % counter
        time.sleep(1)
        counter += 1
        retcode = popen.poll()

    if retcode != 0:
        logging.error("Script %r finished with: %s", scriptName, retcode)
    else:
        logging.info("Script %r finished OK", scriptName)
        # preload the cache
        report.fetchCachedReport();
    yield "finish: %s\n" % retcode

def _forkSiteScript(scriptName):
    """ Starts a ../<scriptName> script.
    The script working directory is set to its directory.
    """
    frontendHome = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    siteHome = os.path.realpath(os.path.join(frontendHome, ".."))
    siteScript = os.path.join(siteHome, scriptName)
    return subprocess.Popen([siteScript], cwd=siteHome,
            stdout=file("/dev/null", "w"))

def main():
    for data in runSiteScript("test.py"):
        sys.stdout.write(data)

if __name__ == "__main__":
    logging.root.setLevel(logging.DEBUG)
    main()

