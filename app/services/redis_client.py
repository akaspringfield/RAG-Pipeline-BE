# import redis
# from app.config import Config

# try:
#     redis_client = redis.Redis(
#         host=Config.REDIS_HOST,
#         port=Config.REDIS_PORT,
#         db=0,
#         decode_responses=True
#     )

#     redis_client.ping()  # test connection

# except Exception:
#     redis_client = None
#     print("⚠️ Redis is not running. Caching disabled.")
import redis
from app.config import Config

try:
    redis_client = redis.Redis(
        host=getattr(Config, "REDIS_HOST", "localhost"),
        port=getattr(Config, "REDIS_PORT", 6379),
        db=getattr(Config, "REDIS_DB", 0),
        decode_responses=True
    )

    # test connection
    redis_client.ping()

except Exception as e:
    print("⚠️ Redis not connected:", e)
    redis_client = None