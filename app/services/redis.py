import redis
import json
from urllib.parse import urlparse
from app.app import user_status
from app.config import settings

# Initialize a Redis client
url = urlparse(settings.REDIS_URL)
redis_client = redis.StrictRedis(
    host=url.hostname,
    port=url.port,
    password=url.password,
)


# Save the user_state in Redis with a TTL of 1 day (86400 seconds)
def save_user_state(user_id, state):
    if settings.CONFIG_TYPE == "BaseConfig":  # 只有在local才使用全域變數存
        user_status[user_id] = state
    else:
        redis_client.set(user_id, json.dumps(state), ex=86400)  # 86400 seconds = 1 day


# Retrieve the user_state from Redis
def get_user_state(user_id):
    if settings.CONFIG_TYPE == "BaseConfig":  # 只有在local才使用全域變數存
        return user_status.get(user_id, {})
    else:
        state = redis_client.get(user_id)
        if state:
            return json.loads(state)
        return {}
