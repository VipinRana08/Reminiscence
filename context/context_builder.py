from config import MAX_CONTEXT_RESULTS


def build_context(context: dict, user_message: str) -> list:
    """
    Takes retrieved memory and assembles it into
    a structured message list for the Claude API.
    Returns a list of messages ready to send.
    """

    system_prompt = _build_system_prompt(context)

    messages = [
        {"role": "user", "content": user_message}
    ]

    return system_prompt, messages


def _build_system_prompt(context: dict) -> str:
    """
    Builds the system prompt by combining all memory
    into one clean readable block for the LLM.
    """

    sections = []

    # Base personality
    sections.append("""You are a helpful personal AI assistant with memory.
You remember past conversations and use them to give better responses.
Be natural, concise, and reference past context when relevant.""")

    # User profile section
    profile = context.get("profile", {})
    if profile:
        sections.append(_format_profile(profile))

    # Short term memory section
    short_term = context.get("short_term_memory", [])
    if short_term:
        sections.append(_format_short_term(short_term))

    # Long term memory from vector search
    similar = context.get("similar_conversations", [])
    if similar:
        sections.append(_format_similar(similar))

    return "\n\n".join(sections)


def _format_profile(profile: dict) -> str:
    """Formats user profile into readable text."""

    lines = ["[USER PROFILE]"]

    if profile.get("name"):
        lines.append(f"Name: {profile['name']}")

    if profile.get("topics"):
        topics = ", ".join(profile["topics"])
        lines.append(f"Frequent topics: {topics}")

    if profile.get("message_count"):
        lines.append(f"Total messages: {profile['message_count']}")

    if profile.get("last_message"):
        lines.append(f"Last message: {profile['last_message']}")

    return "\n".join(lines)


def _format_short_term(short_term: list) -> str:
    """Formats last N messages into readable text."""

    lines = ["[RECENT CONVERSATION]"]

    for entry in short_term[-5:]:
        lines.append(f"User: {entry['user']}")
        lines.append(f"AI: {entry['ai']}")
        lines.append("")

    return "\n".join(lines)


def _format_similar(similar: list) -> str:
    """Formats semantically similar past conversations."""

    lines = ["[RELEVANT PAST MEMORY]"]
    lines.append("These are past conversations related to the current topic:")
    lines.append("")

    for i, conv in enumerate(similar[:MAX_CONTEXT_RESULTS], 1):
        lines.append(f"{i}. {conv}")

    return "\n".join(lines)