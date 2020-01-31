import redis
import hashlib
import json


class RedisHandler:
    def __init__(self, redisConnection):
        self.redisConnection = redisConnection


    def addData(self, uid, author, publisher, title, publishDate, share):
        pubID = self.redisConnection.hlen(uid)
        print(share, flush=True)
        obj = {"author": author, "publisher": publisher, "title": title, "publishDate": publishDate, "share": share, "pubID": pubID}
        objToStore = json.dumps(obj)
        self.redisConnection.hset(uid, pubID, objToStore)
        return pubID

    def updateData(self, pid, uid, author, publisher, title, publishDate, share):
        obj = {"author": author, "publisher": publisher, "title": title, "publishDate": publishDate, "share": share, "pubID": pid}
        objToStore = json.dumps(obj)
        self.redisConnection.hset(uid, pid, objToStore)

    def getList(self, uid):
        data = self.redisConnection.hgetall(uid)
        listData = {}
        for id, stringData in data.items():
            listData[id] = json.loads(stringData).get('title')
        if self.redisConnection.hget("accessToPublication", uid) is not None:
            sharePublications = json.loads(self.redisConnection.hget("accessToPublication", uid))
            extraPublications = {}
            for pubOwner, publicationToShare in sharePublications.items():
                oneOwnerPublications = {}
                for publication in publicationToShare:
                    pub = json.loads(self.getData(pubOwner, publication))
                    pub = json.loads(pub)
                    oneOwnerPublications[pub['pubID']] = {"title": pub['title']}
                extraPublications[pubOwner] = oneOwnerPublications
            extraPublications = {"extraPublications": extraPublications}
            listData.update(extraPublications)
        return listData

    def removeAccess(self, guest, owner, ownerPub):
        shareList = self.redisConnection.hget('accessToPublication', guest)
        shareList = json.loads(shareList)
        shareList.get(owner).remove(ownerPub)
        self.redisConnection.hset('accessToPublication', guest, json.dumps(shareList))

    def setAccess(self, guest, owner, ownerPub):
        if self.redisConnection.hget('accessToPublication', guest) is None:
            self.redisConnection.hset('accessToPublication', guest, json.dumps({}))
        shareList = self.redisConnection.hget('accessToPublication', guest)
        shareList = json.loads(shareList)
        if shareList.get(owner) is None:
            shareList[owner] = [ownerPub]
        else:
            shareList.get(owner).append(ownerPub)
        self.redisConnection.hset('accessToPublication', guest, json.dumps(shareList))

    def getData(self, uid, pubID):
        data = self.redisConnection.hget(uid, pubID)
        return json.dumps(data)

    def deleteData(self, uid, pubID):
        self.redisConnection.hdel(uid, pubID)

    def deleteData(self, uid, pubID):
        self.redisConnection.hdel(uid, pubID)

    def postMessage(self, uid, message):
        self.redisConnection.publish(uid, message)


