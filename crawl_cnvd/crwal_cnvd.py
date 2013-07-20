#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#---
# project:     crawl_cnvd
# Purpose:     format report from other security tools.
# Author:      hufuyu@gmail.com
# Licence:     BSD
#---

import os
import sqlite3
import urllib
import logging
import re


#http://www.cnvd.org.cn/flaw/listResult?startDate=&endDate=&max=100&offset=0

class CnvdSpider():

    def init(self,db_file):
        self.db = db_file

    def initDB(self):
        con = sqlite3.connect(self.db)
        cur = con.cursor()

        try:
            cur.execute("""
            CREATE TABLE  CNVD_flaw (
            cnvd_id     varchar(32) primary key,
            title       varchar(256),
            url         varchar(256),
            pubdate     varchar(32),
            rank        varchar(32),
            rank_detail varchar(64),
            products    varchar(64),
            bugtraq_id  interge,
            flaw_desc   varchar(),
            res_url     varchar(),
            fix_desc    varchar(),
            discover    varchar(),
            patch_title varchar(),
            patch_url   varchar(),
            renew_time  date(),
             )""")
            cur.execute("""
            CREATE TABLE  CNVD_patch (
            cnvd_id     varchar(32) primary key,
            title       varchar(256),
            url         varchar(256),
            desc        varchar(),
            attr_file   varchar(),
            stauts      varchar(),
            save_date   date(),
             )""")
        except sqlite3.OperationalError :
            pass
        con.commit()


    def crawl(self,start_url):
        wp = self.fetchDate(start_url)
        fetch_urls = []
        retry_urls = []
        if not wp :
            logging.error("Can't fetch data from start_url, Pls Check!")
            return
        else:
            data = self.parseFlawPage(wp)
            count = data['coount']

        #gen urls  to fetch.
        #flaw list data
        for i in range(1,count/100):
            url = start_url[:-1] + str(100*i)
            wp = self.fetchDate(url)
            if wp:
                flawdata = self.parseFlawPage(wp)
                if flawdata['count']  != count:
                    logging.error('site add some data, Pls check.')
                self.saveFlawData(flawdata)
            else:
                logging.info("Fetch data Failed: " + url)
                retry_urls.append(url)

        #process retry url

        #flaw data

        #gen urls for patch
        urls = ''
        for url in urls :
            url = 'http://www.cnvd.org.cn/' + url
            wp = self._fetchDate(url)
            if wp:
                patchdata = self.parsePatchPage(wp)
                self.savePatchData(patchdata)
            else:
                logging.info("Fetch data Failed: " + url)
                retry_urls.append(url)


    def _fetchDate(self,url):
        try:
            req = urllib.urlopen(url)
            if req.getcode() == 200:
                page = req.read()
                req.close()
                return page
            else:
                return None
        except:
            logging.error('fetch date error: ' + url )


    def parseFlawListPage(self,page):
        data = []

        s1 = ''
        s0 = '(?<=共&nbsp;)\s+(?P<count>\d+).*'


    def saveFlawData(self,flawdata):
        pass

    def parsePatchPage(self,page):
        pass

    def savePatchData(self,patchdata):
        pass

if __name__ == '__main__':
    db_file = os.path.dirname(__file__) + '/' + "cnvd.db"
    sp = CnvdSpider(db_file)
    sp.initDB()
    sp.crawl()
