import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Song:
    """Represents a single song and its audio feature attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Stores a user's music taste preferences used for scoring songs."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


# ---------------------------------------------------------------------------
# Functional API (used by main.py)
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file, converting numeric columns to floats."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a single song against user preferences; return (score, reasons)."""
    score = 0.0
    reasons = []

    if song.get("genre") == user_prefs.get("genre"):
        score += 2.0
        reasons.append(f"genre match: {song['genre']} (+2.0)")

    if song.get("mood") == user_prefs.get("mood"):
        score += 1.0
        reasons.append(f"mood match: {song['mood']} (+1.0)")

    target_energy = user_prefs.get("energy", 0.5)
    energy_diff = abs(song["energy"] - target_energy)
    energy_score = round(1.0 - energy_diff, 2)
    score += energy_score
    reasons.append(f"energy closeness: {song['energy']:.2f} vs target {target_energy:.2f} (+{energy_score:.2f})")

    if user_prefs.get("likes_acoustic") and "acousticness" in song:
        acoustic_bonus = round(float(song["acousticness"]) * 0.5, 2)
        score += acoustic_bonus
        reasons.append(f"acoustic bonus: acousticness {float(song['acousticness']):.2f} (+{acoustic_bonus:.2f})")

    if not reasons:
        reasons.append("reasonable overall match")

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, List[str]]]:
    """Score all songs, sort highest to lowest, and return the top k results."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, reasons))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]


# ---------------------------------------------------------------------------
# OOP API (used by tests/test_recommender.py)
# ---------------------------------------------------------------------------

def _score_song_obj(song: Song, user: UserProfile) -> float:
    """Compute a numeric match score between a Song dataclass and a UserProfile."""
    score = 0.0

    if song.genre == user.favorite_genre:
        score += 2.0

    if song.mood == user.favorite_mood:
        score += 1.0

    score += 1.0 - abs(song.energy - user.target_energy)

    if user.likes_acoustic:
        score += song.acousticness * 0.5

    return score


class Recommender:
    """OOP wrapper around the recommendation logic; required by the test suite."""

    def __init__(self, songs: List[Song]):
        """Initialize the recommender with a catalog of Song objects."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k songs ranked by match score for the given user."""
        return sorted(self.songs, key=lambda s: _score_song_obj(s, user), reverse=True)[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation of why a song was recommended."""
        reasons = []

        if song.genre == user.favorite_genre:
            reasons.append(f"genre matches your favorite ({song.genre})")

        if song.mood == user.favorite_mood:
            reasons.append(f"mood matches your preference ({song.mood})")

        if abs(song.energy - user.target_energy) <= 0.15:
            reasons.append(f"energy level is close to your target ({song.energy:.2f})")

        if user.likes_acoustic and song.acousticness >= 0.6:
            reasons.append(f"acoustic feel you enjoy (acousticness: {song.acousticness:.2f})")

        if not reasons:
            reasons.append("overall profile is a reasonable match")

        return "Recommended because: " + ", ".join(reasons) + "."