"""Rank agents with a parallel round-robin over both seats."""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import UTC, datetime
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.evaluate import DEFAULT_WORKERS, RUNS, resolve_agent, run_game, wilson_interval


def default_agents() -> list[str]:
    agents = ["random", "first", "."]
    candidates = ROOT / "candidates"
    if candidates.is_dir():
        agents.extend(
            str(path.relative_to(ROOT))
            for path in sorted(candidates.iterdir())
            if (path / "main.py").is_file() and (path / "deck.csv").is_file()
        )
    return agents


def rank(records: list[dict], labels: list[str]) -> dict:
    table: dict[str, dict] = {
        label: {"wins": 0, "games": 0, "errors": 0, "pairs": {}} for label in labels
    }
    for record in records:
        first, second = record["pair"]
        for label, opponent, outcome in (
            (first, second, record["outcome"]),
            (second, first, {"win": "loss", "loss": "win"}.get(record["outcome"], record["outcome"])),
        ):
            entry = table[label]
            pair = entry["pairs"].setdefault(opponent, {"wins": 0, "games": 0})
            if outcome == "error":
                entry["errors"] += 1
                continue
            entry["games"] += 1
            pair["games"] += 1
            if outcome == "win":
                entry["wins"] += 1
                pair["wins"] += 1
    for entry in table.values():
        low, high = wilson_interval(entry["wins"], entry["games"])
        entry["win_rate"] = round(entry["wins"] / entry["games"], 4) if entry["games"] else 0.0
        entry["ci95_low"], entry["ci95_high"] = round(low, 4), round(high, 4)
        for pair in entry["pairs"].values():
            pair["win_rate"] = round(pair["wins"] / pair["games"], 4) if pair["games"] else 0.0
    return table


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agents", help="comma list; default: random,first,. and all candidates")
    parser.add_argument("--games-per-seat", type=int, default=5)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--experiment-id", default="gauntlet")
    args = parser.parse_args()

    labels = (
        [value.strip() for value in args.agents.split(",") if value.strip()]
        if args.agents
        else default_agents()
    )
    if len(labels) < 2:
        parser.error("need at least two agents")
    if args.games_per_seat < 1 or args.workers < 1:
        parser.error("--games-per-seat and --workers must be positive")
    try:
        resolved = {label: resolve_agent(label) for label in labels}
    except ValueError as exc:
        parser.exit(2, f"ERROR: {exc}\n")

    specs = [
        (resolved[first], resolved[second], seat, (first, second))
        for first, second in combinations(labels, 2)
        for seat in (0, 1)
        for _ in range(args.games_per_seat)
    ]
    with ProcessPoolExecutor(max_workers=min(args.workers, len(specs))) as pool:
        raw = list(
            pool.map(
                run_game,
                [spec[0] for spec in specs],
                [spec[1] for spec in specs],
                [spec[2] for spec in specs],
            )
        )
    records = []
    for spec, record in zip(specs, raw, strict=True):
        # run_game reports from the first agent's perspective regardless of seat.
        record["pair"] = spec[3]
        records.append(record)

    table = rank(records, labels)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    RUNS.mkdir(parents=True, exist_ok=True)
    output = RUNS / f"{stamp}__{args.experiment_id}.json"
    output.write_text(
        json.dumps(
            {
                "created_at_utc": datetime.now(UTC).isoformat(),
                "games_per_seat": args.games_per_seat,
                "table": table,
                "records": records,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )

    ordered = sorted(table.items(), key=lambda item: item[1]["win_rate"], reverse=True)
    width = max(len(label) for label in labels)
    print(f"{'agent':<{width}}  win%   [95% CI]        W-L (errors)")
    for label, entry in ordered:
        print(
            f"{label:<{width}}  {entry['win_rate']:.3f}  "
            f"[{entry['ci95_low']:.3f},{entry['ci95_high']:.3f}]  "
            f"{entry['wins']}-{entry['games'] - entry['wins']} ({entry['errors']})"
        )
    print(f"run: {output.relative_to(ROOT)}")
    errors = sum(entry["errors"] for entry in table.values())
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
