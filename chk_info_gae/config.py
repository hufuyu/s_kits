#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#---
# project:     chk_news
# Purpose:     format report from other security tools.
# Author:      hufuyu@gmail.com
# Licence:     BSD
#---

SEND_ADDR       = hufuyu@gmail.com

# init datebase,Pls set complex enough.
# THis only use onetime.
INIT_DB_URL       = /am/db/init

# flush database,Pls set complex enough.
FLUSH_DB_URL      = /am/db/flush


# db default settings.
DB_INIT_SAVE_ID   = 0


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
