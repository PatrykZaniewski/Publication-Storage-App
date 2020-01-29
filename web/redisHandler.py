import redis
import hashlib
import os
import json



class RedisHandler:
    def __init__(self, redisConnection):
        self.redisConnection = redisConnection

    def postMessage(self, uid, message):
        self.redisConnection.publish(uid, message)

    def initUser(self):
        self.redisConnection.set("loginList", json.dumps({}))
        self.createUser("test", "qweqwe123")
        self.createUser("qwe", "qweqwe123")
        self.createUser("qweqwe", "qweqwe123")
        self.createUser("chaberb", "bardzotajnehaslo")
        self.getLoginList()

    def createUser(self, login, password):
        password = password.encode('utf-8')
        saltHistory = "".encode('utf-8')
        for i in range(0, 8):
             salt = os.urandom(16)
             password = hashlib.pbkdf2_hmac(
                 'sha256',
                 password,
                 salt,
                 100000
             )
             saltHistory = saltHistory + salt
        self.redisConnection.hset('account', login, password.hex())
        self.redisConnection.hset('accountSalt', login, saltHistory.hex())
        id = self.redisConnection.hlen('account')
        self.updateLoginList(login, id)

    def updateLoginList(self, login, id):
        loginList = self.redisConnection.get("loginList")
        loginList = json.loads(loginList)
        loginList[id] = login
        self.redisConnection.set("loginList", json.dumps(loginList))

    def getLoginList(self):
        loginDict = self.redisConnection.get("loginList")
        loginDict = json.loads(loginDict)
        loginList = []
        for id, login in loginDict.items():
            loginList.append(login)
        return loginList


    def checkLogin(self, login):
        if self.redisConnection.hget('account', login) is None:
            return False
        return True

    def getAllUsers(self):
        return self.redisConnection.hkey('account')

    def checkCredentials(self, login, passwordToCheck):
        if self.redisConnection.hget('account', login) is None:
            return False
        password = bytes.fromhex(self.redisConnection.hget('account', login))
        saltHistory = bytes.fromhex(self.redisConnection.hget('accountSalt', login))
        passwordToCheck = passwordToCheck.encode('utf-8')
        for i in range(0, 8):
            salt = saltHistory[i*16:i*16+16]
            passwordToCheck = hashlib.pbkdf2_hmac(
                'sha256',
                passwordToCheck,
                salt,
                100000
            )
        if passwordToCheck.hex() != password.hex():
            return False
        return True
