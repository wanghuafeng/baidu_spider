__author__ = 'huafeng'
#coding:utf-8
import subprocess
import os
PATH = os.path.dirname(os.path.abspath(__file__))
import glob
scp_command = "scp mdev:/home/mdev/tmp/wanghuafeng/cities/ankang cities"
# mdev_path = '/home/mdev/tmp/wanghuafeng'

def exec_on_mdev_poi():
    '''将poi.py文件拷贝到mdev，并执行该文件'''
    scp_command = 'scp poi.py mdev:/home/mdev/tmp/wanghuafeng/'
    IsFailed = subprocess.call(scp_command, shell=True)
    if not IsFailed:
        command = 'fab -H mdev --keepalive=10 -- "cd /home/mdev/tmp/wanghuafeng/; python poi.py"'
        subprocess.call(command, shell=True)
# exec_on_mdev_poi()

def data_clean_on_mdev():
    '''在mdev上执行data_clean脚本'''
    mdev_path = '/home/mdev/tmp/wanghuafeng'
    scp_command = 'scp data_clean.py mdev:%s' % mdev_path
    print 'exectuing...: ', scp_command
    IsFailed = subprocess.call(scp_command, shell=True)
    if not IsFailed:
        command = 'fab -H mdev --keepalive=10 -- "cd {mdev_path}; python data_clean.py"'.format(mdev_path=mdev_path)
        subprocess.call(command, shell=True)
# data_clean_on_mdev()
def scp_ch_files_to_s3():
    '''拷贝所有的_ch.txt的文件到s3上'''
    remote_path = '/home/ferrero/cloudinn/filtered_unmatch_sentence/prebuild_packet'
    ch_file_path = os.path.join(PATH, 'cities_cuted', '*_ch.txt')
    file_list = glob.glob(ch_file_path)
    print len(file_list)
    scp_command = 'scp %s s3:{}'.format(remote_path)
    file_index = 0
    for filename in file_list:
        file_index += 1
        print file_index
        subprocess.call(scp_command%filename, shell=True)

def add_city_to_packet_on_s3(filename):
    '''为s3 prebuild_packet目录下所有的.packet，文件添加城市名'''
    city = filename.split('_')[0]
    remote_path = '/home/ferrero/cloudinn/filtered_unmatch_sentence'
    packet_filename = os.path.join(remote_path, 'prebuild_packet', filename)
    scp_command = 'scp tmp_add_city_to_packet.py s3:%s'%remote_path
    subprocess.call(scp_command, shell=True)
    fab_command = 'fab -H s3 --keepalive=10 -- "cd %s; python tmp_add_city_to_packet.py %s %s"'%(remote_path, packet_filename, city)
    subprocess.call(fab_command, shell=True)
filename = 'beijing_cuted_filtered_ch.packet'
add_city_to_packet_on_s3(filename)
def batch_add_city_on_s3():
    '''批量添加city'''
    import json
    remote_path = '/home/ferrero/cloudinn/filtered_unmatch_sentence'
    scp_command = 'scp tmp_poi_dirlist.py s3:%s'%remote_path
    subprocess.call(scp_command, shell=True)
    fab_command = 'fab -H s3 -- "cd %s; python tmp_poi_dirlist.py"'%remote_path
    popen = subprocess.Popen(fab_command, shell=True, stdout=subprocess.PIPE)
    return_list = popen.stdout.readlines()
    print len(return_list)
    file_list = json.loads(return_list[2].strip().split(':')[-1])
    print len(file_list), file_list[0]
    # for sentence_filename in file_list:
    #     add_city_to_packet_on_s3(sentence_filename)
# batch_add_city_on_s3()

