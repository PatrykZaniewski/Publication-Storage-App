import redis
import hashlib
import os


class RedisHandler:
    def __init__(self, redisConnection):
        self.redisConnection = redisConnection

    def initUser(self):
        self.createUser("test", "123")
        self.createUser("chaberb", "bardzotajnehaslo")
        self.redisConnection.hset('test', 0, '{"author": "a", "publisher": "b", "title": "c", "publishDate": "d", "pubID": 0}')

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

    def checkLogin(self, login):
        if self.redisConnection.hget('account', login) is None:
            return False
        return True

    def getAllUsers(self):
        return self.redisConnection.hkey('account')

    def checkCrudentials(self, login, passwordToCheck):
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
