from databases.postgres_db import get_recent_conversations
from databases.redis_db import get_user_profile, get_short_term_memory
from databases.vector_db import search_similar


def retrieve_context(user_id: str, user_message: str) -> dict:
    """
    Fetches all relevant memory for a user before sending to LLM.
    Returns a structured context dictionary.
    """

    # Get user profile
    profile = get_user_profile(user_id)

    # Get last 5 messages
    short_term = get_short_term_memory(user_id)

    # Search semantically similar past conversations
    similar_conversations = search_similar(user_id, user_message)

    # Raw conversations
    recent_conversations = get_recent_conversations(user_id, limit=5)

    # Context
    context = {
        "profile": profile,
        "short_term_memory": short_term,
        "similar_conversations": similar_conversations,
        "recent_conversations": [
            {
                "user": row["user_message"],
                "ai": row["ai_response"],
                "timestamp": str(row["timestamp"])
            }
            for row in recent_conversations
        ]
    }

    return context