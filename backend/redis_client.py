import os
import redis

# Defaults to 'localhost' if running locally, or uses 'redis' when inside Docker
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
print(f"Connected to Redis at {REDIS_HOST}:6379", r.ping())
