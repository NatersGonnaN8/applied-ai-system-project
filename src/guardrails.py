"""
Input guardrails for VibeMatch.

validate_input() is the single entry point. It returns (ok, error_message).
If ok is False, the caller should surface error_message to the user and
skip the RAG pipeline entirely.
"""


def validate_input(text: str) -> tuple[bool, str]:
    """
    Validate a raw user preference string before sending it to the RAG pipeline.

    Returns:
        (True, "")           — input is acceptable
        (False, <message>)   — input was rejected; message explains why
    """
    if not text or not text.strip():
        return False, "Please describe what you're in the mood for."

    stripped = text.strip()

    if len(stripped) < 3:
        return False, "That's too short — try describing your mood or vibe a bit more."

    if len(stripped) > 500:
        return False, (
            f"Input is too long ({len(stripped)} characters). "
            "Please keep it under 500 characters."
        )

    return True, ""
