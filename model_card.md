# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeMatch 1.0**

---

## 2. Goal / Task

Given a user's preferred genre, mood, energy level, and acoustic preference, suggest the top 5 songs from the catalog that best match those preferences. Each suggestion comes with a plain-language explanation of why it was chosen.

---

## 3. Intended and Non-Intended Use

VibeMatch suggests songs from a small catalog based on a user's preferred genre, mood, and energy level. It also optionally favors acoustic-leaning tracks for users who prefer that sound.

This system is built for classroom exploration only. It assumes the user can express their preferences in simple terms — a favorite genre, a favorite mood, and a rough sense of how high or low energy they want. It is not designed for real production use.

**Not intended for:** production music services, real user data, or any context where a poor recommendation has meaningful consequences. The catalog is too small and the scoring too simple to serve as a real product. It should not be used to make claims about what any real listener would enjoy.

---

## 4. Algorithm Summary

Every song in the catalog gets a score based on how well it matches what the user told us they like. The scoring works like this:

- If the song's genre matches the user's favorite, it gets a significant boost — genre is the strongest signal.
- If the song's mood matches (happy, chill, intense, etc.), it gets a moderate boost.
- The closer the song's energy level is to what the user wants, the more points it earns — a perfect match adds a full point, a wide miss adds almost none.
- For users who prefer acoustic-sounding music, songs with a high acousticness rating get a small additional bonus.

After every song is scored, they are ranked highest to lowest and the top results are returned as recommendations. The system also generates a plain-language sentence for each recommendation explaining which factors contributed to the match.

---

## 5. Data Used

The catalog contains 18 songs stored in `data/songs.csv`. Each song has the following attributes: title, artist, genre, mood, energy (0 to 1), tempo in BPM, valence (musical positivity, 0 to 1), danceability (0 to 1), and acousticness (0 to 1).

The original starter dataset had 10 songs. Eight additional songs were added in Phase 2 to improve genre diversity: hip-hop, R&B, classical, Latin, country, reggae, metal, and k-pop.

Genres represented: pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, R&B, classical, Latin, country, reggae, metal, k-pop.
Moods represented: happy, chill, intense, relaxed, focused, moody, hype, romantic, peaceful, festive, melancholic, excited.

Some gaps remain. The mood vocabulary still lacks nuanced states like "nostalgic," "angry," or "euphoric." Most genres are represented by only one song, so a user whose preferred genre is anything other than pop or lofi will get a strong #1 result and then fall back on energy-only matches for the rest of their list.

---

## 6. Strengths

The system works best for users whose taste aligns with the most common entries in the catalog — particularly pop and lofi listeners. A user who says they love pop, want happy vibes, and have high energy will reliably surface "Sunrise City" first, which is genuinely the closest match by every relevant attribute.

The scoring is fully transparent. Every recommendation comes with a plain-language explanation, and the logic is simple enough that a user could manually verify it. That kind of interpretability is something real recommenders often sacrifice in exchange for accuracy.

The energy-closeness calculation is smooth rather than binary. A song does not have to be an exact energy match to earn points — it earns proportionally more the closer it gets. This prevents harsh cliffs in the rankings.

---

## 7. Observed Behavior / Biases

Genre is weighted twice as heavily as mood and significantly more than energy. This means a genre-matching song with a mismatched mood will almost always outrank a mood-matching song in a different genre — even when the user might actually prefer the mood match. The weight choice is a design assumption, not a measured preference.

Valence, danceability, and tempo are collected in the dataset but completely ignored in scoring. A user who says they want high energy and gets a high-energy song that is also low valence (emotionally flat) may be disappointed, and the system has no way to account for that.

The 18-song catalog makes thin results likely for most genres. With only one song per genre for most categories, a user whose preferred genre does not appear among the top entries will get a strong #1 then fall back on energy-only matches for the rest of their list — which is a weak signal on its own.

The catalog itself reflects a narrow slice of musical culture. If most of the songs represent one demographic's taste, users from other backgrounds will be systematically underserved — not because the algorithm is wrong, but because the data never represented them.

---

## 8. Evaluation Process

Three user profiles were tested manually:

**Profile 1 — Pop / Happy / High Energy (0.85) / Not Acoustic**
Results: "Sunrise City" ranked first with a score of 3.97, "Gym Hero" second at 2.92. Both are genuinely good matches. The system behaved as expected. Musically this feels right — Sunrise City is an upbeat pop track that actually sounds like what this profile would want.

**Profile 2 — Lofi / Chill / Low Energy (0.35) / Acoustic**
Results: "Library Rain" (4.43) and "Midnight Coding" (4.28) ranked at the top. Both are lofi, chill, and acoustic — a strong match. The acoustic bonus meaningfully separated them from "Spacewalk Thoughts," which has a high acousticness score but is ambient rather than lofi.

**Profile 3 — Rock / Intense / High Energy (0.92) / Not Acoustic**
Results: "Storm Runner" ranked first at 3.99, a near-perfect match. After that the list drops to 1.99 — the catalog has only one rock song. Positions 2 and 3 (Gym Hero, Iron Curtain) matched on mood and energy only. The system is confident about #1 but essentially guessing after that.

One notable cross-profile surprise: "Gym Hero" appears second on both the Pop and Rock profiles. It is a pop song with an intense mood and high energy, so it earns a genre match for pop and a mood match for rock. That overlap reveals how a single song can be a strong #2 for two very different listeners when it straddles feature categories — which might feel odd to an actual listener who knows the tracks sound nothing alike.

The two automated tests (sorting correctness and explanation non-emptiness) both pass.

---

## 9. Ideas for Improvement

- **Incorporate valence and danceability** into scoring. A user who wants to dance should get danceable songs, even if the genre or mood label is slightly off.
- **Add user weighting controls** so a user can say "genre matters most to me" or "I really care about energy" and the system adjusts its weights accordingly.
- **Expand the catalog** significantly, and ensure it covers a wider range of genres, moods, and cultural styles.
- **Improve diversity** in results. The current system can return five songs that are nearly identical. A better version would balance similarity with variety so the user is not trapped in a narrow corner of the catalog.
- **Support listening history** as input. Instead of asking users to describe their preferences, infer them from what they have actually played.

---

## 10. Personal Reflection

**Biggest learning moment:** How much a recommender depends on data coverage before the algorithm even matters. The scoring logic can be sound, but a catalog with only one rock song will systemically underserve rock listeners regardless of how well the weights are tuned. No weight adjustment fixes missing data.

**Using AI tools:** AI was genuinely useful for generating the expanded CSV quickly — asking it to produce 8 new songs in valid CSV format with diverse genres saved a lot of manual work. Where I had to double-check it was in the scoring logic: the first version it suggested used a raw `energy` difference without clamping, which could have produced negative scores for large gaps. I caught that by tracing a specific example manually before accepting the code.

**What surprised me:** How much the results can "feel" like real recommendations even when the logic is just four arithmetic operations. Running Profile 2 (lofi/chill/acoustic) and seeing Library Rain and Midnight Coding rise to the top felt intuitive — those are genuinely the kind of tracks that profile describes. The system does not know what music sounds like, but the labels and numbers encode enough signal that the output can still feel correct.

**What I'd try next:** Add valence and danceability to the scoring, since right now a high-energy track that feels joyful and one that feels aggressive score identically. That single change would let the system distinguish moods that the current version treats as equivalent.
