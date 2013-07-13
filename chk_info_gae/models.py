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

class ResPool(db.Model):
    name            = db.StringProperty()
    site_type       = db.StringProperty(required=True,choices=set(['wooyun_submit', ]))
    url             = db.StringProperty(required=True)
    last_get_date   = db.DateProperty()
    last_get_status = db.StringProperty(default='200')
    last_save_id    = db.IntegerProperty(required=True)
    # set min check time,void too many times.
    min_gap         = db.StringProperty()

class CheckConfig(db.Model):
    name            = db.StringProperty(required=True)
    desc            = db.StringProperty()
    site_type       = db.StringProperty(required=True,choices=set(['wooyun_submit',]))
    last_chk_id     = db.IntegerProperty(required=True)
    key_words       = db.StringProperty()
    # send one email  everyday or other(at 8.pm\14pm\16pm).
    notice          = db.BooleanProperty(default=True)
    mail_to         = db.StringProperty()
    sent_freq       = db.StringProperty()
    since           = db.DateTimeProperty()
    daily_mail_num  = db.IntegerProperty(default=0)
    total_mail_num  = db.IntegerProperty(default=0)
    total_chk_num   = db.IntegerProperty(default=0)


class WooyunSubmitData(db.Model):
    #'link','title','desc','stauts''pubDate','author','guid'
    # rename 'WooyunData' add 'vuln_type','rank','status'
    # renew date over one month
    guid    = db.StringProperty(required=True)
    link    = db.StringProperty(required=True)
    pub_date= db.DateTimeProperty()
    title   = db.StringProperty()
    desc    = db.TextProperty()
    author  = db.StringProperty()
    detail  = db.TextProperty()
    #choices=set([u'未公开', ])
    status  = db.StringProperty(default=u'暂未公开')
    save_id = db.IntegerProperty()

class SysStat(db.Model):
    # stat sys run every daily.
    # such as : save_id
    stats_id       = db.StringProperty(required=True)
    stats_at      = db.DateTimeProperty()
    count         = db.IntegerProperty(required=True)

