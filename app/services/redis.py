import redis
import json
from urllib.parse import urlparse
from app.config import settings

# Initialize a Redis client
url = urlparse(settings.REDIS_URL)
redis_client = redis.StrictRedis(
    host=url.hostname,
    port=url.port,
    password=url.password,
)

user_status = {}


def reset_user_credits():
    # Reset all user credits to 5 at 00:00
    users = redis_client.keys('user:*')
    for user in users:
        redis_client.set(user, 5)


def get_user_credit(user_id):
    # Get user credit or initialize to 5 if not exists
    credit = redis_client.get(f'user:{user_id}')
    if credit is None:
        redis_client.set(f'user:{user_id}', 5)
        credit = 5
    return int(credit)


def use_credit(user_id):
    # Use 1 credit and return True if successful, False if not enough credits
    current_credit = get_user_credit(user_id)
    if current_credit is not None and int(current_credit) > 0:
        redis_client.decr(f'user:{user_id}')
        return True
    else:
        return False


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
