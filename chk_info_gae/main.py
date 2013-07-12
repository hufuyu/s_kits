#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#---
# project:     chk_news
# Purpose:     format report from other security tools.
# Author:      hufuyu@gmail.com
# Licence:     BSD
#---
#   ver 0.3-20130711
#           *  fix bugs: save every hour/ wooyun[description] re error.
#   ver 0.1-20130706
#           *  just run...  very simple.
#---

import logging
import re
import webapp2 as webapp
from xml.dom.minidom import parseString
from datetime import datetime

import config
import models

from google.appengine.api import mail
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import db

#********************* handle URL ******************************

class indexHandler(webapp.RequestHandler):

    def get(self):
        index_tpl = """
<html><head>
<title>%s</title>
<style>
body {padding: 20px;font-family: arial, sans-serif;font-size: 14px;}
pre { background: #F2F2F2; padding: 10px; }
</style></head>
<body>%s
<pre>%s</pre>
%s</body></html>
"""
        title = "chk-info-gae:check some info in sometime,powed by gae."
        content = "<h1>chk-info-gae</h1><br/>"
        pre_content = "this is system running info."
        footer = "powered by gae, Licence:BSD , Other Question,PLs Mail:hufuyu@gmail.com"
        index_tpl_args = (title,content,pre_content,footer)
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(index_tpl % index_tpl_args)

class init_dbHandler(webapp.RequestHandler):

  def get(self):
        chk_conf = models.CheckConfig.all()
        if not chk_conf.get():
            try:
                ck_wooyun = models.CheckConfig(name ='test',site_type='wooyun_submit',
                                        last_chk_id = config.DB_INIT_SAVE_ID,notice=True,mail_to='natthun@gmail.com',
                                        since=datetime.now())
                ck_wooyun.put()
                res_wooyun = models.ResPool(site_type='wooyun_submit',url='www.wooyun.org/feeds/submit',
                                            last_get_status='200',last_save_id=config.DB_INIT_SAVE_ID)
                res_wooyun.put()
                logging.info("input init data: default value,maybe need change")
            except db.BadValueError:
                logging.error("init data error")
            return

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write("No Need initialize")
        #self.response.out.write(type(sysconf.get()))
        #for entity in sysconf.run():
        #    self.response.out.write(str(entity.key())+"\n")

class resetHandler(webapp.RequestHandler):

    def get(self):
        # reset daily number: CheckConfig.daily_mail_num
        chk_conf = models.CheckConfig.all()
        if not chk_conf.get():
            for item in chk_conf.run():
                item.daily_mail_num = 0
                item.put()
            logging.info('Daily  statistics data reset to 0.')

class chkHandler(webapp.RequestHandler):

    def get(self):
        chk_cfg = self._chkReqArgs()
        if not chk_cfg:
            self.error(404)
            return

        res_pool = models.ResPool.all().filter('site_type =',chk_cfg.site_type)

        if not res_pool.get():
            logging.error('site_type not set in ResPool,Pls chk < %s >' % chk_cfg.site_type)
            self.error(404)
            return

        for res in res_pool.run():
            # check gap, if need fetch data

            # fetch data  and save
            if res.site_type == 'wooyun_submit':
                chk_wooyun = chkWooyunSubmitRSS(res.url)
                msgs = chk_wooyun.fetchData()
                if not msgs:
                    return
                # save data: get last saved data.  delete repeat.
                saved = chk_wooyun.saveData(msgs,res.last_save_id)
                # if save date, update ResPool.last_save_id
                if saved:
                    res.last_save_id += 1
                    res.put()
            # chk data which contain keyword
                if chk_cfg.last_chk_id < res.last_save_id:
                    key_msgs = chk_wooyun.checkKeyWord(chk_cfg.last_chk_id,chk_cfg.key_words)
                    chk_cfg.last_chk_id = res.last_save_id
                    chk_cfg.put()
                else:
                    key_msgs = None

        if chk_cfg.notice and key_msgs:
            logging.info("prepare send notice ...")
            self.sendNotice(chk_cfg.mail_to,key_msgs)
            chk_cfg.total_mail_num += 1
            chk_cfg.daily_mail_num += 1
            chk_cfg.put()


    def _chkReqArgs(self):
        chk_conf = models.CheckConfig.all()
        # '/chk/(?P<name>)',check name in table models.CheckConfig.name
        if not chk_conf.get():
            logging.info('Not set CheckConfig item,Pls set it first')
            return
        arg = self.request.path[5:]
        for entity in chk_conf.run():
            if arg == entity.name:
                return entity
        logging.info("Bad Request Url:" + self.request.path)
        #
        #self.redirect("/404.html")
        self.error(404)


    def sendNotice(self,mailto,msgs):
        sender_address = "Support" + config.SEND_ADDR
        user_address = mailto
        subject = "[Sec][Notice]: Some Vulnerability Submited"

        context_body   = ''
        i = 1
        for item in msgs:
            context_body += str(i) + '.  ' + item.title + '\n'
            context_body += item.link + '\n\n'
            i += 1

        context  =  config.MAIL_CONTEXT_HEADER + context_body + config.MAIL_CONTEXT_FOOTER
        try:
            mail.send_mail(sender_address, user_address, subject, context)
        #InvalidSenderError: Unauthorized sender
        except mail.InvalidSenderError:
            logging.error("InvalidSenderError")

#*********************  process site Data ******************************

class chkWooyunSubmitRSS():

    def __init__(self,url):
        self.url = url
        #self.keyword = keyword
        #self.chk_id = chk_id

    def fetchData(self):
        if 'http' not in self.url:
            self.url = 'http://'+self.url
        try:
            req = urlfetch.fetch(self.url)
        except :
            logging.error("fetch data error.can't download")
            return none
        # save chk status in AppConfig.last_get_status
        if req.status_code == 200:
            logging.info("fetch info status OK.")
            rss_dom = parseString(req.content)
            items = self._parseWooyunRss(rss_dom)
            return items

    def _parseWooyunRss(self,dom):
        items = dom.getElementsByTagName('item')
        items_list = []
        for item in items:
            tag_list = ['link','title','description','pubDate','author','guid']
            items_list.append(self._getItemDict(item,tag_list))

        return self._formatWooyun(items_list)

    def _getItemDict(self,item,list):
        dict = {}
        for tag in list:
            node = item.getElementsByTagName(tag)[0]
            dict[tag] = node.childNodes[0].data

        return dict

    def _formatWooyun(self,items):
        # pease description info in item.items  is dict.
        for dict in items:
            dict['guid'] = dict['guid'].rsplit('/',1)[1]
            ss = dict['description']
            p1 = u'(?<=简要描述：</strong><br/>)(?P<desc>.*)(?=<br/><strong>详细).*'
            p2 = u'(?<=说明：</strong><br/>)(?P<detail>.*)(?=<br/><br/>).*'
            pn = re.compile(p1+p2,re.M|re.S)
            tmp = pn.search(ss)
            if tmp :
                tmp_dict = tmp.groupdict()
                for key in tmp_dict.keys():
                    dict[key] = tmp_dict[key]

                logging.info("wooyun rss description item format ...")
        return items


    def saveData(self,msgs,last_save_id):
        if not msgs:
            logging.info("Nothing to be save!")
            return False
        last_save_guid = self._getGuidData(last_save_id)
        if not last_save_guid:
            logging.error("get last save ")
        repeat = True
        save_id = last_save_id + 1

        for msg in msgs:
            dt = datetime.strptime(msg['pubDate'],'%a, %d %b %Y %H:%M:%S +0800')
            if not msg.has_key('desc'):
                msg['desc']   = msg['description']
                msg['detail'] = ''
                logging.info("Not have key desc,Pls check re.")
            if msg['guid'] in last_save_guid:
                    break
            logging.info("desc == %s" % msg['desc'])
            item=models.WooyunSubmitData(guid=msg['guid'],link=msg['link'],title=msg['title'],
                                         desc=msg['desc'],author=msg['author'],pub_date=dt,
                                         detail=msg['detail'],save_id =save_id)
            item.put()
            logging.info("A Info Data store in DB.")
            repeat = False
        return not repeat

    def _getGuidData(self,num):
        wooyun_data = models.WooyunSubmitData.all()
        guid_list = []
        wooyun_data.filter("save_id =",num)
        for item in wooyun_data.run():
            guid_list.append(item.guid)
        return guid_list

    def checkKeyWord(self,chk_id,keywords):
        wooyun = models.WooyunSubmitData.all()
        notice  = []
        if keywords:
            keywords = keywords.replace('，',',').split(',')
        wooyun.filter('save_id >',chk_id)
        for item in wooyun.run():
            if not keywords or self._hasKey(item,keywords):
                notice.append(item)
        return notice

    def _hasKeyword(self,item,keywords):
        for key in keywords:
            if key in item.desc:
                return True
        return False

#********************* start WSGI  ******************************
#urls =[]
#urls.add('/', indexHandler)

app = webapp.WSGIApplication([('/', indexHandler),
                              ('/chk/.*', chkHandler),
                              (config.INIT_DB_URL, init_dbHandler),
                              ('/reset/daily',resetHandler),
				       ], debug=True)

if __name__ == '__main__':
    run_wsgi_app(app)
