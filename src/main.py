"""
Command line runner for the Music Recommender Simulation.

Run with:  python -m src.main
"""

from src.recommender import load_songs, recommend_songs


def main() -> None:
    """Load the song catalog, score it against a user profile, and print ranked results."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    # Example taste profile — change these to experiment
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    print(f"User profile: genre={user_prefs['genre']}, mood={user_prefs['mood']}, energy={user_prefs['energy']}\n")
    print("=" * 50)

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rank, (song, score, reasons) in enumerate(recommendations, start=1):
        print(f"  {rank}. {song['title']} by {song['artist']}")
        print(f"     Score: {score:.2f}")
        print(f"     Why:")
        for reason in reasons:
            print(f"       - {reason}")
        print()


if __name__ == "__main__":
    main()