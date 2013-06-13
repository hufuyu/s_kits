#!/usr/bin/python3

#-------------------------------------------------------------------------------
# Name   :     SecReport_format.py
# Purpose:     format report from other security tools.
# Version:     v0.1.2-20130609
# Author:      hufuyu@gmail.com
# Created:     09/06/2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os,re,sqlite3

def parseReport(txt,db_cur):
    # check file size,if too large, skip:
    try:
        f=open(txt,'r')
    except IOError:
        print("--- Error ---")
        return ''
    rp=f.read()
    f.close()

    scan_info = parseScanInfo(rp)
    if scan_info :
        si = (scan_info['name'],scan_info['start'],scan_info['end'],scan_info['banner'],scan_info['OS'],scan_info['tech'])
        db_cur.execute('INSERT INTO Target VALUES (NULL,?,?,?,?,?,?)',si)
        #print(db_cur.execute('SELECT * FROM Target').fetchall())
    else:
        return None
    sum_info = parseSummary(rp)
    if sum_info :
        print("+++++ \n",sum_info)
        for (threat,path) in sum_info :
            db_cur.execute('INSERT INTO Summary VALUES (NULL,?,?,?)',(scan_info['name'],threat,path))
    else:
        return None
    #print(db_cur.execute('SELECT * FROM Summary').fetchall())

def parseScanInfo(report):
    '''
    (?=Scan +of).*(?=Threat +level)
    '''
    p = re.compile(r'(?=Scan of).*(?=Threat level)',re.M|re.S)
    m = p.search(report)
    if not m :
       return None
    si = m.group(0)
    #print('+++++  ',si)
    '''
    si='Scan of http://180.166.38.49\nScan details\n\nScan information\nStart time             2013/5/19 19:31:13\nFinish time            2013/5/19 19:35:12\nScan time              3 minutes, 59 seconds\nProfile                Default\n\nServer information\nResponsive             True\nServer banner          Apache/2.2.16 (Debian)\nServer OS              Unix\nServer technologies\n\n\n'
    '''

    #rep =r'(?<=Scan of)\s+(?P<name>.*)\s+(?=Scan details).*(?<=Start time)\s+(?P<start>.*).*(?<=Finish time)\s+(?P<end>.*)\s+(?=Scan time).*(?<=Server banner)\s+(?P<banner>.*).*(?<=Server OS)\s+(?P<OS>.*).*(?<=Server technologies)\s+(?P<tech>.*).*'
    
    s1 = '(?<=Scan of)\s+(?P<name>.*)\s+(?=Scan details).*'
    s2 = '(?<=Start time)\s+(?P<start>.*)\s+(?=Finish time).*'
    s3 = '\s+(?P<end>.*)\s+(?=Scan time).*'
    s4 = '(?<=Server banner)\s+(?P<banner>.*)\s+(?=Server OS).*'
    s5 = '\s+(?P<OS>.*)\s+(?=Server technologies).*'
    s6 = '\s+(?P<tech>.*).*'
    #rep ="r'" + s1 + s2 + s3 + s4 + s5 + s6 + "'" 
    rep =s1 + s2 + s3 + s4 + s5 + s6
    
    p1=re.compile(rep,re.M|re.S)
    scan_info=p1.search(si)
    print(scan_info)

    if scan_info :
        return scan_info.groupdict()
    return scan_info

def parseSummary(report):
    '''
    return dict.
    '''
    p = re.compile(r'(?<=Alerts summary).*(?=Alert details)',re.M|re.S)
    m = p.search(report)
    if not m :
       return None
    ss = m.group(0)

    # remove page footer.
    p1 = re.compile(r'Acunetix Website Audit\s+\d+',re.M|re.S)
    ss = re.sub(p1,'',ss)

    # change "/test.php    s\n  1"  to "/test.php    1"
    p2 = re.compile(r'\s+s\s+(?=\d)',re.M|re.S)
    ss = re.sub(p2,'',ss)

    #remove space char
    p3 = re.compile(r'^\s+|(?<=\n)\s+',re.M|re.S)
    ss = re.sub(p3,'',ss)
    p4 = re.compile(r'Affects\s+Variation',re.M|re.S)
    va = 'Affects Variation'
    ss = re.sub(p4,va,ss)

    ss=ss.splitlines()
    i=0
    rst=[]
    tmp=''

    while( i < len(ss) -1):
        if va in ss[i+1]:
            tmp=ss[i]
            i+=2
        else:
            i +=1
            #print(i,' : ',ss[i])
            rst.append((tmp,ss[i]))
    rst.append((tmp,ss[-1]))
    return rst

def pdf2txt(rp_dir):
    pdf_fs = listFiles(rp_dir,'.pdf')
    print(pdf_fs)
    
    for pdf_f in pdf_fs:
        txt_fn = os.path.splitext(pdf_f)[0] + '.txt'
        dir= os.path.dirname(pdf_f)
        # if exist text file, parse it! Converse PDF to text as same name.
        if  not os.path.exists(txt_fn):
            cmd = 'pdftotext -layout '+ pdf_f +' ' + txt_fn
            os.system(cmd)
    print(listFiles(rp_dir,'.txt'))

def listFiles(dir,ext):
    fn_list = []
    
    for root, dirs, files in os.walk(dir):
        for name in files:
            if os.path.splitext(name)[1] == ext:
                fn=os.path.join(root, name)
                fn_list.append(fn)
    return fn_list

def main():
    db  = "/home/data/tmp/report.db"
    #db = 'D:/test/report.db'
    con = sqlite3.connect(db)
    cur = con.cursor()

    try:
        cur.execute("""
        CREATE TABLE  Target (
        id      integer primary key autoincrement,
        name    varchar(128),
        start   varchar(64),
        end     varchar(64),
        banner  varchar(256),
        OS      varchar(128),
        tech    varchar(256)
        )""")

        cur.execute("""
        CREATE TABLE  Summary (
        id          integer primary key autoincrement,
        target      varchar(128),
        threat      varchar(64),
        path        varchar(64)
        )""")
    except sqlite3.OperationalError :
        pass


    #rf = 'D:/test/report.txt'
    #pdf2txt()
    #try:
    rp_path = '/home/data/tmp/ssss/'
    for rf in listFiles(rp_path,'.txt'):
        print('---       ',rf,'         ---')
        parseReport(rf,cur)
        
    #finally:
    con.commit()
    con.close()

if __name__ == '__main__':
    main()
