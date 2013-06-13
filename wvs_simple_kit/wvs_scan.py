#!python
#-*- coding:utf8 -*-
# author          : hufuyu@gmail.com
# version & date  : v1.0-20130519

'''
simply  script  for  awvs  scan  lots of site. just set sep directory.
hope its can  work.
'''
import os,datetime,time

def scan():
    awvs_path = "wvs_console.exe"
    out_path = "D:/Test/"
    list_file= out_path + "ce-list-20130518.txt"

    print("--- create work directory :")
    os.chdir(out_path)
    workdir = out_path + str(datetime.date.today())
    try:
        os.makedirs(workdir)
    except OSError:
        workdir = workdir + "-01"
        os.makedirs(workdir)

    print("---  read websites file:")
    # get website list which will be  scan.
    try:
        fp = open(list_file)
    except IOError:
        print("!!!!! Bad site list path or file error !!!!! ")
        exit()

    site_list = fp.readlines()
    fp.close()

    for site in site_list:

        # make new directory for new scan
        dir_name = workdir + "/" + site.split('/')[2]
        try:
            os.makedirs(dir_name)
        except OSError:
            dir_name = workdir + "/" + str(time.time())
            os.makedirs(dir_name)
        dir_path = dir_name + "/"
        # scan command
        awvs_cmd = awvs_path + " /Scan " + site + " /SaveFolder " + dir_path +" /Save /GenerateReport /ReportFormat pdf"
        print("---  exec cmd:  %s",awvs_cmd)

        # ~~~~~~~~~~~~~~~~~~~ Error!!!  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Maybe  this is not work at windows,change it! 
        # Single Process!  Too slow!
        
        os.system(awvs_cmd)

if __name__ == "__main__":
    scan()
