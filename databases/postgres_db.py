import psycopg2
from psycopg2.extras import RealDictCursor
from config import POSTGRES_URL


def get_connection():
    return psycopg2.connect(POSTGRES_URL)


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     VARCHAR(50) PRIMARY KEY,
            name        VARCHAR(100),
            created_at  TIMESTAMP DEFAULT NOW()
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id               SERIAL PRIMARY KEY,
            user_id          VARCHAR(50) REFERENCES users(user_id),
            session_id       VARCHAR(100),
            user_message     TEXT,
            ai_response      TEXT,
            timestamp        TIMESTAMP DEFAULT NOW()
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("PostgreSQL tables initialized.")


def save_conversation(user_id, session_id, user_message, ai_response):
    """Save a single conversation turn."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO conversations (user_id, session_id, user_message, ai_response)
        VALUES (%s, %s, %s, %s)
    """, (user_id, session_id, user_message, ai_response))

    conn.commit()
    cursor.close()
    conn.close()


def get_recent_conversations(user_id, limit=10):
    """Fetch last N conversations for a user."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT user_message, ai_response, timestamp
        FROM conversations
        WHERE user_id = %s
        ORDER BY timestamp DESC
        LIMIT %s
    """, (user_id, limit))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def ensure_user_exists(user_id, name="User"):
    """Insert user if not already present."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (user_id, name)
        VALUES (%s, %s)
        ON CONFLICT (user_id) DO NOTHING
    """, (user_id, name))

    conn.commit()
    cursor.close()
    conn.close()