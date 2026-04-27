"""
RAG pipeline for VibeMatch.

Flow:
  1. validate_input()   — guardrail: reject empty/garbage queries
  2. retrieve_songs()   — keyword retrieval from songs.csv catalog
  3. build_context()    — format retrieved songs as structured context
  4. ask_claude()       — send query + context to Claude (with prompt caching)
  5. Return response dict with recommendation text + confidence score

The system prompt is cached with cache_control so repeated queries in a
session avoid re-sending it on every call.
"""

from typing import Any
import anthropic

from src.guardrails import validate_input
from src.logger import get_logger

logger = get_logger()

# ---------------------------------------------------------------------------
# Keyword maps used during retrieval
# ---------------------------------------------------------------------------

MOOD_MAP: dict[str, str] = {
    "chill": "chill",
    "relax": "relaxed",
    "relaxed": "relaxed",
    "happy": "happy",
    "intense": "intense",
    "focus": "focused",
    "focused": "focused",
    "study": "focused",
    "hype": "hype",
    "workout": "hype",
    "pump": "hype",
    "romantic": "romantic",
    "love": "romantic",
    "date": "romantic",
    "peaceful": "peaceful",
    "festive": "festive",
    "party": "festive",
    "melancholic": "melancholic",
    "sad": "melancholic",
    "moody": "moody",
    "excited": "excited",
}

GENRE_KEYWORDS: set[str] = {
    "pop",
    "lofi",
    "lo-fi",
    "rock",
    "ambient",
    "jazz",
    "synthwave",
    "indie",
    "hip-hop",
    "hip hop",
    "r&b",
    "rnb",
    "classical",
    "latin",
    "country",
    "reggae",
    "metal",
    "k-pop",
    "kpop",
}

HIGH_ENERGY_WORDS: set[str] = {
    "high energy",
    "energetic",
    "upbeat",
    "fast",
    "pump",
    "hype",
    "intense",
    "hard",
    "heavy",
    "workout",
    "gym",
}

LOW_ENERGY_WORDS: set[str] = {
    "low energy",
    "slow",
    "soft",
    "quiet",
    "calm",
    "chill",
    "relax",
    "mellow",
    "easy",
    "study",
    "focus",
    "sleep",
}

ACOUSTIC_WORDS: set[str] = {"acoustic", "unplugged", "natural", "warm"}


# ---------------------------------------------------------------------------
# Step 1 — Retrieve
# ---------------------------------------------------------------------------


def retrieve_songs(query: str, songs: list[dict], top_k: int = 10) -> list[dict]:
    """
    Score every song against the user query using keyword matching and return
    the top_k most relevant ones as retrieval context for Claude.

    Scoring:
      +3.0  genre keyword found in query AND matches song genre
      +2.0  mood keyword found in query AND matches song mood
      +1.5  energy direction word found in query (high → favor high-energy songs)
      +1.0  acoustic keyword found in query AND song has high acousticness
    """
    query_lower = query.lower()

    def _score(song: dict) -> float:
        score = 0.0

        # Genre match
        for kw in GENRE_KEYWORDS:
            normalized = kw.replace("-", " ").replace("&", "and")
            song_genre = song["genre"].lower().replace("-", " ").replace("&", "and")
            if kw in query_lower and normalized in song_genre:
                score += 3.0
                break

        # Mood match
        for kw, mood in MOOD_MAP.items():
            if kw in query_lower and mood == song["mood"]:
                score += 2.0
                break

        # Energy direction
        if any(w in query_lower for w in HIGH_ENERGY_WORDS):
            score += float(song["energy"]) * 1.5
        elif any(w in query_lower for w in LOW_ENERGY_WORDS):
            score += (1.0 - float(song["energy"])) * 1.5

        # Acoustic preference
        if any(w in query_lower for w in ACOUSTIC_WORDS):
            score += float(song["acousticness"]) * 1.0

        return score

    ranked = sorted(songs, key=_score, reverse=True)
    return ranked[:top_k]


# ---------------------------------------------------------------------------
# Step 2 — Build context
# ---------------------------------------------------------------------------


def build_context(songs: list[dict]) -> str:
    """Format retrieved songs as a structured block for Claude's user turn."""
    lines = ["Retrieved songs from the VibeMatch catalog:\n"]
    for song in songs:
        lines.append(
            f'- "{song["title"]}" by {song["artist"]}'
            f' | genre: {song["genre"]}'
            f' | mood: {song["mood"]}'
            f' | energy: {song["energy"]}'
            f' | acousticness: {song["acousticness"]}'
            f' | valence: {song["valence"]}'
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Step 3 — Generate via Claude
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """You are VibeMatch, a music recommendation assistant.

You will receive:
1. A natural-language description of what the user is in the mood for.
2. A list of songs retrieved from the catalog that may be relevant.

Your job:
- Pick the top 3 songs from the provided list that best match the user's request.
- Do NOT recommend songs that are not in the provided list.
- Explain in one sentence why each song fits.
- Rate your overall confidence from 0.0 to 1.0 based on how well the catalog matches what the user wants. Low confidence means the catalog doesn't have great matches; high confidence means you found strong fits.

Respond in EXACTLY this format (no extra text before or after):

RECOMMENDATIONS:
1. [Song Title] by [Artist] — [one-sentence reason]
2. [Song Title] by [Artist] — [one-sentence reason]
3. [Song Title] by [Artist] — [one-sentence reason]

CONFIDENCE: [0.0–1.0]
CONFIDENCE_REASON: [one sentence explaining your confidence level]"""


def ask_claude(user_query: str, context: str, client: anthropic.Anthropic) -> dict[str, Any]:
    """
    Send the user query + retrieved context to Claude and parse the response.

    The system prompt uses cache_control so it is only charged once per session
    window rather than on every request.

    Returns:
        {
            "response": str,       full formatted recommendation text
            "confidence": float,   parsed 0.0–1.0 confidence score
            "input_tokens": int,
            "output_tokens": int,
            "cache_read_tokens": int,
        }
    """
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        system=[
            {
                "type": "text",
                "text": _SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"User request: {user_query}\n\n{context}",
            }
        ],
    )

    response_text = message.content[0].text

    # Parse confidence score — default to 0.5 if malformed
    confidence = 0.5
    for line in response_text.splitlines():
        if line.startswith("CONFIDENCE:"):
            try:
                confidence = float(line.split(":", 1)[1].strip())
                confidence = max(0.0, min(1.0, confidence))
            except (ValueError, IndexError):
                pass

    cache_read = getattr(message.usage, "cache_read_input_tokens", 0) or 0

    return {
        "response": response_text,
        "confidence": confidence,
        "input_tokens": message.usage.input_tokens,
        "output_tokens": message.usage.output_tokens,
        "cache_read_tokens": cache_read,
    }


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def rag_recommend(
    user_query: str,
    songs: list[dict],
    client: anthropic.Anthropic,
) -> dict[str, Any]:
    """
    Full RAG pipeline: validate → retrieve → build context → generate.

    Returns either:
        {"error": str, "confidence": 0.0}          — guardrail rejection or API failure
        {"response": str, "confidence": float, ...} — successful recommendation
    """
    # Guardrail
    ok, error_msg = validate_input(user_query)
    if not ok:
        logger.warning("Input rejected by guardrail | reason=%r | input=%r", error_msg, user_query)
        return {"error": error_msg, "confidence": 0.0}

    logger.info("RAG query | input=%r", user_query)

    # Retrieve
    retrieved = retrieve_songs(user_query, songs, top_k=10)
    logger.info("Retrieved %d songs for context", len(retrieved))

    # Build context
    context = build_context(retrieved)

    # Generate
    try:
        result = ask_claude(user_query, context, client)
        logger.info(
            "Claude response | confidence=%.2f | tokens_in=%d | tokens_out=%d | cache_read=%d",
            result["confidence"],
            result["input_tokens"],
            result["output_tokens"],
            result["cache_read_tokens"],
        )
        return result
    except anthropic.APIError as exc:
        logger.error("Claude API error: %s", exc)
        return {"error": f"API error: {exc}", "confidence": 0.0}
