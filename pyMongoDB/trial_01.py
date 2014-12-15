#!/usr/bin/env python2

'''
PyMongo API Documentation:
http://api.mongodb.org/python/current/index.html
'''

# Trial 01

import pymongo
import datetime


def testOperation(data, col='blog', dbname='test', server='127.0.0.1:27017'):
    '''
    function inserts a document to specified collection

    input:
        data : dict([j/b]son strings)
        col : collection
        dbname : databse
        server : mongodb server address and listen port

    returns the inserted data's "_id" field.
    '''
    ip_addr, port = server.split(':')
    client = pymongo.MongoClient(ip_addr, int(port))
    db = client[dbname]
    collection = db[col]
    return collection.insert(data)


if __name__ == '__main__':

    post = {'author': 'Chu',
            'text': 'My first post.',
            'tags': ['mongodb', 'python', 'pymongo'],
            'date': datetime.datetime.utcnow()}

    print testOperation(post, 'blog', 'demo', '10.0.0.10:27017')
