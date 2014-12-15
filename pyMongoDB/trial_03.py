#!/usr/bin/env python2

'''
PyMongo API Documentation:
http://api.mongodb.org/python/current/index.html
'''

# Trial 03 - Aggregation


# because of python dictionaries don't maintain order,
# you should use son or collections.OrderedDict
# where explicit ordering is required e.g. "$sort"
from bson.son import SON as son
from pymongo import MongoClient as client

db = client().demo

db.animals.insert({"x": 1, "tags": ["dog", "cat"]})
db.animals.insert({"x": 2, "tags": ["cat"]})
db.animals.insert({"x": 3, "tags": ["mouse", "cat", "dog"]})
db.animals.insert({"x": 4, "tags": []})

db.animals.aggregate([{"$unwind": "$tags"},
                   {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
                   {"$sort": son([("count", -1), ("_id", -1)])}])

'''
result:
{u'ok': 1.0,
 u'result':
        [
            {u'_id': u'cat', u'count': 3},
            {u'_id': u'dog', u'count': 2},
            {u'_id': u'mouse', u'count': 1}
        ]
}
'''
