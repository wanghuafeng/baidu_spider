__author__ = 'huafeng'
#coding:utf-8
import os
import time
import sys
import codecs

def add_city(filename, city):
    with codecs.open(filename, encoding='utf-8') as f:
        line_list = [item.strip() + '|' + city + '\n' for item in f.readlines()]
    codecs.open(filename, mode='wb', encoding='utf-8').writelines(line_list)
if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 2:
        filename = args[0]
        city = args[1]
        if not os.path.isfile(filename):
            raise ValueError('no such file %s'%filename)
        add_city(filename, city)