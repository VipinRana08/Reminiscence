import uuid
from databases.postgres_db import save_conversation, ensure_user_exists
from databases.redis_db import add_short_term_memory, update_user_profile
from databases.vector_db import save_embedding


def store_interaction(
    user_id: str,
    session_id: str,
    user_message: str,
    ai_response: str
):
    """
    Saves everything after LLM responds.
    Writes to all 3 databases.
    """

    # Make sure user exists in PostgreSQL
    ensure_user_exists(user_id)

    # Save raw conversation to PostgreSQL
    save_conversation(user_id, session_id, user_message, ai_response)

    # Update short term memory in Redis
    add_short_term_memory(user_id, user_message, ai_response)

    # Save embedding to ChromaDB
    combined_text = f"User: {user_message} AI: {ai_response}"
    embedding_id = str(uuid.uuid4())
    save_embedding(user_id, embedding_id, combined_text)

    # Update user profile
    existing_profile = {}
    from databases.redis_db import get_user_profile
    existing_profile = get_user_profile(user_id)

    if "message_count" not in existing_profile:
        existing_profile["message_count"] = 0

    existing_profile["message_count"] += 1
    existing_profile["last_message"] = user_message[:100]

    from databases.redis_db import save_user_profile
    save_user_profile(user_id, existing_profile)

    print(f"[Storage] Saved interaction for user {user_id}")