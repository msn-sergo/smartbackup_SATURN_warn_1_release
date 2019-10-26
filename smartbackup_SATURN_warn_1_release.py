# -*- coding: utf-8 -*-

import subprocess, os, shutil, smtplib, socket
import sys
import time


'''
Script for periodical cleaning of log or backup folders.
SATURN

'''

def mail_send(body, subject, from_mail):
    HOST = "192.168.0.5"
    SUBJECT = subject
    TO = "119_6@hosp13"
    FROM = from_mail
    
    text = body
     
    BODY = "\r\n".join((
        "From: %s" % FROM,
        "To: %s" % TO,
        "Subject: %s" % SUBJECT ,
        "",
        text
    ))
    
    server = smtplib.SMTP(HOST)
    server.sendmail(FROM, [TO], BODY.encode('cp1251'))
    #server.sendmail(FROM, [TO], BODY.encode('utf-8'))
    server.quit()    

def sevenzip(sevevzip_folder, src_dir, dst_dir, password, file_zipname):
    #print("Password is: {}".format(password))
    system = subprocess.Popen([sevevzip_folder, 'a', '-tzip', '-mx1', '-r', dst_dir + file_zipname, src_dir, "-p{}".format(password)])
    return(system.communicate()) 

def newname(dst_dir, file_zipname):
    today = str(time.strftime("%Y-%m-%d", time.localtime()))
    shutil.move(dst_dir + file_zipname + '.zip', (dst_dir + today + '_' + file_zipname + '.zip'))
    #os.rename(dst_dir + file_zipname + '.zip', (dst_dir +'newname_' + file_zipname + '.zip'))


def free_space(path):
        x = shutil.disk_usage(path)
        return format(x.free / 1024 / 1024 / 1024, '.0f') 

def remove(path):
    """
    Remove the file or directory
    """
    
    #if os.path.isdir(path):
        #try:
            #os.rmdir(path)
        #except OSError:
            #print ("Unable to remove folder: %s" % path)
    #else:
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        print ("Unable to remove file: %s" % path)        
 
#----------------------------------------------------------------------
def cleanup(number_of_days, dst_dir):
    """
    Removes files from the passed in path that are older than or equal 
    to the number_of_days
    """
    
    sum_del_files = 0
    size_del_files = 0
    path = dst_dir
    time_in_secs = time.time() - (number_of_days * 24 * 60 * 60)
    for root, dirs, files in os.walk(path, topdown=False):
        for file_ in files:
            full_path = os.path.join(root, file_)
            stat = os.stat(full_path)
            if stat.st_mtime <= time_in_secs:
                sum_del_files += 1
                sizeFile = os.path.getsize(full_path)
                size_del_files += sizeFile
                #print(k,  full_path)
                
                remove(full_path)
        if not os.listdir(root):
            print(root)
            #remove(root)
    return ( sum_del_files, size_del_files )

def body(subject, starttime, date_until_deleted, sum_del_files, size_del_files, file_zipname):
    a=('\n'+'-----------------------------------------------'+'\n')
    b=('\n'+"Today                                         " + str(starttime))+ '\n'
    c=("Files older {} days, was deleted, early then {} \n".format(days, date_until_deleted))+ '\n'
    d=("Total deleted --{}-- files size   :  {:.6} mb".format(str(file_zipname), str(size_del_files/1024/1024)))+ '\n'
    e=("Total number deleted --{}-- files :  ".format(str(file_zipname)) + str(sum_del_files)) + " files" + '\n'
    #f=("Total deleted empty folders:  " + str(TOTAL_DELETED_DIRS))+ '\n'
    #g=("Elapsed time               :  {:.6} sec".format(str(finishtime)))+ '\n'

    txt = (a,b,c,d,e,a)
    body=subject + ("" . join(txt))
    return body
 
    
if __name__ == "__main__":
    days= 60 # 2 month
    minDiskSpaceGB_warn = 45
    minDiskSpaceGB_alert = 30
    disk = r"\\neptun\e$"
    nowTime = time.time()
    ageTime = nowTime - (60*60*24*days)
    date_until_deleted=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ageTime))
    starttime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    time_speed_start= time.time()    
    #sevevzip_folder = 'D:\\pub\\bat\\7za.exe'
    #dst_dir = r'E:\test\dst' + '\\'
    #src_dir = r'E:\test\src'
    sevevzip_folder = 'E:\\Backup\\Dont_touch\\bat\\7za.exe'
    dst_dir = r'\\neptun\E$\backup\ares' + '\\'
    src_dir = r'E:\Backup\Ares'
    file_zipname = 'ares_fullbackup'
    password = 'asu#1494'
    
    free_space = int(free_space(disk))
    if free_space < minDiskSpaceGB_warn and free_space >= (minDiskSpaceGB_alert):
        body = str('Server {} has only {} Gb free space on disk {} \nafter disk space < {} GB all backup files, oldest {} days, will be remove.'.format(socket.gethostname(), free_space, disk, minDiskSpaceGB_alert, days))
        subject = str('Warning Server {} has only {} Gb free space on disk {}'.format(socket.gethostname(), free_space, disk))
        mail_send(body, subject, (socket.gethostname()))
        sevenzip(sevevzip_folder, src_dir, dst_dir, password, file_zipname)
        newname(dst_dir, file_zipname)
        
    elif free_space < minDiskSpaceGB_alert:
        #cleanup(days, dst_dir)
        subject = str('Alert Server {} has only {} Gb free space on disk {}'.format(socket.gethostname(), free_space, disk))
        '''
        body = str('Server {} has only {} Gb free space on disk {} \nDisk space < {} GB, all backup files will be remove to date: {clean[0]} and {clean[0]} --{zf}-- files have been deleted. Size deleted files {clean[1]} mb'.format(socket.gethostname(), free_space, disk, minDiskSpaceGB_alert, clean=cleanup(days, dst_dir), zf=file_zipname))
        '''
        clean = cleanup(days, dst_dir)
        sum_del_files = (clean[0])
        size_del_files = (clean[1])
        #txt = body (subject, starttime, date_until_deleted, sum_del_files, size_del_files)
        #print(txt)
        
        
        mail_send ((body (subject, starttime, date_until_deleted, sum_del_files, size_del_files, file_zipname)), subject, (socket.gethostname()) )
        sevenzip(sevevzip_folder, src_dir, dst_dir, password, file_zipname)
        newname(dst_dir, file_zipname)        
    
    else:
        sevenzip(sevevzip_folder, src_dir, dst_dir, password, file_zipname)
        newname(dst_dir, file_zipname)         
            
    
            
        
        
        
    #setParams(sys.argv)
    #free_space_up_to(minDiskSpace, foldersToObserve)
    #for folderToDelete in foldersToObserve:
        #deleteEmptyFolders(folderToDelete)

