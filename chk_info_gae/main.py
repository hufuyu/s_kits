#!/usr/bin/env python2
# coding: utf-8

#---
# project:     chk_news
# Purpose:     format report from other security tools.
# Author:      hufuyu@gmail.com
# Licence:     BSD
#---
#   ver 0.1-20130706
#           :  just run...  very simple.
#
#---

import logging
import re
import webapp2 as webapp

import appDB

from google.appengine.api import mail
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import db

from xml.dom.minidom import parseString

#********************* handle URL ******************************

class indexHandler(webapp.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if user:
            logging.info(user.email())
        else:
            logging.info('No User!')

class setupHandler(webapp.RequestHandler):

  def get(self):
        chk_conf = models.CheckCfg.all()
        if not chk_conf.get():
            try:
                ck_wooyun = models.CheckCfg(name ='test',site_type='wooyun_submit',
                                        last_chk_id = 0,notice=True,mail_to='natthun@gmail.com',
                                        last_get_status='200',last_chk_id=0)
                ck_wooyun.put()
                res_wooyun = models.ResPool(site_type='wooyun_submit',url='www.wooyun.org/feeds/submit',
                                            last_get_status='200',last_save_id=0)
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

class chkHandler(webapp.RequestHandler):

    def get(self):
        appcfg = self._chkReqArgs()
        if not appcfg:
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.out.write("bad request or other reason!")
            return

        if appcfg.site_type == 'wooyun_submit':
            msgs = chkWooyunSubmitRSS(appcfg.url,appcfg.key_words).fetchInfo()
        if appcfg.notice and msgs:
            logging.info("prepare send notice ...")
            self.sendNotice('natthun@gmail.com','Wooyun',msgs)
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.out.write("mail send!")

    def _chkReqArgs(self):
        sysconf = models.AppConfig.all()
        # '/chk/(?P<name>)',check name in table models.AppConfig.name
        if not sysconf.get():
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.out.write("Nothing to be check,Pls set frist!")
            return
        arg = self.request.path[5:]
        for entity in sysconf.run():
            if arg == entity.name:
                return entity
        logging.info("Bad Request Url:" + self.request.path)
        #
        #self.redirect("/404.html")
        self.error(404)

    def sendNotice(self,mailto,site,msgs):
        sender_address = "Support <hufuyu@gmail.com>"
        user_address = mailto
        subject = "[Sec][Notice]: Some Vulnerability Submited @ %s" % site

        context_header = """
Dear user:
There are some vuln discovered by somebody. please check as soon as
possible. the summary info are blow:

        """

        context_body   = ''
        i = 1
        for item in msgs:
            context_body += str(i) + '.  ' + item['title'] + '\n'
            context_body += item['link'] + '\n\n'
            i += 1

        context_footer = """

This email send automate.No longer interested in receiving these emails?,
Pls contact ...
        """

        context  =  context_header + context_body + context_footer
        try:
            mail.send_mail(sender_address, user_address, subject, context)
        #InvalidSenderError: Unauthorized sender
        except mail.InvalidSenderError:
            logging.error("InvalidSenderError")

#*********************  process site Data ******************************

class chkWooyunSubmitRSS():

    def __init__(self,url,keyword):
        self.url = url
        self.keyword = keyword

    def fetchInfo(self):
        if 'http' not in self.url:
            self.url = 'http://'+self.url
        #try:
        req = urlfetch.fetch(self.url)
        # save chk status in AppConfig.last_get_status
        if req.status_code == 200:
            logging.info("fetch info status OK.")
            rss_dom = parseString(req.content)
            items = self._parseWooyunRss(rss_dom)
            self.saveItem(items)
            self.notice_msgs = self.checkKeyWord(items)
            return self.notice_msgs

    def _parseWooyunRss(self,dom):
        items = dom.getElementsByTagName('item')
        items_list = []
        for item in items:
            tag_list = ['link','title','description','pubDate','author','guid']
            items_list.append(self._getItemDict(item,tag_list))

        return self._formatWooyunDesc(items_list)

    def _getItemDict(self,item,list):
        dict = {}
        for tag in list:
            node = item.getElementsByTagName(tag)[0]
            dict[tag] = node.childNodes[0].data

        return dict

    def _formatWooyunDesc(self,items):
        # pease description info in item.items  is dict.
        for dict in items:
            ss = dict['description']
            p1 = '(?<=简要描述：</strong><br/>)(?P<desc>.*)(?=<br/><strong>详细).*'
            p2 = '(?<=说明：</strong><br/>)(?P<status>.*)(?=<br/><br/>).*'
            pn = re.compile(p1+p2,re.M|re.S)
            tmp = pn.search(ss)
            if tmp :
                tmp_dict = tmp.groupdict()
                for key in tmp_dict.keys():
                    dict[key] = tmp_dict[key]
                logging.info("Info item format ...")
        #    print(ss)
        return items

    def checkKeyWord(self,msgs):
        # item dict
        notice  = []
        if not self.keyword:
            return msgs
        # change zh_CN charter (，)
        keylist = self.keyword.replace('，',',').split(',')
        for item in msgs:
            flag = 0
            for key in keylist:
                # try: dict has key['desc']
                if key in item['desc']:
                    flag =1
                    break
            if flag:
                notice.append(item)
        return notice

    def saveItem(self,msgs):
        for msg in msgs:
            guid = msg['guid'].rsplit('/',1)[1]
            if not msg.has_key('desc'):
                msg['desc'] = msg['description']
                msg['status'] = "ERROR!chk re"
            item=models.WooyunSubmitData(guid=guid,link=msg['link'],title=msg['title'],
                                        desc=msg['desc'],author=msg['author'],status=msg['status'])
            item.put()
        logging.info("Info store in  DB.")

#********************* start WSGI  ******************************

app = webapp.WSGIApplication([('/', indexHandler),
                              ('/chk/.*', chkHandler),
                              ('/setup', setupHandler),
				       ], debug=True)

if __name__ == '__main__':
    run_wsgi_app(app)
