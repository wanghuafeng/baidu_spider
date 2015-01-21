__author__ = 'wanghuafeng'
#coding:utf-8
import subprocess

def exec_on_remote_server(serverName):#1000-1500
    scp_command = 'scp -r /home/huafeng/PycharmProjects/baidu_whole_music %s:~'%serverName
    IsFailed = subprocess.call(scp_command, shell=True)
    if not IsFailed:
        fab_command = 'fab -H %s -- "cd ~/baidu_whole_music; python baidu_music.py"'%serverName
        subprocess.call(fab_command, shell=True)
#控制url的抓取范围需要球该baidu_music.py的_load_all_singer_url()方法
# exec_on_remote_server('s1')#500-1000
# exec_on_remote_server('s2')#1000-1500
# exec_on_remote_server('s3')#1500-