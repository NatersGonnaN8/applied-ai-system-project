"""
VibeMatch — Music Recommender with RAG

Two modes:
  python -m src.main              → interactive RAG mode (requires ANTHROPIC_API_KEY)
  python -m src.main --profiles   → original rule-based profile runner (no API key needed)
"""

import argparse
import os
import sys

import anthropic
from dotenv import load_dotenv

load_dotenv()

from src.logger import get_logger
from src.rag_recommender import rag_recommend
from src.recommender import load_songs, recommend_songs

logger = get_logger()

# ---------------------------------------------------------------------------
# Original rule-based profiles (kept for backward compatibility)
# ---------------------------------------------------------------------------

PROFILES = {
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.85,
        "likes_acoustic": False,
    },
    "Chill Lofi / Acoustic": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.35,
        "likes_acoustic": True,
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.92,
        "likes_acoustic": False,
    },
}


def run_profile(name: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Print ranked recommendations for a single named user profile."""
    print(f"\n{'=' * 60}")
    print(f"  Profile: {name}")
    print(
        f"  genre={user_prefs['genre']}  mood={user_prefs['mood']}  "
        f"energy={user_prefs['energy']}  acoustic={user_prefs.get('likes_acoustic', False)}"
    )
    print(f"{'=' * 60}")

    recommendations = recommend_songs(user_prefs, songs, k=k)

    print("\nTop recommendations:\n")
    for rank, (song, score, reasons) in enumerate(recommendations, start=1):
        print(f"  {rank}. {song['title']} by {song['artist']}")
        print(f"     Score: {score:.2f}")
        print(f"     Why:")
        for reason in reasons:
            print(f"       - {reason}")
        print()


def profiles_mode(songs: list) -> None:
    """Run the three original rule-based profiles and print results."""
    print(f"\nLoaded {len(songs)} songs from catalog.")
    for name, prefs in PROFILES.items():
        run_profile(name, prefs, songs)


# ---------------------------------------------------------------------------
# Interactive RAG mode
# ---------------------------------------------------------------------------


def interactive_rag_mode(songs: list, client: anthropic.Anthropic) -> None:
    """
    REPL loop: user describes their vibe in natural language, VibeMatch
    retrieves matching songs and asks Claude to recommend + explain.
    """
    print("\n" + "=" * 60)
    print("  VibeMatch — Natural Language Music Recommender (RAG)")
    print("=" * 60)
    print('  Describe what you\'re in the mood for. Type "quit" to exit.\n')

    logger.info("Interactive RAG session started")

    while True:
        try:
            user_input = input("  What are you in the mood for? > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n  Goodbye!")
            logger.info("Session ended by user (KeyboardInterrupt / EOFError)")
            break

        if user_input.lower() in ("quit", "exit", "q"):
            print("  Goodbye!")
            logger.info("Session ended by user (quit command)")
            break

        result = rag_recommend(user_input, songs, client)

        print()

        if "error" in result:
            print(f"  VibeMatch: {result['error']}")
        else:
            print(result["response"])
            print(f"\n  [confidence: {result['confidence']:.2f}]")

        print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="VibeMatch — Music Recommender with RAG",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python -m src.main                  # interactive RAG mode\n"
            "  python -m src.main --profiles       # rule-based profile runner\n"
        ),
    )
    parser.add_argument(
        "--profiles",
        action="store_true",
        help="Run the 3 built-in rule-based profiles instead of interactive RAG mode.",
    )
    args = parser.parse_args()

    songs = load_songs("data/songs.csv")
    logger.info("Catalog loaded | songs=%d", len(songs))

    if args.profiles:
        profiles_mode(songs)
        return

    # RAG mode — needs API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print(
            "\n[ERROR] ANTHROPIC_API_KEY is not set.\n"
            "\nSet it first:\n"
            "  Mac/Linux : export ANTHROPIC_API_KEY=sk-...\n"
            "  Windows   : set ANTHROPIC_API_KEY=sk-...\n"
            "\nOr run rule-based mode (no API key needed):\n"
            "  python -m src.main --profiles\n"
        )
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    interactive_rag_mode(songs, client)


if __name__ == "__main__":
    main()
