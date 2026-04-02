# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeMatch 1.0**

---

## 2. Intended Use

VibeMatch suggests songs from a small catalog based on a user's preferred genre, mood, and energy level. It also optionally favors acoustic-leaning tracks for users who prefer that sound.

This system is built for classroom exploration only. It assumes the user can express their preferences in simple terms — a favorite genre, a favorite mood, and a rough sense of how high or low energy they want. It is not designed for real production use.

---

## 3. How the Model Works

Every song in the catalog gets a score based on how well it matches what the user told us they like. The scoring works like this:

- If the song's genre matches the user's favorite, it gets a significant boost — genre is the strongest signal.
- If the song's mood matches (happy, chill, intense, etc.), it gets a moderate boost.
- The closer the song's energy level is to what the user wants, the more points it earns — a perfect match adds a full point, a wide miss adds almost none.
- For users who prefer acoustic-sounding music, songs with a high acousticness rating get a small additional bonus.

After every song is scored, they are ranked highest to lowest and the top results are returned as recommendations. The system also generates a plain-language sentence for each recommendation explaining which factors contributed to the match.

---

## 4. Data

The catalog contains 10 songs stored in `data/songs.csv`. Each song has the following attributes: title, artist, genre, mood, energy (0 to 1), tempo in BPM, valence (musical positivity, 0 to 1), danceability (0 to 1), and acousticness (0 to 1).

Genres represented: pop, lofi, rock, ambient, jazz, synthwave, indie pop.
Moods represented: happy, chill, intense, relaxed, focused, moody.

The dataset was not modified from the starter — no songs were added or removed.

There are noticeable gaps. Latin, hip-hop, R&B, classical, and country are entirely absent. The mood vocabulary is small — nuanced states like "nostalgic," "angry," or "romantic" are not represented. The catalog also skews toward Western contemporary styles, which means users whose taste lives outside that space will consistently get poor matches regardless of their stated preferences.

---

## 5. Strengths

The system works best for users whose taste aligns with the most common entries in the catalog — particularly pop and lofi listeners. A user who says they love pop, want happy vibes, and have high energy will reliably surface "Sunrise City" first, which is genuinely the closest match by every relevant attribute.

The scoring is fully transparent. Every recommendation comes with a plain-language explanation, and the logic is simple enough that a user could manually verify it. That kind of interpretability is something real recommenders often sacrifice in exchange for accuracy.

The energy-closeness calculation is smooth rather than binary. A song does not have to be an exact energy match to earn points — it earns proportionally more the closer it gets. This prevents harsh cliffs in the rankings.

---

## 6. Limitations and Bias

Genre is weighted twice as heavily as mood and significantly more than energy. This means a genre-matching song with a mismatched mood will almost always outrank a mood-matching song in a different genre — even when the user might actually prefer the mood match. The weight choice is a design assumption, not a measured preference.

Valence, danceability, and tempo are collected in the dataset but completely ignored in scoring. A user who says they want high energy and gets a high-energy song that is also low valence (emotionally flat) may be disappointed, and the system has no way to account for that.

The 10-song catalog makes ties and thin results likely. A user whose preferred genre does not appear in the catalog (e.g., hip-hop) will never get a genre match and will only be differentiated by energy closeness — which is a weak signal on its own.

The catalog itself reflects a narrow slice of musical culture. If most of the songs represent one demographic's taste, users from other backgrounds will be systematically underserved — not because the algorithm is wrong, but because the data never represented them.

---

## 7. Evaluation

Three user profiles were tested manually:

**Profile 1 — Pop / Happy / High Energy (0.8) / Not Acoustic**
Results: "Sunrise City" ranked first with a score near 4.0, "Gym Hero" second. Both are genuinely good matches. The system behaved as expected.

**Profile 2 — Lofi / Chill / Low Energy (0.35) / Acoustic**
Results: "Library Rain" and "Midnight Coding" ranked at the top. Both are lofi, chill, and acoustic — a strong match. The acoustic bonus meaningfully separated them from ambient and jazz tracks with similar energy.

**Profile 3 — Jazz / Relaxed / Medium Energy (0.5) / Acoustic**
Results: "Coffee Shop Stories" ranked first, which is correct. However, after that first match, the fallback results were ambient and lofi tracks — the catalog simply has very few jazz or relaxed-mood songs. The system cannot manufacture diversity that the data does not contain.

The two automated tests (sorting correctness and explanation non-emptiness) both pass.

---

## 8. Future Work

- **Incorporate valence and danceability** into scoring. A user who wants to dance should get danceable songs, even if the genre or mood label is slightly off.
- **Add user weighting controls** so a user can say "genre matters most to me" or "I really care about energy" and the system adjusts its weights accordingly.
- **Expand the catalog** significantly, and ensure it covers a wider range of genres, moods, and cultural styles.
- **Improve diversity** in results. The current system can return five songs that are nearly identical. A better version would balance similarity with variety so the user is not trapped in a narrow corner of the catalog.
- **Support listening history** as input. Instead of asking users to describe their preferences, infer them from what they have actually played.

---

## 9. Personal Reflection

Building this made it concrete how much a recommender depends on the quality and coverage of its data. The scoring logic can be well-designed, but if the catalog does not include songs that match a user's actual taste, no algorithm can fix that. The system is only as good as what it has to work with.

It also surfaced how many invisible design decisions go into something that feels simple. Choosing to weight genre twice as heavily as mood is an assumption about human taste — and it might be wrong for many users. Real recommenders at scale face the same problem, just with millions of parameters instead of four. That makes interpretability and the ability to explain "why did you recommend this" much harder to maintain, and much more important to try.
