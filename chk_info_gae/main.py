#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#---
# project:     chk-info-gae
# Purpose:     format report from other security tools.
# Author:      hufuyu@gmail.com
# Licence:     BSD
#---
#   todo:
#           *  add  search
#           *  add  task queue
#           *  add  new URL to check
#   ver 0.5-20130720
#           *  change process. refresh ResPool at time. change cron.
#   ver 0.4-20130719
#           *  spilt fetch data OP & chk OP, user  bootstrap , handle data.
#   ver 0.3-20130711
#           *  fix bugs: save every hour/ wooyun[description] re error.
#   ver 0.1-20130706
#           *  just run...  very simple.
#---

import logging
import re
import os
from xml.dom.minidom import parseString
from datetime import datetime

import config
import models

import jinja2
import webapp2 as webapp
from google.appengine.api import mail
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import db

#********************* handle URL ******************************
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])


class indexHandler(webapp.RequestHandler):

    def get(self):
        #path = os.path.join(os.path.dirname(__file__), 'static/tpl/base.html')
        #self.response.write(template.render(path))
        template = JINJA_ENVIRONMENT.get_template('static/tpl/base.html')
        self.response.write(template.render())

class loginHandler(webapp.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('static/tpl/login.html')
        self.response.write(template.render())

class chk_itemHandler(webapp.RequestHandler):

    def get(self):
        # if method == 'add':
        template = JINJA_ENVIRONMENT.get_template('static/tpl/add_chk_item.html')
        self.response.write(template.render())

    def post(self):
        if self.request.get('Name') and  self.request.get('SiteType'):
            #bug: Not check.
            isNotice  = self.request.get('isNotice')
            keywords  = self.request.get('KeyWords').replace(u'，',u',')
            try:
                ck_wooyun = models.CheckConfig(name =self.request.get('Name'),site_type=self.request.get('SiteType'),
                                        last_chk_id = config.DB_INIT_SAVE_ID,notice=True,
                                        mail_to=self.request.get('Emails'),key_words=keywords,
                                        since=datetime.now())
                ck_wooyun.put()
            except db.BadValueError:
                logging.error("add data error")
                return
            logging.info("add chk_config:" + isNotice)
        else:
            self.redirect('/am/chk/add')

class init_dbHandler(webapp.RequestHandler):

    def get(self):
        chk_conf = models.CheckConfig.all()
        if not chk_conf.get():
            try:
                for cfg_data in config.DB_INIT_CHECKCONFIG:
                    logging.info(cfg_data['name'] + cfg_data['site_type'] + cfg_data['mail_to'] + cfg_data['key_words'])
                    ck_wooyun = models.CheckConfig(name =cfg_data['name'],site_type=cfg_data['site_type'],
                                        last_chk_id = config.DB_INIT_SAVE_ID,notice=True,mail_to=cfg_data['mail_to'],
                                        key_words =cfg_data['key_words'],since=datetime.now())
                    ck_wooyun.put()
                for res_data in config.DB_INIT_RESPOOL:
                    res_wooyun = models.ResPool(site_type=res_data['site_type'],url=res_data['url'],
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

class dailyHandler(webapp.RequestHandler):

    def get(self):
        # reset daily number: CheckConfig.daily_mail_num
        chk_conf = models.CheckConfig.all()
        if chk_conf.get():
            for item in chk_conf.run():
                item.daily_mail_num = 0
                item.put()
            logging.info('Daily  statistics data reset to 0.')
        else:
            logging.info('Nothing find CheckConfig. maybe need check.')
        # send a summary email which keyword is null.
        chk_config = models.CheckConfig.all()
        if chk_config.get():
            for chk_cfg in chk_config.run():
                # if send everyone a email,commit next line.add other mark.
                if not chk_cfg.key_words:
##                    self.redirect('/chk/' + item.name)
                    res_pool = models.ResPool.all().filter('site_type =',chk_cfg.site_type)
                    for res in res_pool:
                        chkHandler().chk_keywords(chk_cfg,res)
        else:
            logging.info("No need send a summary mail")

class resHandler(webapp.RequestHandler):

    def get(self):
        res = self._chkReqArgs()
        # fetch data  and save
        if not res:
            return
        if res.site_type == 'wooyun_submit':
            chk_wooyun = chkWooyunSubmitRSS(res.url)
            msgs = chk_wooyun.fetchData()
            if not msgs:
               return
                # save data: get last saved data.  delete repeat.
            saved = chk_wooyun.saveData(msgs,res.last_save_id)
                # if save date, update ResPool.last_save_id
            if not saved:
                logging.info("Nothing saved")
                return
            res.last_save_id += 1
            res.put()

        chk = models.CheckConfig.all().filter('site_type =',res.site_type)
        if chk.get():
            for item in chk.run():
                if item.key_words and item.name:
                    logging.info('Lisk check /chk/' + item.name)
                    # maybe bug: confirm bug.
                    #self.redirect('/chk/' + item.name)
                    res_pool = models.ResPool.all().filter('site_type =',item.site_type)
                    for res in res_pool:
                        chkHandler().chk_keywords(item,res)
        else:
            logging.info('No Need check [' + site +'],Pls set it first')

    def _chkReqArgs(self):
        arg = self.request.path[5:]
        if arg :
            chk_res = models.ResPool.all().filter('site_type =',arg)
            # '/res/(?P<name>)',check name in table models.ResPool.name
            if not chk_res.get():
                logging.info('Not init ResPool,Pls set it first')
                return

            for entity in chk_res.run():
                return entity
        else:
            logging.info("Bad Request Url:" + self.request.path)
            #
            #self.redirect("/404.html")
            self.error(404)

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
            #if chk_cfg.key_words:
            self.chk_keywords(chk_cfg,res)

    def chk_keywords(self,chk_cfg,res):
            # chk data which contain keyword
        if chk_cfg.last_chk_id < res.last_save_id:
            key_msgs = chkWooyunSubmitRSS().checkKeyWord(chk_cfg.last_chk_id,chk_cfg.key_words)
            chk_cfg.last_chk_id = res.last_save_id
            chk_cfg.put()
            logging.info("Chk_id renew.")
        else:
            key_msgs = None

        if chk_cfg.notice and key_msgs:
            logging.info("prepare send notice ...")
            if not chk_cfg.mail_to:
                logging.error("Notice Email Address is Null,Pls check.")
                return
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
        sender_address = "Support<" + config.SEND_ADDR +">"
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
        except mail.InvalidSenderError,mail.InvalidEmailError:
            logging.error("InvalidSenderError or Invalid Email Address Error")

#*********************  process site Data ******************************

class chkWooyunSubmitRSS():

    def __init__(self,url=""):
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
            return None
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

                #logging.info("wooyun rss description item format ...")
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
            #logging.info("A Info Data store in DB.")
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
        wooyun = models.WooyunSubmitData.all().filter('save_id >',chk_id)
        notice  = []
        if keywords:
            # replace ',' before saved
            keywords = keywords.split(',')
        for item in wooyun.run():
            if not keywords or self._hasKeyword(item,keywords):
                notice.append(item)

        return notice

    def _hasKeyword(self,item,keywords):
        for key in keywords:
            if key in item.title or key in item.desc:
                logging.info("Find Key word")
                return True
        return False

#********************* start WSGI  ******************************
#urls =[]
#urls.add('/', indexHandler)

app = webapp.WSGIApplication([('/', indexHandler),
                              ('/chk/.*', chkHandler),
                              ('/res/.*', resHandler),
                              (config.INIT_DB_URL, init_dbHandler),
                              ('/am/daily',dailyHandler),
                              ('/am/login',loginHandler),
                              ('/am/chk/add',chk_itemHandler),
				       ], debug=True)

if __name__ == '__main__':
    run_wsgi_app(app)
