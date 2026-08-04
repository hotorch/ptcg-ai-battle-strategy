"""Run non-deterministic CABT match bundles from both seats."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import sys
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "research_loop" / "runs"
RESULTS = ROOT / "research_loop" / "results.tsv"
BUNDLES = {"smoke": 1, "quick": 10, "full": 50}
BUILTINS = {"random", "first"}


def resolve_agent(value: str) -> str:
    if value in BUILTINS:
        return value
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    if path.is_dir():
        path = path / "main.py"
    if not path.is_file():
        raise ValueError(f"agent not found: {value}")
    if not (path.parent / "deck.csv").is_file():
        raise ValueError(f"deck.csv not found beside: {path}")
    return str(path.resolve())


@contextmanager
def agent_context(path: Path):
    previous = Path.cwd()
    old_path = list(sys.path)
    os.chdir(path)
    sys.path.insert(0, str(path))
    local_sdk = ROOT / "data" / "raw" / "sample_submission"
    if (local_sdk / "cg").is_dir():
        sys.path.insert(0, str(local_sdk))
    try:
        yield
    finally:
        os.chdir(previous)
        sys.path[:] = old_path


def load_agent(value: str, suffix: str):
    if value in BUILTINS:
        return value
    path = Path(value)
    spec = importlib.util.spec_from_file_location(f"ptcg_agent_{suffix}", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load agent: {path}")
    module = importlib.util.module_from_spec(spec)
    with agent_context(path.parent):
        spec.loader.exec_module(module)
    base = module.agent

    def wrapped(obs):
        with agent_context(path.parent):
            return base(obs)

    return wrapped


def wilson_interval(wins: int, games: int, z: float = 1.96) -> tuple[float, float]:
    if games == 0:
        return 0.0, 0.0
    rate = wins / games
    denominator = 1 + z * z / games
    center = (rate + z * z / (2 * games)) / denominator
    margin = z * math.sqrt(rate * (1 - rate) / games + z * z / (4 * games * games)) / denominator
    return max(0.0, center - margin), min(1.0, center + margin)


def run_game(candidate: str, opponent: str, seat: int) -> dict:
    record = {"opponent": opponent, "candidate_seat": seat}
    try:
        candidate_agent = load_agent(candidate, f"candidate_{id(record)}")
        opponent_agent = load_agent(opponent, f"opponent_{id(record)}")
        agents = (
            [candidate_agent, opponent_agent] if seat == 0 else [opponent_agent, candidate_agent]
        )
        env = make("cabt", debug=False)
        env.run(agents)
        final = env.steps[-1]
        rewards = [state.reward for state in final]
        statuses = [state.status for state in final]
        mine, theirs = rewards[seat], rewards[1 - seat]
        error = statuses != ["DONE", "DONE"] or mine is None or theirs is None
        record.update(rewards=rewards, statuses=statuses, turns=len(env.steps) - 1, error=error)
        record["outcome"] = (
            "error" if error else "win" if mine > theirs else "loss" if mine < theirs else "draw"
        )
    except Exception as exc:  # noqa: BLE001 - a crashed match is evaluation data
        record.update(error=True, outcome="error", exception=f"{type(exc).__name__}: {exc}")
    return record


def summarize(records: list[dict]) -> dict:
    valid = [record for record in records if not record["error"]]
    wins = sum(record["outcome"] == "win" for record in valid)
    losses = sum(record["outcome"] == "loss" for record in valid)
    draws = sum(record["outcome"] == "draw" for record in valid)
    low, high = wilson_interval(wins, len(valid))
    return {
        "games": len(records),
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "errors": len(records) - len(valid),
        "win_rate": round(wins / len(valid), 4) if valid else 0.0,
        "ci95_low": round(low, 4),
        "ci95_high": round(high, 4),
        "mean_turns": round(sum(record["turns"] for record in valid) / len(valid), 2)
        if valid
        else None,
        "by_seat": {
            str(seat): {
                outcome: sum(
                    r["candidate_seat"] == seat and r["outcome"] == outcome for r in records
                )
                for outcome in ("win", "loss", "draw", "error")
            }
            for seat in (0, 1)
        },
    }


def append_result(args: argparse.Namespace, total: dict) -> None:
    description = " ".join(args.description.split()).replace("\t", " ")
    row = [
        args.experiment_id,
        args.hypothesis_id,
        args.candidate,
        args.opponents,
        total["games"],
        total["wins"],
        total["losses"],
        total["draws"],
        total["errors"],
        total["win_rate"],
        total["ci95_low"],
        total["ci95_high"],
        args.status,
        description,
    ]
    with RESULTS.open("a", encoding="utf-8") as output:
        output.write("\t".join(map(str, row)) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", default=".")
    parser.add_argument("--opponents", default="random,first")
    parser.add_argument("--bundle", choices=BUNDLES, default="quick")
    parser.add_argument("--games-per-seat", type=int)
    parser.add_argument("--experiment-id", default="untracked")
    parser.add_argument("--hypothesis-id", default="H-000")
    parser.add_argument("--status", default="measured")
    parser.add_argument("--description", default="")
    parser.add_argument("--append-results", action="store_true")
    args = parser.parse_args()

    games_per_seat = args.games_per_seat or BUNDLES[args.bundle]
    if games_per_seat < 1:
        parser.error("--games-per-seat must be positive")
    try:
        candidate = resolve_agent(args.candidate)
        opponents = [
            resolve_agent(value.strip()) for value in args.opponents.split(",") if value.strip()
        ]
    except ValueError as exc:
        parser.exit(2, f"ERROR: {exc}\n")

    records = [
        run_game(candidate, opponent, seat)
        for opponent in opponents
        for seat in (0, 1)
        for _ in range(games_per_seat)
    ]
    total = summarize(records)
    payload = {
        "created_at_utc": datetime.now(UTC).isoformat(),
        "candidate": args.candidate,
        "opponents": args.opponents,
        "bundle": args.bundle,
        "games_per_seat": games_per_seat,
        "summary": total,
        "records": records,
        "note": "CABT RNG is not seed-controlled; results are unpaired repeated games.",
    }
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    RUNS.mkdir(parents=True, exist_ok=True)
    output = RUNS / f"{stamp}__{args.experiment_id}.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(total, ensure_ascii=False, indent=2))
    print(f"run: {output.relative_to(ROOT)}")
    if args.append_results:
        append_result(args, total)
        print(f"ledger: {RESULTS.relative_to(ROOT)}")
    return 1 if total["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
