#!/usr/bin/env python3
# coding: utf-8



from urllib.request import urlopen
import urllib
from xml.dom.minidom import parseString
from smtplib import SMTP
from time import sleep

import optparse
import configparser
import re

class simpleRSS():
    def __init__(self,conf):
        self.url = conf['url']
        self.keyword = conf['keyword']
        self.conf = conf

    def checkRSS(self):
        if 'http' not in self.url:
            self.url = 'http://'+self.url
        try:
            req = urlopen(self.url)
        except urllib.error.HTTPError:
            return None
        if req.status == 200:
            rss = req.readall()
        req.close()
        # parse rss if renew.
        rss_dom = parseString(rss.decode('utf-8'))
        items = self.WooyunRss(rss_dom)
        notice_msgs = self.checkKeyWord(items)
        #print("______Message Number: %n" % len(notice_msgs))
        print("_____________ RSS checked: __________")
        for msg in notice_msgs:
            print("Msg: %s @ %s" % (msg['desc'],msg['link']))

        if self.conf['notice'] == 'True':
            print("sent Notice")


    def WooyunRss(self,dom):
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
        #    print(ss)
        return items

    def checkKeyWord(self,items):
        # item dict
        notice  = []
        keylist = self.conf['keyword'].replace('，',',').split(',')
        for dict in items:
            flag = 0
            for key in keylist:
                # try: dict has key['desc']
                if key in dict['desc']:
                    flag =1
                    break
            if flag:
                notice.append(dict)
        return notice

    def _sentMail(self):
        if self.notice:
            auth = {user:'','password':''}
            smtp = SMTP()
            try:
                smtp.login(auth)
            except:
                smtp.close()
                return
            smtp.send_message(msg)
            smtp.close()

    def render_email_template(title, news):
        msg = []
        msg.append(title)
        result_str.append('%s\n' % sys_args.cmd)

        return '\n'.join(msg)

class simple_RSS(simpleRSS):

    def parseWooyunRss(dom):
        p_items = re.compile(r'(?<=<item>).*(?=</item>)',re.M|re.S)
        items = p_items.search(dom)
        if items:
            items = items.group(0).split('</item>\n<item>')
        p1 = '\s+(?<=<link>)(?P<link>.*)(?=</link>).*'
        P2 = '(?<=<title><![CDATA[)(?P<title>.*)(?=]]></title>).*'
        p3 = '(?<=<description><![CDATA[)(?P<description>.*)(?=]]></description>).*'
        p4 = '(?<=<pubDate>)(?P<pubDate>.*)(?=</pubDate>).*'
        p5 = '(?<=<guid>)(?P<guid>.*)(?=</guid>).*'
        pn = p1 + p2 + p3 + p4 + p5
        p_item = re.compile(pn,re.M|re.S)
        for item in items:
            item_dict = p_item.search(item)
            if item_dict :
                return item_dict.groupdict()

def main():
    conf = configparser.ConfigParser()
    conf.read('rss.cfg',encoding='utf-8')
    #
    #conf.sections()
    #conf[Global][refresh]

    #Parse sys_args.time
    max_time = conf['Global']['refresh']
    rp = re.compile(r'(\d+)([dhm])')
    st = rp.findall(max_time)
    sp = 0
    for(t_val, t_unit) in st:
        #Convert time to min
        if t_unit == 'd':
            sp += int(t_val)*24*60
        elif t_unit == 'h':
            sp += int(t_val)*60
        elif t_unit == 'm':
            sp += int(t_val)

    while True:
        sr=simpleRSS(conf['wooyun'])
        sr.checkRSS()
        sleep(sp*60)


if __name__ == '__main__':
    main()
