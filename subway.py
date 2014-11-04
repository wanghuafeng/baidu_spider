__author__ = 'sivil'
#coding:utf-8
import os
import codecs
import time
import requests
import simplejson
from bs4 import BeautifulSoup
PATH = os.path.dirname(__file__)

def handle_param_dic():
    param = u'''
    newmap	1
    reqflag	pcmap
    biz	1
    from	webmap
    qt	bt
    da_src	pcmappg.searchBox.button
    c	131
    sn	2$$$$$$育新$$0$$$$
    en	2$$$$$$太阳宫$$0$$$$
    sc	131
    ec	131
    rn	5
    exptype	dep
    exptime	2014-11-01 16:35
    version	5
    tn	B_NORMAL_MAP
    nn	0
    ie	utf-8
    l	12
    b	(12930992.97,4824883.72;12985328.97,4826931.72)
    t	1414830934024'''
    param_list =  [item.split('\t') for item in param.split('\n') if item]
    param_dic = dict(param_list)
    print param_dic
    url = 'http://map.baidu.com/#'
    r = requests.get(url)
    print r.text

def get_distance_from_baidu(start, end):
    '''get distance between two stations. (data from baidu)'''
    url = 'http://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&qt=bt&da_src=pcmappg.searchBox.button&c=131&sn=2$$$$$${start}$$0$$$$&en=2$$$$$${end}$$0$$$$&sc=131&ec=131&rn=5&exptype=dep&exptime=2014-11-02%2017:10&version=5&tn=B_NORMAL_MAP&nn=0&ie=utf-8&l=13&b=(12944392.254999999,4849774.095000001;12971560.254999999,4850094.095000001)&t=1414923533275'.format(start=start, end=end)
    r = requests.get(url)
    json_data =  simplejson.loads(r.text)
    try:
        contents =  json_data['content']#exts,line,stop info .etc
        exts = contents[0]['exts']
        distance = exts[0].get('distance')
        return  distance
    except:
        return False

# get_distance_from_baidu('通州北苑', '八里桥')


def start_end_time_of_each_station():
    '''start time and end time of each station'''
    url = 'http://map.baidu.com/?qt=inf&newmap=1&it=3&uid=3d00aa624525bbe9c5f50dcc&ie=utf-8&f=[1,12,13]&c=131&m=sbw&ccode=131&t=14148457164491414845716449'
    s = requests.session().cookies.set_cookie('BAIDUID=57A3D76B9D0B6E63ED76649FA81E3B30:FG=1; BAIDUPSID=57A3D76B9D0B6E63ED76649FA81E3B30; BDUSS=nJlcm1nMXY1TWR5Nm91S0RacWRxVWtoNGVGLWJuREtLOWhJMlR0azVaSUhRSE5VQVFBQUFBJCQAAAAAAAAAAAEAAADrlDsL0-~ErL6y0PoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAezS1QHs0tUV; H_PS_PSSID=6766_1446_7802_9499_6504_9509_6018_9619_9532_9478_7799_9454_9193_9024_9188; bus_time_tip=1; busCmsAd=2; Maptodowntip=2; BDRCVFR[u4lWRKtRdYC]=mk3SLVN4HKm; ci_session=a%3A4%3A%7Bs%3A10%3A%22session_id%22%3Bs%3A32%3A%2209fb7ca3e7059d83c8a3cb5283551117%22%3Bs%3A10%3A%22ip_address%22%3Bs%3A11%3A%2210.57.29.73%22%3Bs%3A10%3A%22user_agent%22%3Bs%3A50%3A%22Mozilla%2F5.0+%28X11%3B+Ubuntu%3B+Linux+i686%3B+rv%3A24.0%29+Gec%22%3Bs%3A13%3A%22last_activity%22%3Bi%3A1414843716%3B%7Df77e35d8ae56754985feb45be3bc6c54')
    print s.get(url).text
# start_end_time_of_each_station()


def get_all_station_name():
    '''get all station from official net'''
    url = 'http://www.bjsubway.com/station/xltcx/'
    r = requests.get(url)
    r.encoding = 'gb2312'
    html = r.text
    soup = BeautifulSoup(html)
    div_list = soup.find_all('div', class_='station')
    station_list = set([item.text.strip() for item in div_list])
    subway_filename = os.path.join(PATH, 'station_names')
    codecs.open(subway_filename, mode='wb', encoding='utf-8').writelines([item+'\n' for item in station_list])

# get_all_station_name()

def get_station_pair():
    '''return all station pair N*(N-1)/2, write into file: total_station_pair_name'''
    subway_filename = os.path.join(PATH, 'station_names')
    station_pair_set = set()
    with codecs.open(subway_filename, encoding='utf-8')as f:
        line_list = [item.strip() for item in f.readlines()]
        list_lenght = len(line_list)
        for index in range(list_lenght):
            station = line_list[index]
            for i in range(index, list_lenght):
                com_station = line_list[i]
                station_pair_set.add((station, com_station))
    # print len(station_pair_set)
    com_str_list = ['\t'.join(item)+'\n' for item in station_pair_set]
    station_pair_filename = os.path.join(PATH, 'total_station_pair_name')
    codecs.open(station_pair_filename, mode='wb', encoding='utf-8').writelines(com_str_list)
    # return station_pair_set
# get_station_pair()


def failed_crawled_station():
    '''crawl failed station for the second time'''
    failed_station_list = []
    filename = os.path.join(PATH, 'failed_crawled_station')
    with open(filename) as f:
        for line in f.readlines():
            splited_line = line.split('\t')
            start = splited_line[0]
            end = splited_line[1].strip()
            if start != end:
                failed_station_list.append(line)
    # print len(failed_station_list)
    return failed_station_list
# failed_crawled_station()

def crawl_distance_bewteen_two_station():
    station_pair_filename = os.path.join(PATH, 'failed_crawled_station2')
    start_end_distance_filename = os.path.join(PATH, 'start_end_distance')
    failed_cralwd_filename = os.path.join(PATH, 'failed_crawled_station3')
    with codecs.open(station_pair_filename) as f, \
    codecs.open(start_end_distance_filename, mode='a') as wf,\
    codecs.open(failed_cralwd_filename, mode='a') as failed_obj:
        count = 0
        for line in f.readlines():
            count += 1
            splited_line = line.split('\t')
            start = splited_line[0]
            end = splited_line[-1].strip()
            if start == end:
                continue
            distance = get_distance_from_baidu(start, end)
            if distance:
                print count, start, end, distance
                com_str = '\t'.join((start, end, str(distance))) + '\n'
                wf.write(com_str)
                time.sleep(2)
            else:
                print count, start, end, 'crawled failed...'
                failed_obj.write(line)
                time.sleep(2)
crawl_distance_bewteen_two_station()
