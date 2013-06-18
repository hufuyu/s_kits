#!/usr/bin/python
# coding: utf-8

#+++++++++++++++++++++++++++++++++++++++++++++++++++++
#
#   1. add  private fm
#   2. add  cache
#   3. signal  system [ paulse \ next \ favorite \ drop ]
#-----------------------------------------------------


 import httplib
 import json
 import os
 import sys
 import subprocess
 import time
 
 reload(sys)
 sys.setdefaultencoding('utf-8')
 
 while True:
     # 获取播放列表
     httpConnection = httplib.HTTPConnection('douban.fm')
     httpConnection.request('GET', '/j/mine/playlist?type=n&channel=0')
     song = json.loads(httpConnection.getresponse().read())['song']
 
     picture = 'images/' + song[0]['picture'].split('/')[4]
 
     # 下载专辑封面
     if not os.path.exists(picture):
         subprocess.call([
             'wget',
             '-P',
             'images',
             song[0]['picture']])
 
     # 发送桌面通知
     subprocess.call([
         'notify-send',
         '-i',
         os.getcwd() + '/' + picture,
         song[0]['title'],
         song[0]['artist'] + '\n' + song[0]['albumtitle']])
 
     # 播放
     player = subprocess.Popen(['mplayer', song[0]['url']])
     time.sleep(song[0]['length'])
     player.kill()
