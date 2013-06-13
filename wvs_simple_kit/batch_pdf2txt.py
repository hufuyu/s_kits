#!/usr/bin/python


import os

def main():
    rp_dir = '/home/data/tmp/awvs-scan-result/'
    pdf_fs = listFiles(rp_dir,'.pdf')
    print pdf_fs
    
    for pdf_f in pdf_fs:
        txt_fn = os.path.splitext(pdf_f)[0] + '.txt'
        dir= os.path.dirname(pdf_f)
        # if exist text file, parse it! Converse PDF to text as same name.
        if  not os.path.exists(txt_fn):
            cmd = 'pdftotext -layout '+ pdf_f +' ' + txt_fn
            os.system(cmd)
    print listFiles(rp_dir,'.txt')
    
def listFiles(dir,ext):
    fn_list = []
    
    for root, dirs, files in os.walk(dir):
        for name in files:
            if os.path.splitext(name)[1] == ext:
                fn=os.path.join(root, name)
                fn_list.append(fn)
    return fn_list
    
if __name__ == '__main__':
    main()
