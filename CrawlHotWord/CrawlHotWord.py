#coding:utf-8
import os
import re
import time
import codecs
import urllib2
import datetime
from bs4 import BeautifulSoup

from  mongoDB import MongoDB

try:
    PATH = os.path.dirname(os.path.abspath(__file__))
except:
    PATH = os.getcwd()

def baidu_crawl_one_page_url():
    '''抓取指定百度热词url'''
    topic_url = 'http://top.baidu.com/buzz?b=495&c=31'
    no_num_pattern = re.compile(ur"([^\u4E00-\u9FA5]+)", re.U)
    html = urllib2.urlopen(topic_url).read()
    soup = BeautifulSoup(html)
    keyword_list = [keyword_str.find('a').text.strip() for keyword_str in soup.find_all('td', class_='keyword')]
    # print len(keyword_list)
    search_count_list = []
    # search_count_list = [item.text.strip() for item in soup.find_all('td', class_='last')]
    for srarch_count_str in soup.find_all('td', class_='last'):
        search_count = srarch_count_str.text.strip()
        if search_count:
            search_count_list.append(search_count)
        else:
            search_count_list.append('1')
    keyword_search_count_tuple_list = zip(keyword_list, search_count_list)
    for keyword_searchCount_tuple in keyword_search_count_tuple_list:
        keyword = keyword_searchCount_tuple[0]
        searchCount = keyword_searchCount_tuple[-1]
        if no_num_pattern.search(keyword):
            # print keyword, searchCount
            continue
        else:
            print keyword, searchCount
# baidu_crawl_one_page_url()
def sina_topicUrl_topicTitle():
    '''抓取新浪topic_url与topic_title所构成的tuple的数组'''
    sina_url = 'http://top.weibo.com'
    sina_base_url = 'http://top.weibo.com/newtop/keyword'
    html = urllib2.urlopen(sina_base_url).read()
    soup = BeautifulSoup(html)
    div_level_str = soup.find('div', id='pl_index_toplist')
    dl_level_str_list = div_level_str.find_all('dl', class_='bd_list clearfix')
    whole_dd_level_list = []
    for dl_level_str in dl_level_str_list:
        whole_dd_level_list.extend(dl_level_str.find_all('dd'))
    topicUrl_topciTitle_tuple_list = [(sina_url+item.find('a')['href'], item.text) for item in whole_dd_level_list]

    # print len(topicUrl_topciTitle_tuple_list)
    return [item[-1] for item in topicUrl_topciTitle_tuple_list]
# sina_topicUrl_topicTitle()
class HotWordCrawler:
    def __init__(self):
        self.sina_url = 'http://top.weibo.com'
        self.hot_word_log()
        try:
            self.mongo = MongoDB()
        except:
            self.logObj.write('mongoDB connectd failed...')
    def hot_word_log(self):
        '''热词错误信息'''
        log_filename = os.path.join(PATH, 'log', 'hot_word_log.txt')
        self.logObj = codecs.open(log_filename, 'ab', encoding='utf-8')
    def baidu_crawler(self):
        '''抓取百度热词'''
        baidu_url = 'http://top.baidu.com'
        topic_url_filename = os.path.join(PATH, 'src', 'baidu_whole_topic_url.txt')
        no_num_pattern = re.compile(ur"([^\u4E00-\u9FA5]+)", re.U)
        with codecs.open(topic_url_filename, encoding='utf-8') as f:
            for line in f.readlines():
                splited_line = line.split('#')
                topic_url = splited_line[0]
                topic_title = splited_line[-1].strip()
                timestamp = time.strftime('%Y_%m_%d_%H:%M:%S')
                try:
                    html = urllib2.urlopen(topic_url).read()
                except:
                    time.sleep(120)
                    try:
                        html = urllib2.urlopen(topic_url).read()
                    except:
                        time.sleep(120)
                        try:
                            html = urllib2.urlopen(topic_url).read()
                        except:
                            self.logObj.write('baidu_spider %(timestamp)s timed out in url;%(topic_url)s\n'%{'timestamp':timestamp,'topic_url':topic_url})
                            continue
                time.sleep(8)
                soup = BeautifulSoup(html)
                try:
                    keyword_list = [keyword_str.find('a').text.strip() for keyword_str in soup.find_all('td', class_='keyword')]
                    search_count_list = []
                    for srarch_count_str in soup.find_all('td', class_='last'):
                        search_count = srarch_count_str.text.strip()
                        if search_count:
                            search_count_list.append(search_count)
                        else:
                            search_count_list.append('1')
                except BaseException:
                    self.logObj.write('baidu_spider %(timestamp)s div pattern changed in url;%(topic_url)s\n'%{'timestamp':timestamp, 'topic_url':topic_url})
                # print keyword_list, search_count_list
                # print len(keyword_list), len(search_count_list)
                try:
                    assert len(keyword_list) == len(search_count_list)
                except AssertionError:
                    self.logObj.write('baidu_spider %(timestamp)s lenght of keyword_list and search_count_list do not equal in url;%(topic_url)s\n'%{'timestamp':timestamp, 'topic_url':topic_url})
                keyword_search_count_tuple_list = zip(keyword_list, search_count_list)
                for keyword_search_count_tuple in keyword_search_count_tuple_list:
                    keyword, search_count = keyword_search_count_tuple
                    if no_num_pattern.search(keyword):
                        continue
                    else:
                        now = datetime.datetime.now()
                        # print keyword, baidu_url, topic_title, {'f':int(search_count),'d':now}
                        self.mongo.update_word(keyword, baidu_url, topic_title, {'f':int(search_count),'d':now})
    def sina_topicUrl_topicTitle(self):
        '''抓取新浪topic_url与topic_title所构成的tuple的数组'''
        sina_base_url = 'http://top.weibo.com/newtop/keyword'
        timestamp = time.strftime('%Y_%m_%d_%H:%M:%S')
        try:
            html = urllib2.urlopen(sina_base_url, timeout=20).read()
        except BaseException:
            time.sleep(120)
            try:
                html = urllib2.urlopen(sina_base_url, timeout=20).read()
            except BaseException:
                time.sleep(120)
                try:
                    html = urllib2.urlopen(sina_base_url, timeout=20).read()
                except BaseException:
                    self.logObj.write('sina base_url timeoutd out at: %s'%timestamp)
                    return []
        soup = BeautifulSoup(html)
        div_level_str = soup.find('div', id='pl_index_toplist')
        dl_level_str_list = div_level_str.find_all('dl', class_='bd_list clearfix')
        whole_dd_level_list = []
        for dl_level_str in dl_level_str_list:
            whole_dd_level_list.extend(dl_level_str.find_all('dd'))
        topicUrl_topciTitle_tuple_list = [(self.sina_url+item.find('a')['href'], item.text) for item in whole_dd_level_list]
        return topicUrl_topciTitle_tuple_list
    def sina_crawler(self):
        '''关键字以及搜索量，并将插入到数据库中'''
        topicUrl_topciTitle_tuple_list = self.sina_topicUrl_topicTitle()
        no_num_pattern = re.compile(ur"([^\u4E00-\u9FA5]+)", re.U)
        timestamp = time.strftime('%Y_%m_%d_%H:%M:%S')
        for topicUrl_topicTitle_tuple in topicUrl_topciTitle_tuple_list:
            topic_url = topicUrl_topicTitle_tuple[0]
            topic_title = topicUrl_topicTitle_tuple[-1]
            try:
                html = urllib2.urlopen(topic_url).read()
            except BaseException:
                time.sleep(120)
                try:
                    html = urllib2.urlopen(topic_url).read()
                except BaseException:
                    time.sleep(120)
                    try:
                        html = urllib2.urlopen(topic_url).read()
                    except BaseException:
                        self.logObj(self.logObj.write('sina_spider %(timestamp)s timed out in url;%(topic_url)s\n'%{'timestamp':timestamp,'topic_url':topic_url}))
                        continue
            time.sleep(10)
            soup = BeautifulSoup(html)
            try:
                div_level_str = soup.find('div', class_='influ_frame_con')
                dt_level_str_list = div_level_str.find_all('dt')
            except BaseException:
                self.logObj.write('sina_spider %(timestamp)s div pattern changed in url;%(topic_url)s\n'%{'timestamp':timestamp,'topic_url':topic_url})
                continue
            for dt_level_str in dt_level_str_list:
                try:
                    keyword = dt_level_str.find('span', class_='key').text
                    search_count = dt_level_str.find('span', class_='num').text
                except BaseException:
                    self.logObj.write('sina_spider %(timestamp)s div pattern changed in url;%(topic_url)s\n'%{'timestamp':timestamp,'topic_url':topic_url})
                    continue
                if no_num_pattern.search(keyword):
                    continue
                else:
                    now = datetime.datetime.now()
                    # print keyword, self.sina_url, topic_title, {'f':int(search_count),'d':now}
                    # time.sleep(1)
                    try:
                        self.mongo.update_word(keyword, self.sina_url, topic_title, {'f':int(search_count),'d':now})
                    except:
                        self.logObj.write('db update error in url;%s'%topic_url)
    def main(self):
        self.baidu_crawler()
        self.sina_crawler()
if __name__ == '__main__':
    crawler = HotWordCrawler()
    crawler.main()
