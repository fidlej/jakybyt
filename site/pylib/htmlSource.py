"""
Library to obtain an URL content.
"""
import urllib2
import urllib
import re
import logging

USER_AGENT = "Mozilla/5.0 (X11; U; Linux i686; en-US) Gecko/20070723"

def getUrlContent(url, options={}, headers={"User-Agent": USER_AGENT}):
    """ Returns the source page with proper unicode encoding.
    """
    fileinput = _getUrlStream(url, options, headers)
    content = fileinput.read()

    charset = None
    info = fileinput.info()
    if "Content-Type" in info:
        contentType = info['Content-Type']
        match = re.search(r"""charset=([^ ;"']*)""", contentType)
        if match is not None:
            charset = match.group(1)
    if charset is None:
        match = re.search(r"""Content-Type.*charset=([^"']*)(?:'|")""", content)
        if match is not None:
            charset = match.group(1)

    if charset is not None:
        logging.debug("Found charset: '%s'" % charset)
        content = unicode(content, charset)
    return content

def _getUrlStream(url, options={}, headers={}):
    url = prepareUrl(url, options)
    request = urllib2.Request(url)
    for name, value in headers.iteritems():
        request.add_header(name, value)
    logging.info("Opening: %s", url)
    return urllib2.urlopen(request)

def prepareUrl(url, options={}):
    first = url.find("?") == -1
    keys = options.keys()
    keys.sort()
    for key in keys:
        if first:
            url += "?"
            first = False
        else:
            url += "&"
        url += "%s=%s" % (_urlquote(key), _urlquote(options[key]))
    return url

def _urlquote(value):
    """ Quotes str or unicode for URL.
    Plain urllib.quote() would raise KeyError on unicode.
    """
    if isinstance(value, unicode):
        value = value.encode("utf-8")
    return urllib.quote(value)

