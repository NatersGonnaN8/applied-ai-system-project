# Reflection: Profile Comparisons

## Profile 1 vs. Profile 2 — High-Energy Pop vs. Chill Lofi / Acoustic

The contrast here is almost total. "Sunrise City" dominates Profile 1 with a score of 3.97 while it doesn't appear anywhere in Profile 2's top 5. The lofi profile's top two results ("Library Rain" and "Midnight Coding") are locked together by three matching signals — genre, mood, and near-perfect energy — with the acoustic bonus adding meaningful separation between them. Profile 1 has no acoustic bonus in play, so after the top 2 pop matches the fallback results (Rooftop Lights, Calor de Verano) are held up purely by mood or energy proximity. That shift makes sense: a chill acoustic user and a high-energy pop user want genuinely different things, and the scoring reflects it.

## Profile 2 vs. Profile 3 — Chill Lofi / Acoustic vs. Deep Intense Rock

Both profiles produce a clean, confident #1 result (Library Rain at 4.43, Storm Runner at 3.99) — the catalog happens to have good coverage for both. The difference shows up in positions 2–5. Profile 2 stays coherent: all five results are genuinely low-energy, acoustic-leaning tracks. Profile 3 falls off sharply after #1 — positions 2 and 3 (Gym Hero, Iron Curtain) only matched on mood and energy, not genre, meaning the score dropped from ~4.0 to ~2.0. That gap reveals how much genre weight carries the top result. When the catalog only has one rock song, the recommender is right about #1 but uncertain about everything below it.

## Profile 1 vs. Profile 3 — High-Energy Pop vs. Deep Intense Rock

Both profiles target high energy (0.85 and 0.92 respectively), so the energy-closeness scores are similar across their results. The key differentiator is genre and mood. Profile 1 rewards happy vibes; Profile 3 rewards intensity. "Gym Hero" appears second on both lists — which is telling. It is a pop song with high energy and an "intense" mood, so it earns a mood match for rock/intense and a genre match for pop. This shows how a song can be a strong #2 for two very different users when it straddles multiple feature categories. It also hints at a limitation: the system has no way to know that a "Gym Hero" pop track and a "Storm Runner" rock track feel very different to a listener, even when the numbers are close.
