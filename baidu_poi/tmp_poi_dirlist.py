__author__ = 'huafeng'
#coding:utf-8
import os
import time
import json
import glob
def batch_file_to_packet():
    # file_list = os.listdir('/home/ferrero/cloudinn/filtered_unmatch_sentence/prebuild_packet')
    file_pattern = '/home/ferrero/cloudinn/filtered_unmatch_sentence/prebuild_packet/*.packet'
    file_list = glob.glob(file_pattern)
    print json.dumps(file_list)#将返回数据封装为json格式，供fab进行解析
batch_file_to_packet()
