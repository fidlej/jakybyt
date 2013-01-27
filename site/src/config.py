
import os

DEBUG = bool(os.environ.get("DEBUG", False))

# for http://frontend/
#MAP_KEY = "ABQIAAAA5utgD3zqAMmcVm5dKFq3yhS2G4ksK8qnED7EeCboK3SkiH1maxQFUGQWn18rWFeJb9gzLZhSKSG-7A"

# for http://192.168.44.6:1234/
#MAP_KEY = "ABQIAAAA5utgD3zqAMmcVm5dKFq3yhRRaYm4GtXCOPNi-E363UiXcfDw1RSjbKXLfoal-QkxFIRTEq8nUu-A7Q"

# for http://jakybyt.cz/
MAP_KEY = "ABQIAAAA5utgD3zqAMmcVm5dKFq3yhQjoMga_Hamap_DFcXuo67aZuJuMxSZ8rCFi6yfLVMEuF1K9NY58WPZLw"

def setLogging():
    """ Chooses between logging to stderr
    or to a log file.
    Production mode also redirects stderr
    to the log file. So even a cash will be visible.
    """
    import os
    import sys
    import logging
    import logging.config
    os.umask(0)
    if DEBUG:
        logging.basicConfig(level=logging.DEBUG,
                format="%(asctime)s %(levelname)-5s: %(message)s")
        logging.info("Started")
    else:
        logging.config.fileConfig("logging.ini")
        logfilename = "log/server.log"
        try:
            surelog = file(logfilename, "a", 0)
            sys.stderr.flush()
            os.dup2(surelog.fileno(), sys.stderr.fileno())
        except IOError, e:
            logging.error("Unable log to: %r; error: %s", logfilename, e)

