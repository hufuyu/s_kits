#!/usr/bin/python
# coding: utf-8

#
#  1. private  fm
#  2. cache
#  3. signal  [ paulse \ next \ favorite \ drop]
#
 
 
 import httplib
 import json
 import os
 import sys
 import subprocess
 import time
 
 
 class DoubanFM():
     
     
 
 
 while True:
     # get list
     httpConnection = httplib.HTTPConnection('douban.fm')
     httpConnection.request('GET', '/j/mine/playlist?type=n&channel=0')
     song = json.loads(httpConnection.getresponse().read())['song']
 
     picture = 'images/' + song[0]['picture'].split('/')[4]
 
     # get picture

 
 
     # Play
     player = subprocess.Popen(['mplayer', song[0]['url']])
     time.sleep(song[0]['length'])
     player.kill()
     
     
if __name__ == '__main__':
     play = DoubanFM() 
