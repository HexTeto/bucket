#!/usr/bin/env python2

'''
PyMongo API Documentation:
http://api.mongodb.org/python/current/index.html
'''

# Trial 02

import pymongo
import datetime


class TrialQuery(object):

    def __init__(self, colname='blog', dbname='test', server='127.0.0.1:27017'):
        ip_addr, port = server.split(':')
        client = pymongo.Connection(ip_addr, int(port))
        db = client[dbname]
        self.col = db[colname]

    def insert(self, data):
        return self.col.insert(data)

    def find_one(self, req=None):
        if req == None:
            return self.col.find_one()
        return self.col.find_one(req)

    def indexing(self, order='A'):
        if order == 'A':
            order = pymongo.ASCENDING
        else:
            order = pymongo.DESCENDING

        self.col.create_index([("date", order)])
        return self.col.find().sort("date").explain()["cursor"]
