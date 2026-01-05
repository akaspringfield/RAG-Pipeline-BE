from app.services.redis_client import redis_client
from datetime import datetime, timedelta

LIMIT = 20  # messages per minute

# def check_rate_limit(user_id):

#     if redis_client is None:
#         # fallback: allow requests when redis is down
#         return True

# def check_rate_limit(user_id):

#     key = f"rate:{user_id}"
#     count = redis_client.get(key)

#     if count and int(count) >= LIMIT:
#         return False

#     pipe = redis_client.pipeline()
#     pipe.incr(key, 1)
#     pipe.expire(key, 60)
#     pipe.execute()

#     return True


def check_rate_limit(user_id):

    # ---------------- FALLBACK MODE ----------------
    if redis_client is None:
        # Redis down → allow request (fail open)
        return True

    try:
        key = f"rate:{user_id}"
        count = redis_client.get(key)

        if count and int(count) >= LIMIT:
            return False

        pipe = redis_client.pipeline()
        pipe.incr(key, 1)
        pipe.expire(key, 60)
        pipe.execute()

        return True

    except Exception as e:
        print("⚠️ Redis error (fallback enabled):", e)
        # fallback: allow request instead of crashing
        return True