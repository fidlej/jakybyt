#!/bin/sh
if test $# -eq 1 ; then
	ln -s -f -n "beta$1" latest
	ln -s -f -n "beta`expr 1 + $1`" beta
else
	echo >&2 "Usage: $0 stable_version_number"
	echo >&2 "Switches production version to the given version."
	echo >&2
fi
ls --color=auto -l latest
ls --color=auto -l beta
sudo /etc/init.d/lighttpd restart
