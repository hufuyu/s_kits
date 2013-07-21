#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#---
# project:     chk-info-gae
# Purpose:     format report from other security tools.
# Author:      hufuyu@gmail.com
# Licence:     BSD
#---

SEND_ADDR       = 'hufuyu@gmail.com'
#SEND_ADDR       = 'chk-info@appspot.com'

# init datebase,Pls set complex enough.
# THis only use onetime.
INIT_DB_URL       = '/am/db/init'

# flush database,Pls set complex enough.
FLUSH_DB_URL      = '/am/db/flush'


# db default settings.
DB_INIT_SAVE_ID     = 0
DB_INIT_RESPOOL     =[{
                    'site_type' : 'wooyun_submit',
                    'url'       : 'www.wooyun.org/feeds/submit',
                    }]

DB_INIT_CHECKCONFIG =[{
                    'name'      : 'test',
                    # site_type: don't change this!
                    'site_type' : 'wooyun_submit',
                    'key_words' : '',
                    # need change.
                    'mail_to'   : 'natthun@gmail.com',
                    }]

# mail  settings:
MAIL_CONTEXT_HEADER = """
Dear user:
There are some vulnerability discovered by somebody. please check as soon as
possible. the summary info are blow:\n
"""

MAIL_CONTEXT_FOOTER = """
\nThis email send automate.No longer interested in receiving these emails?,
Pls contact ...
        """
