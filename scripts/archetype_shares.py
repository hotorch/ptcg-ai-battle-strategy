#!/usr/bin/env python3
"""deck-stats --out JSON 덤프를 아키타입별 셰어로 전량 집계한다 (분모 = 덱-게임 수 = 2×에피소드).

검증: 2026-08-12 덤프로 top-agent-observation.md 결과 1 수치 정확 재현 (8/16).
사용: uv run python scripts/archetype_shares.py <decks_YYYY-MM-DD.json> [...]
"""
import json
import sys

ARCHETYPES = [
    ("Dragapult", lambda c: {119, 120, 121} <= c),
    ("Grimmsnarl", lambda c: {646, 647, 648} <= c),
    ("Alakazam", lambda c: {741, 742, 743} <= c),
    ("Meganium/TapuBulu", lambda c: {709, 917} <= c),
    ("Slowking", lambda c: {162, 163} <= c),
    ("MegaLucario", lambda c: {673, 678} <= c),
    ("Unknown-848line", lambda c: {848, 849} <= c),
]


def classify(cards: set) -> str:
    for name, rule in ARCHETYPES:
        if rule(cards):
            return name
    return "기타"


def main(path: str) -> None:
    with open(path, encoding="utf-8") as f:
        rows = json.load(f)
    total_games = sum(r["games"] for r in rows)
    agg: dict = {}
    for r in rows:
        cards = {cid for cid, _n in r["signature"]}
        name = classify(cards)
        a = agg.setdefault(name, {"games": 0, "wins": 0})
        a["games"] += r["games"]
        a["wins"] += r["wins"]
    print(f"{path}: total deck-games={total_games} (episodes~{total_games // 2})")
    for name, a in sorted(agg.items(), key=lambda kv: -kv[1]["games"]):
        share = 100.0 * a["games"] / total_games
        wr = 100.0 * a["wins"] / a["games"]
        print(f"  {name:20s} share={share:5.1f}%  win={wr:4.1f}%  games={a['games']}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        main(p)
