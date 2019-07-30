import redis
import config

_redis = None

def init_redis():
    global _redis

    _redis = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0)

    return _redis
