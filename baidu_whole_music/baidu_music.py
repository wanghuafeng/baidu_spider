__author__ = 'wanghuafeng'
#coding:utf-8
import os
import re
import time
import codecs
import requests
import simplejson
from bs4 import BeautifulSoup

PATH = os.path.dirname(os.path.abspath(__file__))

def get_hot_singer_url():
    '''获取所有歌手的url'''
    baidu_music_url = 'http://music.baidu.com/artist'
    html = requests.get(baidu_music_url, timeout=20).text
    soup = BeautifulSoup(html)
    li_url_list = []
    ul_level_list = soup.find_all('ul', class_='clearfix')
    [li_url_list.extend(item.find_all('li')) for item in ul_level_list]
    # print len(set(li_url_list))#2331
    total_singer_set =set()
    for li_str in li_url_list:
        if not li_str.find('a'):
            continue#如果没有a标签
        total_singer_set.add(li_str.a['href'])
    print len(total_singer_set)#歌手数量2200
    codecs.open('total_singer_url.txt', mode='wb', encoding='utf-8').writelines(["http://music.baidu.com/" + item+'\n' for item in total_singer_set])
# get_hot_singer_url()

def analysis_one_singer_page():
    '''解析一个歌手的页面'''
    url = 'http://music.baidu.com//artist/87954342'
    html = requests.get(url, timeout=20).text
    soup = BeautifulSoup(html)
    song_title_str_list = soup.find_all('span', class_='song-title')
    song_title_list = [song_title.a['title'].strip() for song_title in song_title_str_list]#当前页的歌曲列表
    for song in song_title_list:
        print song
    total_page_num_div = soup.find('div', class_='page-inner')#总页码所在div
    page_list = total_page_num_div.find_all('a', text=re.compile('\d+'))
    if page_list:#数据位多页
        total_page_num = page_list[-1].get_text()
        # print page_list[-1]
        print total_page_num #总页码
# analysis_one_singer_page()

def page_turning_json_data():
    '''第二次请求时返回json格式数据，解析出该页面的歌曲列表'''
    url = 'http://music.baidu.com/data/user/getsongs'
    query = {
            # "start":"0",
            # "ting_uid":'172120638',
        "start" : '25',
        "ting_uid" : '12894013',
        'order': "hot",
            }
    r = requests.get(url, params=query)
    print r.url
    jsonObj = simplejson.loads(r.text).get('data')
    if jsonObj:
        html = jsonObj.get('html').strip()
        if html:
            # print html
            soup = BeautifulSoup(html)
            song_title_str_list = soup.find_all('span', class_='song-title')
            song_title_list = [song_title.a["title"].strip() for song_title in song_title_str_list]
            for song in song_title_list:
                print song
# page_turning_json_data()

class BaiduSongSpider(object):

    # first_failed_crawled_url_list = []
    # second_failed_crawled_url_list = []
    songs_fileanme = os.path.join(PATH, 'total_songs.txt')
    frist_failed_filename = os.path.join(PATH, 'first_crawl_failed_url.txt')
    second_failed_filename = os.path.join(PATH, 'second_crawl_failed_url.txt')
    def __init__(self, singer_filename=None):
        if not singer_filename:
            singer_filename = os.path.join(PATH, 'total_singer_url.txt')
        self.all_singer_url_list = []
        self._load_all_singer_url(singer_filename)

    def write_song_title(self, songer_list):
        '''抓取成功的歌曲列表写入本地'''
        codecs.open(self.songs_fileanme, mode='ab', encoding='utf-8').writelines(songer_list)

    def write_failed_crawl_url(self, url, firstRequest=True):
        '''抓取是是失败的url写入到本地'''
        if firstRequest:
            codecs.open(self.frist_failed_filename, mode='ab', encoding='utf-8').write(url + '\n')
        else:
            codecs.open(self.second_failed_filename, mode='ab', encoding='utf-8').write(url + '\n')

    def _load_all_singer_url(self, singer_filename):
        '''读取所有歌手的url'''
        all_singer_url_list = codecs.open(singer_filename, encoding='utf-8').readlines()
        self.all_singer_url_list.extend([item.strip() for item in all_singer_url_list])
    # total_singer_url_list = get_all_singer_url()#所有歌手url列表2200

    def first_crawl(self, singer_url):
        '''第一次请求，地址为歌手url，判断该页面是否为多页
           将该页的歌曲列表写入到本地，
           返回该歌手歌曲是否为多页并返回页码，若非多页，则返回空'''
        try:
            html = requests.get(singer_url, timeout=20).text
        except:
            try:
                html = requests.get(singer_url, timeout=20).text
            except:
                print 'timeout url: ', singer_url
                self.write_failed_crawl_url(singer_url)
                return
        soup = BeautifulSoup(html)
        time.sleep(3)
        song_title_str_list = soup.find_all('span', class_='song-title')
        if song_title_str_list:
            song_title_list = [song_title.a['title'].strip() for song_title in song_title_str_list]
            self.write_song_title([item + '\n' for item in song_title_list])#抓取到的歌曲名写入到本地文件
        else:
            print 'failed url: ', singer_url
            # self.first_failed_crawled_url_list.append(singer_url)
            self.write_failed_crawl_url(singer_url)
            return

        #解析该歌手歌曲是否为多页
        total_page_num_div = soup.find('div', class_='page-inner')#总页码所在div
        if not total_page_num_div:
            print 'no has page-inne in url: ', singer_url
            self.write_failed_crawl_url(singer_url)
            return
        page_list = total_page_num_div.find_all('a', text=re.compile('\d+'))
        if page_list:#数据位多页
            total_page_num = page_list[-1].get_text()
            # print page_list[-1]
            return total_page_num #总页码

    def second_and_then_crawl(self, start, singerID):
        '''第二页及以后的请求，返回json格式数据'''
        url = 'http://music.baidu.com/data/user/getsongs'
        query = {
            "start":"%s"%start,
            "ting_uid":"%s"%singerID,
            'order': "hot",
            }
        try:
            r = requests.get(url, params=query, timeout=20)
        except:
            try:
                r = requests.get(url, params=query, timeout=20)
            except:
                # self.second_failed_crawled_url_list.append(url + '?start=%(start)s&ting_uid=%(ting_uid)s'%(query))
                self.write_failed_crawl_url(url + '?start=%(start)s&ting_uid=%(ting_uid)s'%(query), False)
                return

        jsonObj = simplejson.loads(r.text).get('data')
        time.sleep(3)
        if jsonObj:
            html = jsonObj.get('html').strip()
            if html:
                soup = BeautifulSoup(html)
                song_title_str_list = soup.find_all('span', class_='song-title')
                song_title_list = [song_title.a['title'].strip() for song_title in song_title_str_list]
                self.write_song_title([item + '\n' for item in song_title_list])#抓取到的歌曲名写入到本地文件
            else:
                print 'no html in jsonObj : ', r.url
                # self.second_failed_crawled_url_list.append(r.url)
                self.write_failed_crawl_url(r.url, False)
        else:
            print 'no jsonObj : ', r.url
            # self.second_failed_crawled_url_list.append(r.url)
            self.write_failed_crawl_url(r.url, False)

if __name__ == "__main__":
    def first_crawl_test():
        url = u'http://music.baidu.com//artist/87954342'
        print BaiduSongSpider().first_crawl(url)
    # first_crawl_test()
    def second_crawl_test():
        start = '25'
        singer_id = '2507'
        BaiduSongSpider().second_and_then_crawl(start, singer_id)
    # second_crawl_test()
    def run():
        total_singer_filename = os.path.join(PATH, 'total_singer_url.txt')
        songSpider = BaiduSongSpider(total_singer_filename)
        count = 1
        for singer_url in songSpider.all_singer_url_list:
            singer_id = os.path.basename(singer_url)#歌手ID
            print 'crawling url count: ', count
            total_page_num = songSpider.first_crawl(singer_url)#第一次抓取，返回总页码
            print "url count: %s, total_page_num: %s"%(count, total_page_num if total_page_num else "0")
            count += 1
            if total_page_num:#如果数据为多页
                for page_num in range(1, int(total_page_num)):
                    print 'page turning: %s'%page_num
                    start = page_num * 25
                    songSpider.second_and_then_crawl(start, singer_id)#翻页请求

    run()
