"""
VibeMatch RAG — Evaluation Harness

Runs a predefined set of test cases through the full RAG pipeline and prints
a structured pass/fail summary with average confidence scores.

Usage:
    python evaluate.py

Requires:
    ANTHROPIC_API_KEY environment variable to be set.

Exit codes:
    0 — all tests passed
    1 — one or more tests failed (or API key not set)
"""

import os
import sys

import anthropic
from dotenv import load_dotenv

load_dotenv()

from src.recommender import load_songs
from src.rag_recommender import rag_recommend

# ---------------------------------------------------------------------------
# Test suite
# ---------------------------------------------------------------------------

TEST_CASES = [
    {
        "name": "Happy pop / high energy (morning vibes)",
        "query": "I want something upbeat and happy, pop vibes, high energy to start my morning",
        "expect_guardrail_rejection": False,
        "min_confidence": 0.6,
        "expected_keywords": ["pop", "happy"],
    },
    {
        "name": "Lofi study session",
        "query": "something chill and acoustic for studying, low energy lofi",
        "expect_guardrail_rejection": False,
        "min_confidence": 0.6,
        "expected_keywords": ["lofi", "chill"],
    },
    {
        "name": "Rock / intense workout",
        "query": "heavy rock, intense, high energy for working out at the gym",
        "expect_guardrail_rejection": False,
        "min_confidence": 0.4,  # lower threshold — catalog has only 1 rock song
        "expected_keywords": ["rock", "intense"],
    },
    {
        "name": "Romantic dinner",
        "query": "something romantic and smooth for a dinner date, R&B or slow vibes",
        "expect_guardrail_rejection": False,
        "min_confidence": 0.5,
        "expected_keywords": ["romantic"],
    },
    {
        "name": "Classical / peaceful",
        "query": "peaceful classical music, very low energy, almost like background ambience",
        "expect_guardrail_rejection": False,
        "min_confidence": 0.4,
        "expected_keywords": ["classical", "peaceful"],
    },
    # --- Guardrail cases ---
    {
        "name": "Empty input (guardrail)",
        "query": "",
        "expect_guardrail_rejection": True,
        "min_confidence": 0.0,
        "expected_keywords": [],
    },
    {
        "name": "Too-short input (guardrail)",
        "query": "hi",
        "expect_guardrail_rejection": True,
        "min_confidence": 0.0,
        "expected_keywords": [],
    },
    {
        "name": "Overlong input (guardrail)",
        "query": "x" * 501,
        "expect_guardrail_rejection": True,
        "min_confidence": 0.0,
        "expected_keywords": [],
    },
]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def run_evaluation() -> tuple[int, int]:
    """Run all test cases, print results, return (passed, failed) counts."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print(
            "ERROR: ANTHROPIC_API_KEY is not set.\n"
            "Export it first:  export ANTHROPIC_API_KEY=sk-..."
        )
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    songs = load_songs("data/songs.csv")

    print("=" * 65)
    print("  VibeMatch RAG — Evaluation Harness")
    print(f"  Catalog: {len(songs)} songs   |   Test cases: {len(TEST_CASES)}")
    print("=" * 65)

    passed = 0
    failed = 0
    rag_confidences: list[float] = []

    for idx, case in enumerate(TEST_CASES, 1):
        label = case["name"]
        query = case["query"]
        display_query = repr(query) if len(query) <= 60 else repr(query[:57] + "...")

        print(f"\n[{idx}/{len(TEST_CASES)}] {label}")
        print(f"  Query : {display_query}")

        result = rag_recommend(query, songs, client)

        if "error" in result:
            # Guardrail rejection path
            if case["expect_guardrail_rejection"]:
                print(f"  PASS  — guardrail correctly rejected: {result['error']}")
                passed += 1
            else:
                print(f"  FAIL  — unexpected rejection: {result['error']}")
                failed += 1

        else:
            # RAG response path
            confidence = result["confidence"]
            response_lower = result["response"].lower()

            if case["expect_guardrail_rejection"]:
                print(f"  FAIL  — expected guardrail rejection but got a response")
                failed += 1
            elif confidence >= case["min_confidence"]:
                kw_hits = [kw for kw in case["expected_keywords"] if kw in response_lower]
                print(
                    f"  PASS  — confidence: {confidence:.2f}  "
                    f"keywords matched: {kw_hits or 'n/a'}"
                )
                passed += 1
            else:
                print(
                    f"  FAIL  — confidence {confidence:.2f} is below "
                    f"threshold {case['min_confidence']:.2f}"
                )
                failed += 1

            rag_confidences.append(confidence)

    # Summary
    print(f"\n{'=' * 65}")
    print(f"  Results : {passed} passed / {failed} failed / {len(TEST_CASES)} total")
    if rag_confidences:
        avg = sum(rag_confidences) / len(rag_confidences)
        print(f"  Avg confidence (RAG cases only) : {avg:.2f}")
    print("=" * 65)

    return passed, failed


if __name__ == "__main__":
    passed, failed = run_evaluation()
    sys.exit(0 if failed == 0 else 1)
