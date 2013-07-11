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
import datetime
import models

from google.appengine.api import mail
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import db

from xml.dom.minidom import parseString

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

class setupHandler(webapp.RequestHandler):

  def get(self):
        chk_conf = models.CheckConfig.all()
        if not chk_conf.get():
            try:
                ck_wooyun = models.CheckConfig(name ='test',site_type='wooyun_submit',
                                        last_chk_id = 0,notice=True,mail_to='natthun@gmail.com',
                                        )
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
        chk_cfg = self._chkReqArgs()
        if not chk_cfg:
            self.error(404)
            return

        res_pool = models.ResPool.all().filter('site_type =',chk_cfg.site_type).get()

        if not res_pool:
            logging.error('site_type not set in ResPool,Pls chk < %s >' % chk_cfg.site_type)
            self.error(404)
            return

        for res in res_pool:
            # check gap, if need fetch data

            # fetch data  and save
            if res.site_type == 'wooyun_submit':
                chk_wooyun = chkWooyunSubmitRSS(chk_cfg.url,chk_cfg.key_words)
                msgs = chk_wooyun.fetchInfo()
            # save data: get last saved data.  delete repeat.
            #getData('WooyunSubmitData',res.last_save_id)
            #    chk_wooyun.saveData(msgs,res.last_save_id + 1)
            #    res.last_save_id += 1
            #    res.put()
            # chk data which contain keyword


        if appcfg.notice and msgs:
            logging.info("prepare send notice ...")
            self.sendNotice(chk_cfg.mail_to,'Wooyun',msgs)
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.out.write("mail send!")

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

    def checkKeyWord(self,msgs):
        pass

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
            return items

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
            p1 = u'(?<=简要描述：</strong><br/>)(?P<desc>.*)(?=<br/><strong>详细).*'
            p2 = u'(?<=说明：</strong><br/>)(?P<status>.*)(?=<br/><br/>).*'
            pn = re.compile(p1+p2,re.M|re.S)
            tmp = pn.search(ss)
            if tmp :
                tmp_dict = tmp.groupdict()
                for key in tmp_dict.keys():
                    dict[key] = tmp_dict[key]
                logging.info("wooyun rss description item format ...")
        #    print(ss)
        return items


    def saveData(self,msgs):
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
#urls =[]
#urls.add('/', indexHandler)

app = webapp.WSGIApplication([('/', indexHandler),
                              ('/chk/.*', chkHandler),
                              ('/setup', setupHandler),
				       ], debug=True)

if __name__ == '__main__':
    run_wsgi_app(app)
