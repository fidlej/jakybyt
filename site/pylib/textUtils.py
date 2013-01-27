
import re
import logging
import htmlentitydefs
import unicodedata

def utf8(text):
    """ Converts utf-8 string from 8-bit to unicode representation.
    """
    if isinstance(text, str):
        text = unicode(text, "utf-8")
    return text

def deaccent(text):
    text = utf8(text)
    chars = []
    for aChar in unicodedata.normalize("NFD", text):
        if not unicodedata.combining(aChar):
            chars.append(aChar)
    return "".join(chars)

def isWithDiacritics(unistr):
    for aChar in unicodedata.normalize("NFD", unistr):
        if unicodedata.combining(aChar):
            return True
    return False

def deHtml(text):
    """ Returns plain text without HTML tags and entities.
    Also collapses spaces.
    """
    if text is None:
        return None
    text = re.sub(r"<[^>]+>", "", text)
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return decodeHtmlEntities(text)

def decodeHtmlEntities(text):
    """ Returns plain text without html entities.
    """
    decoded = ""
    pos = text.find("&")
    while pos != -1:
        entityEnd = text.find(";", pos)
        if entityEnd != -1:
            decoded += text[:pos]
            entity = text[pos+1:entityEnd]
            decoded += decodeEntity(entity)

            text = text[entityEnd+1:]
        else:
            logging.debug("Unenclosed HTML entity: %r" % text[pos:])
            decoded += text[:pos+1]
            text = text[pos+1:]
        pos = text.find("&")

    decoded += text
    return decoded

def decodeEntity(entity):
    decoded = ""
    codePoint = None
    if entity.startswith("#x"):
        codePoint = int(entity[2:], 16)
    elif entity.startswith("#"):
        codePoint = int(entity[1:])
    else:
        codePoint = htmlentitydefs.name2codepoint.get(entity)

    if codePoint is not None:
        decoded = unichr(codePoint)
    else:
        logging.debug("Unknown HTML entity: %r" % entity)
    return decoded

