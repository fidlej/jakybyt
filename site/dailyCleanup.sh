#!/bin/sh
set -e
./purgeBrokenUrls.py
./contentDownloader.py -f
./batchAnalyser.py -f
./exportAvgs.py
rm -f frontend/static/generated/view.html
wget -q http://jakybyt.cz/vyvoj -O /dev/null

