#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#---
# project:     send_mail_rpt
# Purpose:     format report from other security tools.
# Author:      hufuyu@gmail.com
# Licence:     BSD
#---

# bug: sent_time  Not use!
# bug: files not in one directory

import os
import sys
import ConfigParser
import smtplib
import mimetypes

from datetime import datetime
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.MIMEAudio import MIMEAudio
from email.MIMEImage import MIMEImage
from email.Encoders import encode_base64

def main():
    cfg = ConfigParser.ConfigParser()
    if not os.path.exists('config.ini'):
        playNotice('error')
        print "Can't find config file,PLs check..."
        exit
    try:
        cfg.read('config.ini')
    except ConfigParser.ParsingError:
        playNotice('error')
        print "Read config file Error,PLs check config.ini ..."
        exit

    tasks = chk_tasks(cfg)
    if tasks:
        for task in tasks:
            if send_mail(cfg,task):
                post_send(cfg,task)

    playNotice('error')
    print "there is nothing to run,PLs chk ..."


def chk_tasks(config):
    # chk which task should run
    tasks_name = config.sections()
    tasks_name.remove('global')
    # chk 1 : in the time range
    # chk 2 : file exise.
    if not tasks_name:
        print "No Available task"
        return None

    for task in tasks_name:
        if not os.path.exists(config.get(task,'ext_file_dir')):
            tasks_name.remove(task)
    return tasks_name


def send_mail(config,task):
    # construct Mail Message Part
    msg = MIMEMultipart()
    try:
        msg['From'] = config.get('global','SEND_ADDR')
        msg['To'] = config.get(task,'send_to')
        msg['Subject'] = config.get(task,'mail_subject')
        msg.attach(MIMEText(config.get(task,'mail_context')))
        filelist = config.get(task,'ext_file_name').split(',')
    except ConfigParser.NoOptionError:
        print "Config file error,some section not None."
        exit

    for filename in filelist:
        msg.attach(getAttachment(config.get(task,'ext_file_dir')+filename))

    # Connect Server and Send mail
    try:
        smtp = smtplib.SMTP(config.get('global','SMTP_ADDR'),int(config.get('global','SMTP_PORT')))
    except Exception, errmsg:
        print "connect SMTP server error. retry?"
        return None

    if config.get('global','STARTTLS') == 'True':
        smtp.ehlo()
        smtp.starttls()
    smtp.ehlo()
    try:
        smtp.login(config.get('global','SEND_ADDR'), config.get('global','SMTP_PSWD') )
        smtp.sendmail(config.get('global','SEND_ADDR'), config.get(task,'sent_to'), msg.as_string())
    except:
        print "Error：Sent mail failed"
        return False
    smtp.close()
    return True

def post_send(config,task):
    # rename files name. add "-send" mark.
    dir = config.get(task,'ext_file_dir')
    for file in config.get(task,'ext_file_name'):
        (filename,extname)=os.path.splitext(file)
        os.rename(dir+file,dir+filename+'-send.'+extname)

def playNotice(sound):
    if os.name == 'nt':
        import winsound

def getAttachment(attachmentFilePath):
    if not os.path.exists(attachmentFilePath):
        print "ERROR: bad attachment file path, Pls check :  %s " % attachmentFilePath
        return None

    contentType, encoding = mimetypes.guess_type(attachmentFilePath)

    if contentType is None or encoding is not None:
        contentType = 'application/octet-stream'

    mainType, subType = contentType.split('/', 1)
    file = open(attachmentFilePath, 'rb')

    if mainType == 'text':
        attachment = MIMEText(file.read())
    elif mainType == 'message':
        attachment = email.message_from_file(file)
    elif mainType == 'image':
        attachment = MIMEImage(file.read(),_subType=subType)
    elif mainType == 'audio':
        attachment = MIMEAudio(file.read(),_subType=subType)
    else:
        attachment = MIMEBase(mainType, subType)
    attachment.set_payload(file.read())
    encode_base64(attachment)

    file.close()

    attachment.add_header('Content-Disposition', 'attachment',   filename=os.path.basename(attachmentFilePath))
    return attachment


if __name__ == '__main__':
    main()