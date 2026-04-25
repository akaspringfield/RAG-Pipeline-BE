'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''

import json
from app.services.redis_client import redis_client


CACHE_TTL = 3600  # 1 hour

def get_cache(key):
    if not redis_client:
        return None

    data = redis_client.get(key)
    return None if not data else json.loads(data)


def set_cache(key, value):
    if not redis_client:
        return

    redis_client.setex(key, CACHE_TTL, str(value))