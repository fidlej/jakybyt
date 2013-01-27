#!/bin/sh
domain=messages

mkdir -p locale
pot="locale/$domain.pot"
xgettext -o "$pot" `find . -name '*.py'`
for lang in cs ; do
    base="locale/$lang/LC_MESSAGES"
    mkdir -p "$base"
    po="$base/$domain.po"
    if test ! -f "$po" ; then
        msginit -i "$pot" -o "$po" -l "$lang" --no-translator
    fi
    msgmerge -U "$po" "$pot"
    msgfmt -o "$base/$domain.mo" "$po"
done
