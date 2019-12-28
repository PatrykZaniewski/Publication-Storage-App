import redis
import hashlib


class RedisHandler:
    def __init__(self, redisConnection):
        self.redisConnection = redisConnection

    def initUser(self):
        self.redisConnection.hset('account', "test", "123")
        self.redisConnection.hset('account', "chaberb", "bardzotajnehaslo")
        self.redisConnection.hset('test', 0, '{"author": "a", "publisher": "b", "title": "c", "publishDate": "d", "pubID": 0}')

    def checkUser(self, login, password):
        if self.redisConnection.hget('account', login) is None:
            return False
        if self.redisConnection.hget('account', login) != password:
            return False
        return True
