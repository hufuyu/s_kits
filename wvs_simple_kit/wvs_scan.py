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
		#由于windows不支持os.wait()，系统会不停的创建进程， 这里使用一个sets()作为一个池，控制进程的数量，
		#使用subprogress 调用外部命令完成工作
		'''
		ps = set()
		max_p = 20
		p = subprocess.Popen(cmd,stdin=None,stdout=None, shell=True)
		ps.add(p)
		while len(ps) >= max_p:
			time.sleep(0.001)#这个值如果设置得当，可以不再下面进行异常捕获的操作
			try:
				ps.difference_update(d for d in ps if d.poll() is not None)
			except:
				pass
        '''
        os.system(awvs_cmd)

if __name__ == "__main__":
    scan()
