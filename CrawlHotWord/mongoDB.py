# -*- coding: utf-8 -*-
from pymongo import MongoClient
import codecs
class MongoDB:
    def __init__(self):
        self.client = MongoClient('192.168.0.253')
        self.db = self.client['hotword']
        
    def update_word(self,word, source, category,doc):
        update_doc = {'$set': {source + '.' + category: doc}}
        self.db.word.update({'w': word}, update_doc, upsert=True)
        self.db.word.update({'w': word}, {'$inc': {source + '.' + category + '.c': 1}})
        self.db.word.update({'w': word}, {'$inc': {source + '.c': 1}})
