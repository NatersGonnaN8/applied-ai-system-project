"""
Command line runner for the Music Recommender Simulation.

Run with:  python -m src.main
"""

from src.recommender import load_songs, recommend_songs


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
    print(f"  genre={user_prefs['genre']}  mood={user_prefs['mood']}  "
          f"energy={user_prefs['energy']}  acoustic={user_prefs.get('likes_acoustic', False)}")
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


def main() -> None:
    """Load the song catalog, score it against multiple user profiles, and print ranked results."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    for name, prefs in PROFILES.items():
        run_profile(name, prefs, songs)


if __name__ == "__main__":
    main()