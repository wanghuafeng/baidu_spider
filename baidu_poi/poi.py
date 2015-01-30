__author__ = 'huafeng'
#coding:utf-8
import os
import codecs
import json
import time
import glob
import subprocess
import requests
import Queue
from math import ceil
PATH = os.path.dirname(os.path.abspath(__file__))
import gevent.monkey
gevent.monkey.patch_all()

url_pattern = 'http://localhost:4185/geocut?text=%s'

def get_all_poi_files():
    total_poi_list = []
    glob_pattern = os.path.join(PATH, 'cities', '*')
    file_list = glob.glob(glob_pattern)
    print 'files count', len(file_list)
    for filename in file_list:
        with codecs.open(filename, encoding='utf-8') as f:
            total_poi_list.extend(f.readlines())

def splited_poi_sentence(sentence, queue):
    # sentence = '北大街与西大街交汇处'
    '''切割poi词汇'''
    # sentence_set = set()
    try:
        url = url_pattern % sentence
        html = requests.get(url, timeout=80).text
        json_dic =  json.loads(html)
        splited_sentence = json_dic.get('data')
        for words_list in splited_sentence:
            for words in words_list:
                queue.put_nowait(words)
    except:
        print 'slicer failed in: ', sentence
        return

def read_poi_files():
    '''读取不同城市POI信息'''
    total_poi_list = []
    thread_sentence_queue = Queue.Queue()
    with codecs.open('combine_poi.txt', encoding='utf-8') as f:
        total_poi_list.extend(f.readlines())
    poi_count = len(total_poi_list)
    print 'poi sentence count:', poi_count #10099198
    threads = []
    threads_count = 1000
    line_list_partial_count = int(ceil(poi_count)/float(threads_count))
    print 'line_list_partial_count', line_list_partial_count
    for poi_sequence in range(4550, line_list_partial_count):
        if poi_count == poi_count - 1:
            range_start, range_end = poi_sequence*threads_count, poi_count
        else:
            range_start, range_end = poi_sequence*threads_count, (poi_sequence+1)*threads_count
        print 'range_start, range_end: ', range_start, range_end
        for poi_index in xrange(range_start, range_end):
            poi_sentence = total_poi_list[poi_index].strip().split(':')[-1]
            threads.append(gevent.spawn(splited_poi_sentence, poi_sentence, thread_sentence_queue))
        gevent.joinall(threads)
        print('thread_sentence_queue.qsize()', thread_sentence_queue.qsize())
        # partial_splited_sentence_set = set()
        tmp_list = [thread_sentence_queue.get(index) for index in range(thread_sentence_queue.qsize())]
        codecs.open('./data/%s_.txt'%(poi_sequence+1), mode='wb', encoding='utf-8').writelines(set([item+'\n' for item in tmp_list]))
# read_poi_files()
def read_poi_city(filename):
    '''读取不同城市POI信息'''
    total_poi_list = []
    thread_sentence_queue = Queue.Queue()
    with codecs.open(filename, encoding='utf-8') as f:
        total_poi_list.extend(f.readlines())
    total_poi_count = len(total_poi_list)
    print 'line list count:', total_poi_count #10099198
    threads = []
    threads_count = 1000
    line_list_partial_count = int(ceil(total_poi_count)/float(threads_count))
    print 'line_list_partial_count', line_list_partial_count
    if (total_poi_count != 0) and (line_list_partial_count==0):#list中的数据不满1000的时候，line_list_partial_count值为0，此时会跳过某文件的抓取
        line_list_partial_count = 1
    for poi_sequence in range(line_list_partial_count):
        # print poi_sequence, line_list_partial_count
        if poi_sequence == line_list_partial_count - 1:
            range_start, range_end = poi_sequence*threads_count, total_poi_count
        else:
            range_start, range_end = poi_sequence*threads_count, (poi_sequence+1)*threads_count
        # print 'range_start, range_end: ', range_start, range_end
        print "total count:%s, range_index:%s, city:%s"%(line_list_partial_count, poi_sequence+1, os.path.basename(filename))
        for poi_index in xrange(range_start, range_end):
            poi_sentence = total_poi_list[poi_index].strip().split(':')[-1]
            threads.append(gevent.spawn(splited_poi_sentence, poi_sentence, thread_sentence_queue))
        gevent.joinall(threads)
        print('queue lenght:', thread_sentence_queue.qsize())
        # partial_splited_sentence_set = set()
    tmp_list = [thread_sentence_queue.get(index) for index in range(thread_sentence_queue.qsize())]
    codecs.open('./cities_cuted/%s_cuted.txt'%os.path.basename(filename), mode='wb', encoding='utf-8').writelines(set([item+'\n' for item in tmp_list]))
# filename = os.path.join(PATH, 'cities', 'beijing')
# read_poi_city(filename)

def get_poi_cuted_sentence(filename):
    '''对传入文件中所有的poi_sentence进行切割'''
    comamnd =  "coffee ./geocut/cut.coffee %s" % filename
    total_cuted_sentence_set = set()
    popen = subprocess.Popen(comamnd, shell=True, stdout=subprocess.PIPE)
    stdout_json_data_list = popen.stdout.readlines()
    print len(stdout_json_data_list),
    for line in stdout_json_data_list:
        cuted_sentence_list = json.loads(line.decode('utf-8'))
        if not isinstance(cuted_sentence_list, list):
            continue
        for partial_list in cuted_sentence_list:
            assert isinstance(partial_list, list)
            for words in partial_list:
                total_cuted_sentence_set.add(words)
    print len(total_cuted_sentence_set), os.path.basename(filename)
    codecs.open('./%s_cuted.txt'%os.path.basename(filename), mode='wb', encoding='utf-8').writelines([item+'\n' for item in total_cuted_sentence_set])
filename = os.path.join(PATH, 'cities', 'beijing')
get_poi_cuted_sentence(filename)

def glob_file_list(startwith='', file_list_index_start=0):
    '''用glob筛选出符合规则的poi文件'''
    glob_pattern = os.path.join(PATH, 'cities', '%s*'%startwith)
    file_list = glob.glob(glob_pattern)
    print file_list
    print 'file_list lenght: ', len(file_list)
    file_index = file_list_index_start
    for filename in file_list[file_list_index_start:]:
        print 'filename, file_index', filename, file_index
        file_index += 1
        # read_poi_city(filename)
        get_poi_cuted_sentence(filename)

# glob_file_list(startwith='beijing', file_list_index_start=0)
# [glob_file_list(startwith=i, file_list_index_start=0) for i in 'g h i j k l m n o p q r s t u v w x y z'if i.isalpha()]