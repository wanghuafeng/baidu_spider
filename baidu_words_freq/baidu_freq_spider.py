__author__ = 'huafeng'
#coding:utf-8

import os
import re
import sys
import codecs
import time
import requests
from bs4 import BeautifulSoup

PATH = os.path.dirname(os.path.abspath(__file__))
class CrawlFreq(object):

    def __init__(self, filename):
        '''输入文本格式[1,n]列，其间用\t隔开，第一列为待抓取词'''
        self.filename = filename
        self.words_list = []#待抓取词数组
        self._gen_words_list()#加载待抓取，去重

    def _gen_words_list(self):
        '''加载待抓取词'''
        with codecs.open(self.filename, encoding='utf-8') as f:
            unique_words_set = set((line.strip().split('\t')[0] for line in f.readlines() if line))
            self.words_list.extend(unique_words_set)
            # print len(unique_words_set)
    @staticmethod
    def get_freq_by_words(words):
        '''抓取指定词的词频'''
        url_pattern = 'http://www.baidu.com/s?wd="%s"'
        num_pattern = re.compile(r'\d+')
        url = url_pattern%words
        try:
            html = requests.get(url, timeout=15).text
        except:
            time.sleep(10)
            try:
                html = requests.get(url, timeout=15).text
            except:
                return
        soup = BeautifulSoup(html)
        time.sleep(2)
        num_class_str = soup.find(class_='nums')
        if num_class_str:
            num_text = num_class_str.get_text()
            num = "".join(num_pattern.findall(num_text))
            return num

    def get_freq_by_file(self):
        '''抓取初始文件中所有词的百度词频'''
        crawl_failed_words_list = []
        url_pattern = 'http://www.baidu.com/s?wd="%s"'
        num_pattern = re.compile(r'\d+')
        words_freq_filename = self.filename.rsplit('.', 1)[0] + '.freq'
        sucess_count = 0
        failed_count = 0
        with codecs.open(words_freq_filename, mode='wb', encoding='utf-8')as wf:
            for word in self.words_list:
                url = url_pattern%word
                try:html = requests.get(url, timeout=15).text
                except:
                    time.sleep(10)#第一次请求超时，10秒后最第二次请求
                    try:html = requests.get(url, timeout=15).text
                    except:
                        crawl_failed_words_list.append(word)
                        continue
                soup = BeautifulSoup(html)
                span_level_str = soup.find(class_='nums')
                if span_level_str:
                    sucess_count += 1
                    num_text = span_level_str.get_text()
                    num = "".join(num_pattern.findall(num_text))
                    com_str = "\t".join((word, num))
                    print  sucess_count , " ", com_str
                    wf.write(com_str + '\n')#抓取成功的词，连同词频一起写入到本地
                    time.sleep(2)
                else:
                    crawl_failed_words_list.append(word)
                    failed_count += 1
                    print "failed ... %s"%word

        if crawl_failed_words_list:
            #解析页面失败的词，进行二次抓取
            reCrawl_sucess_words_list = []# 第二次抓取成功
            reCrawl_failed_words_list = []# 第二次抓取失败
            print 're crawl the failed words...'
            for words in crawl_failed_words_list:
                words_freq = self.get_freq_by_words(words)
                if words_freq:
                    reCrawl_sucess_words_list.append(words + '\t' + words_freq + '\n')
                else:
                    reCrawl_failed_words_list.append(words + '\n')
            failed_words_filename = os.path.join(PATH, 'crawl_failed_words.txt')
            codecs.open(failed_words_filename, mode='wb', encoding='utf-8').writelines(
                reCrawl_failed_words_list)#抓取失败的词
            codecs.open(words_freq_filename, mode='ab', encoding='utf-8').writelines(reCrawl_sucess_words_list)
            print 'crawl finished, failed count: ', len(reCrawl_failed_words_list)
        print 'total count of unique words: ', len(self.words_list)

        self.make_inorder(words_freq_filename)#将抓取成功的词按序排列
    @staticmethod
    def make_inorder(filename):
        '''使文件按词频倒序排列
        文件格式: 第一列为词，第二列为词频, \t 分割'''
        with codecs.open(filename, encoding='utf-8') as f:
            line_list_inorder = sorted(f.readlines(), key=lambda x:int(x.split('\t')[-1]), reverse=True)
            codecs.open(filename, mode='wb', encoding='utf-8').writelines(line_list_inorder)
if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 2:
        filename = args[1]
        if not os.path.isfile(filename):
            raise ValueError('no such file: %s'%filename)
        freq_crawler = CrawlFreq(filename)
        freq_crawler.get_freq_by_file()
    else:
        print 'USAGE: -f filename'
        
    def main_test():
        '''主函数测试'''
        src_filename = r'F:\github\Spider_baidu\baidu_words_freq\New_Word.txt'
        freq_crawler = CrawlFreq(src_filename)
        freq_crawler.get_freq_by_file()
    def make_inorder_test():
        '''测试排序操作'''
        filename = os.path.join(PATH, 'New_Word.freq')
        CrawlFreq.make_inorder(filename)
    # make_inorder_test()
    def test_on_crawl():
        '''测试某一个词的词频抓取'''
        words = '百度'
        print CrawlFreq.get_freq_by_words(words)
    def use_num_pattern():
        '''从百度标签中中筛选出词频'''
        s = "百度为您找到相关结果约8,080,000个"
        num_list = re.findall(r'\d+',s)
        num = "".join(num_list)
        print num
        print type(num)
    # use_num_pattern()
    def read_unformal_page(words):
        url = 'http://www.baidu.com/s?wd="%s"'%words
        html = requests.get(url).text
        soup = BeautifulSoup(html)
        div_level_str = soup.find(class_='nums')
        print div_level_str
    # read_unformal_page('百度')
