import redis
import hashlib
import json


class RedisHandler:
    def __init__(self, redisConnection):
        self.redisConnection = redisConnection


    def addData(self, uid, author, publisher, title, publishDate):
        #TODO sprawdzac czy nie istnieje juz o takim tytule
        pubID = self.redisConnection.hlen(uid)
        obj = {"author": author, "publisher": publisher, "title": title, "publishDate": publishDate, "pubID": pubID}
        objToStore = json.dumps(obj)
        self.redisConnection.hset(uid, pubID, objToStore)
        return pubID


    def getList(self, uid):
        data = self.redisConnection.hgetall(uid)
        listData = {}
        for id, stringData in data.items():
            listData[id] = json.loads(stringData).get('title')
        return json.dumps(listData)


    def getData(self, uid, pubID):
        data = self.redisConnection.hget(uid, pubID)
        return json.dumps(data)

    def deleteData(self, uid, pubID):
        self.redisConnection.hdel(uid, pubID)


