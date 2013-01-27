"""
Derived from:
http://blogstatic.micropledge.com/2007/11/emailerror.py.txt
"""

from util import config

# change these to suit your setup
SMTP_SERVER = 'localhost'
NOTIFY_EMAIL = 'error@jakybyt.cz'
ERROR_FILE_PREFIX = 'log/errors/'
ERROR_LINK_PREFIX = '/showtrace/'
SUBJECT_TEMPLATE = 'Exception on %s'

import sys
import sha, smtplib
from email.MIMEText import MIMEText
import logging

import web

def _email(subject, body, to, from_=None):
    if not from_: from_ = to
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_
    msg['To'] = to
    s = smtplib.SMTP(SMTP_SERVER)
    try:
        refused = s.sendmail(from_, to, msg.as_string())
    except smtplib.SMTPRecipientsRefused, r:
        refused = r.recipients
    s.quit()
    return refused

def _inform(page):
    key = sha.new(page).hexdigest()
    f = file(ERROR_FILE_PREFIX + key + '.html', 'wb')
    f.write(page)
    f.close()
    link = web.ctx.home + ERROR_LINK_PREFIX + key

    exception_type, exception_value, tback = sys.exc_info()
    body = "%s: %s\n\n%s\n" % (exception_type, exception_value, link)
    logging.error(body)
    subject = SUBJECT_TEMPLATE % web.ctx.host
    _email(subject, body, NOTIFY_EMAIL)

def internalerror():
    if config.DEBUG:
        return web.debugerror()

    web.header('Content-Type', 'text/html; charset=utf-8', unique=True)
    web.ctx.status = "500 Internal Server Error"
    print 'internal server error'
    page = web.djangoerror()
    _inform(page)

class showtrace:
    def GET(self, key):
        # You should do a check here to see if the user is an admin user.
        # You should also check that they're viewing the traceback over HTTPS,
        # otherwise potentially critical data like DB passwords can be sent in the clear.
        web.header('Content-Type', 'text/html; charset=utf-8')
        try:
            f = file(ERROR_FILE_PREFIX + key + '.html', 'rb')
        except IOError:
            print 'Error file not found'
        else:
            print f.read()

