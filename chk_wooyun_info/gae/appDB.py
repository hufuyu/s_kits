#!/usr/bin/env python2
# coding: utf-8

#---
# project:     chk-info-gae
# Purpose:     format report from other security tools.
# Author:      hufuyu@gmail.com
# Licence:     BSD
#---

import datetime
from google.appengine.ext import db
from google.appengine.api import users

class AppConfig(db.Model):
    name            = db.StringProperty(required=True)
    site_type       = db.StringProperty(required=True,choices=set(['wooyun_submit', ]))
    url             = db.StringProperty(required=True)
    last_get_date   = db.DateProperty()
    last_get_status = db.StringProperty(required=True,default='200')
    key_words       = db.StringProperty()
    # send one email  everyday or other(at 8.pm\14pm\16pm).
    notice          = db.BooleanProperty()
    mail_to         = db.StringProperty()


class WooyunSubmitData(db.Model):
    #'link','title','desc','stauts''pubDate','author','guid'
    guid = db.StringProperty(required=True)
    link = db.StringProperty(required=True)
    pubDate = db.DateProperty()
    title = db.StringProperty()
    desc  = db.StringProperty()
    author = db.StringProperty()
    #choices=set([u'未公开', ])
    status = db.StringProperty()

