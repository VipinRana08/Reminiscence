import redis
import json
from config import REDIS_URL, SHORT_TERM_MEMORY_LIMIT

client = redis.from_url(REDIS_URL)


def save_user_profile(user_id, profile: dict):
    """Save or update user profile."""
    client.set(f"profile:{user_id}", json.dumps(profile))


def get_user_profile(user_id):
    """Get user profile. Returns empty dict if not found."""
    data = client.get(f"profile:{user_id}")
    return json.loads(data) if data else {}


def update_user_profile(user_id, key, value):
    """Update a single field in user profile."""
    profile = get_user_profile(user_id)
    profile[key] = value
    save_user_profile(user_id, profile)


def add_short_term_memory(user_id, user_message, ai_response):
    """Keep last N messages in Redis for quick access."""
    key = f"short_term:{user_id}"
    entry = json.dumps({
        "user": user_message,
        "ai": ai_response
    })

    client.rpush(key, entry)

    # Keep only last N messages
    client.ltrim(key, -SHORT_TERM_MEMORY_LIMIT, -1)


def get_short_term_memory(user_id):
    """Fetch last N messages from Redis."""
    key = f"short_term:{user_id}"
    entries = client.lrange(key, 0, -1)
    return [json.loads(e) for e in entries]


def clear_short_term_memory(user_id):
    """Clear short term memory for a user."""
    client.delete(f"short_term:{user_id}")