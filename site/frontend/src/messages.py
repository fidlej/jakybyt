
import os
import gettext
import logging

DOMAIN = "messages"

def install(lang):
    appHome = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    localeHome = os.path.join(appHome, "locale")

    try:
        lang = gettext.translation(DOMAIN, localeHome,
                languages=[lang])
    except IOError, e:
        logging.warn("Falling back from lang: %s; localeHome=%s; reason=%s",
                lang, localeHome, e)
        lang = gettext.translation(DOMAIN, localeHome, fallback=True)
    lang.install(unicode=1)

