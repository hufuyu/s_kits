#!/usr/bin/env python
# coding: utf-8

#-------------------------------------------------------------------------------
# project:     chk_news
# Purpose:     format report from other security tools.
# Author:      hufuyu@gmail.com
# Licence:     BSD    
#-------------------------------------------------------------------------------












app = webapp.WSGIApplication([('/', indexHandler), 
                              ('/chk_rss', ChkRss_Handler), 
				       ], debug=True)

def main():
    run_wsgi_app(app)

if __name__ == '__main__':
  main()
