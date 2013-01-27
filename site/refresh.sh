#!/bin/sh
# Refreshes storage.
set -e
./urlDiscoverer.py
./contentDownloader.py
./batchAnalyser.py
