__author__ = 'huafeng'
#coding:utf-8
import os
import re
import codecs
import time
import random
import urllib2
import gevent
import gevent.monkey
from math import ceil, floor
from bs4 import BeautifulSoup
gevent.monkey.patch_all()
PATH = os.path.dirname(os.path.abspath(__file__))
class FreqCrawler(object):
    def __init__(self, filename):
        '''输入文本格式[1,n]列，期间用\t隔开，第一列为待抓取词'''
        self.filename = filename
        self.words_list = []#待抓取词数组
        self._gen_word_list()#加载待抓取，去重
        self.word_freq_list = []

    def _gen_word_list(self):
        with open(self.filename) as f:
            self.words_list.extend(set([item.strip().split('\t')[0] for item in f.readlines()]))

    def read_item_url(self, word):

        url_pattern = 'http://www.baidu.com/s?wd="%s"&fr=wenku'
        num_pattern = re.compile(r'\d+')

        # for word in self.words_list:
        url = url_pattern%word
        try:
            html = urllib2.urlopen(url, timeout=30).read()
        except:
            try:
                html = urllib2.urlopen(url, timeout=30).read()
            except:
                print 'request timed out in url:%s'%url
                return
        soup = BeautifulSoup(html)
        span_level_str_list = soup.find_all('span', class_='nums')

        if span_level_str_list:
            span_level_str = span_level_str_list[0]
            num_text = span_level_str.get_text()
            num = "".join(num_pattern.findall(num_text))
            com_str = "\t".join((word, str(num))) + '\n'
        else:
            com_str = "\t".join((word, "0")) + '\n'
        self.word_freq_list.append(com_str)

    def write_wrod_freq(self):
        filename = os.path.join(PATH, 'out', 'local_multi_thread_word_freq')
        with open(filename, mode='a') as wf:
            wf.writelines(self.word_freq_list)

    def main(self):
        '''使用gevent多线程抓取'''
        threads = []#要执行的线程
        words_count = len(self.words_list)
        thread_count = 10000#线程数量

        words_list_partial_count = int(ceil(words_count/float(thread_count)))
        for section_sequence in range(words_list_partial_count):
            if section_sequence == words_count - 1:#保证所有的数组内元素都会被使用到
                range_start, range_end = thread_count*section_sequence, words_count
            else:
                range_start, range_end = thread_count*section_sequence, (section_sequence +1)*thread_count

            for word_point in range(range_start, range_end):
                word = self.words_list[word_point]
                threads.append(gevent.spawn(self.read_item_url, word))
            gevent.joinall(threads)


            self.write_wrod_freq()
            self.word_freq_list[:] = []
            time.sleep(2)

freqspider = FreqCrawler('filename.txt')
freqspider.main()

