#coding:utf-8
import os
import re
import time
import codecs
import urllib2
import datetime
from bs4 import BeautifulSoup

try:
    PATH = os.path.dirname(os.path.abspath(__file__))
except:
    PATH = os.getcwd()

def baidu_topic_url():
    '''抓取所有百度topic url，并写入到本地'''
    baidu_url = 'http://top.baidu.com'
    baidu_root_url = 'http://top.baidu.com/boards'
    html = urllib2.urlopen(baidu_root_url).read()
    soup = BeautifulSoup(html)
    whole_topic_list = soup.find_all('div', class_='links')#所有百度风云榜13个主题
    total_a_level_list = []
    for topic_url in whole_topic_list:
        total_a_level_list.extend(topic_url.find_all('a'))
    href_topic_name_tuple_list = [(item['href'].replace('.', baidu_url), item.text) for item in total_a_level_list]
    com_str_list = ['#'.join(item)+'\n' for item in href_topic_name_tuple_list]
    topic_url_filename = os.path.join(PATH, 'src', 'baidu_whole_topic_url.txt')
    codecs.open(topic_url_filename, mode='wb', encoding='utf-8').writelines(com_str_list)
# baidu_topic_url()

def baidu_crawl_one_page_url():
    '''抓取指定百度热词url'''
    topic_url = 'http://music.baidu.com/top/yingshijinqu'
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
    print len(keyword_list), len(search_count_list)
    keyword_search_count_tuple_list = zip(keyword_list, search_count_list)
    for keyword_searchCount_tuple in keyword_search_count_tuple_list:
        keyword = keyword_searchCount_tuple[0]
        searchCount = keyword_searchCount_tuple[-1]
        if no_num_pattern.search(keyword):
            # print keyword, searchCount
            continue
        else:
            print keyword, searchCount
baidu_crawl_one_page_url()
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
    return topicUrl_topciTitle_tuple_list
# sina_topicUrl_topicTitle()
def crawl_keyword_searchCount():
    '''关键字以及搜索量'''
    sina_url = 'http://top.weibo.com'
    no_num_pattern = re.compile(ur"([^\u4E00-\u9FA5]+)", re.U)
    topicUrl_topciTitle_tuple_list = sina_topicUrl_topicTitle()
    for topicUrl_topicTitle_tuple in topicUrl_topciTitle_tuple_list:
        url = topicUrl_topicTitle_tuple[0]
        topicTitle = topicUrl_topicTitle_tuple[-1]
        # url = 'http://top.weibo.com/newtop/keyworddetail?second=431&depart=1'
        html = urllib2.urlopen(url).read()
        soup = BeautifulSoup(html)
        div_level_str = soup.find('div', class_='influ_frame_con')
        dt_level_str = div_level_str.find('dt')
        keyword = dt_level_str.find('span', class_='key').text
        search_count = dt_level_str.find('span', class_='num').text
        if no_num_pattern.search(keyword):
            continue
        else:
            now = datetime.datetime.now()
            print keyword, search_count
            time.sleep(1)
# crawl_keyword_searchCount()
        # print keyword, search_count
# fileObj = open(os.path.join(PATH, 'a.txt'), mode='wb')
# print >>fileObj, 'helloworld'
