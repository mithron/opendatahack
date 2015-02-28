import pymongo
import json

c = pymongo.MongoClient()
db = c.moscow

for row in json.load(open('schools-suppliers.txt')):
    db.suppliers.insert(row)