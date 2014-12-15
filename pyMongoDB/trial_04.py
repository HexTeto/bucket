#!/usr/bin/env python2

'''
PyMongo API Documentation:
http://api.mongodb.org/python/current/index.html
'''

# Trial 04 - Map/Reduce

from pymongo import MongoClient as client
from bson.code import Code as code
from bson.son import SON as son


mapper = code("""
            function() {
                this.tags.forEach(function(z) {
                    emit(z, 1);
                });
            }
            """)

reducer = code("""
            function(key, values) {
                var total = 0;
                for (var i = 0; i < values.length; i++) {
                    total += values[i];
                }
                return total;
            }
            """)


db = client().demo
result = db.animals.map_reduce(mapper, reducer, "myresults")

for doc in result.find():
    print doc


# get more detailed results when desired, by passing full_response=True to map_reduce()
result = db.animals.map_reduce(mapper, reducer, "myresults", full_response=True)

# all of the optional map/reduce parameters are also supported, simply pass them as keyword arguments
result = db.animals.map_reduce(mapper, reducer, "myresults", query={"x": {"$gt": 2}})

# can use SON or collections.OrderedDict to specify a different database to store the result collection
result = db.animals.map_reduce(mapper, reducer, out=son([("replace", "results"), ("db", "outdb")]), full_response=True)

# group() method provides some of the same functionality as SQL’s GROUP BY.
# Simpler than a map reduce you need to provide a key to group by, an initial value for the aggregation and a reduce function.
# group() doesn't work with sharded mongodb configurations.
reducer = code("""
            function(obj, prev) {
                prev.count++;
            }
            """)
result = db.animals.group(key={"x": 1}, condition={}, initial={"count": 0}, reduce=reducer)
