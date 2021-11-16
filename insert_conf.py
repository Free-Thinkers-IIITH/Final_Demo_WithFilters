import json
from pymongo import MongoClient, InsertOne

client = MongoClient('mongodb+srv://root:root@cluster0.4g04r.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = client.paper_db
collection = db.conferences
requesting = []

with open('ranks.json') as f:
    for conf in json.load(f):
        temp = dict()
        temp["name"] = conf["Acronym"] + " " +conf["Standard Name"]
        temp["rank"] = conf["Rank"]
        requesting.append(InsertOne(temp))

result = collection.bulk_write(requesting)
client.close()
        

