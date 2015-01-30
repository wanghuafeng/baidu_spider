__author__ = 'huafeng'
#coding:utf-8
import sys
import subprocess
import time
import glob
import codecs
import os
import re
PATH = os.path.dirname(os.path.abspath(__file__))

def combine_files():
    file_pattern = os.path.join(PATH, 'data', '*.txt')
    total_line_set = set()
    file_list = glob.glob(file_pattern)
    print 'length of file_list is: ', len(file_list)
    file_index = 0
    for filename in file_list:
        file_index += 1
        print 'file_index: ', file_index
        with codecs.open(filename, encoding='utf-8') as f:
            for line in f.readlines():
                total_line_set.add(line.strip())
    codecs.open('combine_poi_unfiltered.txt', mode='wb', encoding='utf-8').writelines([item+'\n' for item in total_line_set])
# combine_files()
def filter_poi_data(filename):
    '''过滤原则:
    1、长度小于等于1
    2、以数字开头
    3、以数字结尾
    4、滤去句子中非汉字、非英文、非数字
    '''
    new_line_list = []
    # filename = os.path.join(file_path, 'combine_poi_unfiltered.txt')
    num_pattern = re.compile(r'\d+')
    ch_letter_num_pattern = re.compile(ur"([\u4E00-\u9FA5\w]+)", re.U)
    with codecs.open(filename, encoding='utf-8') as f:
        for line in f.readlines():
            line = ''.join(ch_letter_num_pattern.findall(line)) #过滤掉非汉字、非英文、非数字字符
            if len(line.strip()) <= 1:  #长度小于1的句子
                # print 'lenth < 1: ', line
                continue
            if num_pattern.match(line):#以数字开头
                # print 'start with nun: ', line
                continue
            if num_pattern.match(line.strip()[-1]):
                # print 'end with num: ', line # 以数字结尾
                continue
            new_line_list.append(line)
    print len(new_line_list)
    filtered_filename = filename.split('.')[0] + "_filtered.txt"
    codecs.open(filtered_filename , mode='wb', encoding='utf-8').writelines([item+'\n' for item in new_line_list])

    only_ch_txt(filtered_filename)#数据分离


def only_ch_txt(filtered_filename):
    '''将过滤后的文件分为只有汉字的（*_ch.txt）和包含英文/数字字符的（*_eng_num.txt）'''
    en_letter_pattern = re.compile(ur"([^\u4E00-\u9FA5]+)", re.U)
    en_letter_list = []
    # combine_filename = os.path.join(file_path, 'combine_poi_filtered.txt')
    only_ch_list = []
    with codecs.open(filtered_filename, encoding='utf-8') as f:
        for line in f.readlines():
            if en_letter_pattern.search(line.strip()):
                en_letter_list.append(line)
            else:
                only_ch_list.append(line)
    ch_filename = filtered_filename.split('.')[0] + "_ch.txt"
    eng_num_filename = filtered_filename.split('.')[0] + "_eng_num.txt"
    print 'ch lenght: %s, eng lenght: %s' % (len(only_ch_list), len(en_letter_list))
    codecs.open(ch_filename, mode='wb', encoding='utf-8').writelines(only_ch_list)
    codecs.open(eng_num_filename, mode='wb', encoding='utf-8').writelines(en_letter_list)

def data_clean():
    '''数据清洗'''
    cuted_file_pattern = os.path.join(PATH, 'cities_cuted', '*_cuted.txt')
    print cuted_file_pattern
    file_list = glob.glob(cuted_file_pattern)
    print "len(file_list):", len(file_list)
    for filename in file_list:
        print 'filtering...: ', filename
        filter_poi_data(filename)

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
if __name__ == "__main__":
    scp_ch_files_to_s3()
