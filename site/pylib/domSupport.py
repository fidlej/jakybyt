
import re
import datetime
import time
import xml.dom.minidom

def parseRoot(input):
    if isinstance(input, (str, unicode)):
        doc = xml.dom.minidom.parseString(input)
    else:
        doc = xml.dom.minidom.parse(input)
    return doc.documentElement

def isElement(node, elementName):
    return (node.nodeType == node.ELEMENT_NODE
            and node.tagName == elementName)

def getChild(node, elementName):
    """ Returns the first element under that name or None.
    """
    for child in node.childNodes:
        if isElement(child, elementName):
            return child
    return None

def getChildElements(node, elementName):
    """ Returns all child elements with the given name.
    """
    kids = []
    for child in node.childNodes:
        if isElement(child, elementName):
            kids.append(child)
    return kids

def getText(node):
    text = ""
    for child in node.childNodes:
        if child.nodeType == child.TEXT_NODE:
            text += child.data
    return text

def getChildText(node, elementName):
    """ Returns value stored inside the named element.
    @return text or None
    """
    element = getChild(node, elementName)
    if element is None:
        return ""
    return getText(element)

def getDescendantText(node):
    text = ""
    for child in node.childNodes:
        if child.nodeType == child.TEXT_NODE:
            text += child.data
        else:
            text += getDescendantText(child)
    return text

def findNode(node, path):
    """ Returns the first found node on the path.
    The path only accepts tag names separated by '/'.
    """
    tags = path.split("/")
    child = None
    for tag in tags:
        child = getChild(node, tag)
        if child is None:
            return None
        node = child
    return child

def findNodes(node, path):
    """ Returns all nodes matching the given path.
    """
    tags = path.split("/")

    foundNodes = []
    nodesToExamine = [node]
    for tag in tags:
        kids = []
        for toExamine in nodesToExamine:
            kids += getChildElements(toExamine, tag)
        nodesToExamine = kids
        foundNodes = kids
    return foundNodes

def findTexts(node, path):
    nodes = findNodes(node, path)
    return [getText(found) for found in nodes]

def findText(node, path):
    found = findNode(node, path)
    if found is not None:
        return getText(found)
    return ""


FLOAT_NUMBER = r"-?[0-9]+(?:\.[0-9]+)?"
DURATION_PATTERN = re.compile(r"P(?P<years>%sY)?(?P<months>%sM)?(?P<days>%sD)?T?(?P<hours>%sH)?(?P<minutes>%sM)?(?P<seconds>%sS)?" % (6 * (FLOAT_NUMBER,)))

def parseDuration(value):
    """ Parses XML Schema duration datetype:
    http://www.w3.org/TR/xmlschema-2/#duration
    Value example: "PT1H50M0S"
    Returns dict {"years":years, "months":months, ...}
    """
    match = DURATION_PATTERN.match(value)
    if not match:
        raise ValueError("Bad duration: %r" % value)
    numbers = {}
    for key, found in match.groupdict().iteritems():
        if found is None:
            numbers[key] = 0
        else:
            # Strips the designator char
            numbers[key] = float(found[:-1])
    return numbers

DATETIME_PATTERN = re.compile(r"(\d+)-(\d+)-(\d+)T(\d+):(\d+):(\d+)Z?$")

def parseDateTime(value):
    """ Parses subset of XML Schema dateTime:
    Value example: "2007-07-30T03:30:00"
    Returns datetime.datetime.
    """
    match = DATETIME_PATTERN.match(value)
    if match is None:
        raise ValueError("Invalid dateTime value: '%s'" % value)
    numbers = []
    for group in match.groups():
        numbers.append(int(group))
    return datetime.datetime(*numbers)

def pdatetime(value, format="%Y-%m-%d"):
    tm = time.strptime(value, format)
    return datetime.datetime(*tm[:6])

