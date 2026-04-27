# Model Card: VibeMatch 2.0 — AI Music Recommender with RAG

## 1. Model / System Name

**VibeMatch 2.0**

Extended from VibeMatch 1.0 (Module 2). The original system used a fully rule-based scoring formula with fixed weights (genre, mood, energy, acousticness) to rank songs from a static 18-track catalog. VibeMatch 2.0 replaces the structured-input interface with a natural language RAG pipeline powered by Claude Haiku.

---

## 2. Goal / Task

Accept a plain-English description of what the user is in the mood for, retrieve the most relevant songs from the catalog, and ask Claude to generate grounded recommendations with explanations and a self-reported confidence score. The system also includes input guardrails, structured logging, and an automated evaluation harness.

---

## 3. Intended and Non-Intended Use

**Intended for:** learning and classroom demonstration of RAG architecture, prompt design, input validation, and AI evaluation patterns.

**Not intended for:** production music services, real user data pipelines, or any context where a poor recommendation has meaningful consequences. The catalog is 18 songs — results are illustrative, not competitive with real recommenders.

---

## 4. System Architecture Summary

The pipeline runs in three stages:

1. **Guardrails** — `src/guardrails.py` rejects empty, too-short (< 3 chars), or overlong (> 500 chars) input before any API call is made.
2. **Retrieval** — `src/rag_recommender.retrieve_songs()` keyword-scores all 18 catalog songs against the user query using genre, mood, energy direction, and acoustic cues. Returns top 10 candidates.
3. **Generation** — `src/rag_recommender.ask_claude()` sends the retrieved context plus the user query to `claude-haiku-4-5-20251001`. The system prompt is cached with `cache_control: ephemeral`. Claude returns top 3 picks, plain-language explanations, a confidence score (0.0–1.0), and a confidence reason.

Logging (`src/logger.py`) writes every step to `logs/vibematch_YYYYMMDD.log`.

---

## 5. Data Used

18-song catalog in `data/songs.csv`. Each entry has: title, artist, genre, mood, energy (0–1), tempo BPM, valence, danceability, acousticness.

Genres represented: pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, R&B, classical, Latin, country, reggae, metal, k-pop.

Genre coverage is uneven — pop and lofi each have multiple songs; most other genres have exactly one. This directly affects recommendation quality for users outside the pop/lofi space.

---

## 6. Strengths

- Retrieval grounds every response in real catalog entries — Claude cannot hallucinate song titles that are not in the retrieved set.
- Confidence scores are well-calibrated without explicit instructions to match catalog coverage. Thin-catalog genres (rock, classical) consistently produce lower confidence than well-covered ones.
- The guardrail layer prevents malformed input from reaching the API at all.
- Prompt caching reduces token cost on repeated queries within the same session.

---

## 7. Limitations and Biases

**Genre imbalance:** Pop and lofi users get high-quality, confident results. Rock, jazz, classical, and most other genre users get a strong #1 and then fall back on energy-only matches — the system is honest about this via low confidence scores, but the experience is still weaker.

**Keyword-based retrieval:** Retrieval scores by keyword presence, not semantic similarity. A query like "music that feels like rain" gets no retrieval signal because "rain" is not a genre or mood label. Embedding-based retrieval would handle this better.

**Fixed scoring weights:** The retrieval scoring encodes assumptions (genre > mood > energy > acousticness) that may not match every user's actual priorities.

**No memory:** The system treats every query as independent. A follow-up like "something less chill" has no access to what was previously recommended.

**Misuse potential:** The RAG pattern itself is low-stakes here, but the same architecture applied to health, legal, or financial advice could mislead users who over-trust AI-generated outputs without knowing the retrieval corpus is limited. The confidence score + confidence reason is the mitigation: surfacing uncertainty is the first line of defense.

---

## 8. Evaluation Results

**Unit tests (pytest):** 2 / 2 passed — core sorting logic and explanation generation.

**Evaluation harness (evaluate.py):** 8 / 8 passed across 5 RAG cases and 3 guardrail cases.

| Case | Result | Confidence |
|------|--------|-----------|
| Happy pop / high energy | PASS | 0.88 |
| Lofi study session | PASS | 0.92 |
| Rock / intense workout | PASS | 0.55 |
| Romantic dinner | PASS | 0.72 |
| Classical / peaceful | PASS | 0.48 |
| Empty input (guardrail) | PASS | n/a |
| Too-short input (guardrail) | PASS | n/a |
| Overlong input (guardrail) | PASS | n/a |

**Average confidence (RAG cases only):** 0.71

**What worked:** Guardrail rejections were 100% reliable. Lofi and pop cases scored highest confidence, matching actual catalog coverage depth.

**What struggled:** Rock (0.55) and classical (0.48) reflect genuine catalog thinness, not model failure. The system correctly signals its own uncertainty.

**Surprise:** Claude's confidence scores were self-calibrating without explicit instruction. When only one rock song existed in retrieved context, it returned 0.55 unprompted. That calibration behavior was not engineered — it emerged from the model reasoning about the context it received.

---

## 9. AI Collaboration

**One helpful suggestion from Claude:**
Claude suggested adding `cache_control: ephemeral` to the system prompt to avoid re-paying full input token cost on every query within a session. This was not part of the original plan — the original design sent the full system prompt on every call. The caching suggestion improved cost efficiency meaningfully for multi-turn sessions and was adopted directly.

**One flawed suggestion from Claude:**
The first version of `retrieve_songs()` that Claude generated used exact string equality for genre matching (`song["genre"] == query_genre`). This silently broke retrieval for "hip-hop" vs. "hip hop" and "r&b" vs. "rnb" — the matching returned zero genre hits for those entries even when the user explicitly asked for them. The bug was caught by running the evaluation harness and tracing which songs were absent from retrieval results, then fixed by adding string normalization (lowercasing and stripping hyphens/spaces) before comparison.

---

## 10. Ideas for Improvement

- **Embedding-based retrieval** to handle semantic queries that don't map to genre/mood keywords.
- **Catalog expansion** — particularly rock, jazz, classical, and non-Western genres — to reduce confidence gaps across user profiles.
- **Conversation memory** so follow-up queries can reference prior recommendations.
- **Valence and danceability** in both retrieval scoring and the user-facing prompt, so emotionally distinct songs with similar energy levels score differently.
- **User feedback loop** — thumbs up/down on recommendations to adjust retrieval weights over time.
