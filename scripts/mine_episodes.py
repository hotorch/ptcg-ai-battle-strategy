"""Daily top-episodes 데이터 마이닝.

deck-stats: 각 episode의 양측 덱 시그니처와 승패를 집계한다.
extract: 특정 카드 조합을 포함한 덱이 등장하는 episode 목록/파일을 추출한다.

replay 원문은 Competition Data이므로 데이터 산출물(집계 TSV, 추출 JSON)은
data/raw/ 아래에만 두고 커밋하지 않는다.
"""

from __future__ import annotations

import argparse
import collections
import json
import zipfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

_ZIP_PATH: Path | None = None
_ZIP: zipfile.ZipFile | None = None


def _init_worker(zip_path: str) -> None:
    global _ZIP_PATH, _ZIP
    _ZIP_PATH = Path(zip_path)
    _ZIP = zipfile.ZipFile(zip_path)


def _episode_summary(name: str) -> dict | None:
    assert _ZIP is not None
    episode = json.loads(_ZIP.read(name))
    steps = episode.get("steps") or []
    if not steps or len(steps[0]) != 2:
        return None
    decks = None
    for agent_state in steps[0]:
        for visual in agent_state.get("visualize") or []:
            action = visual.get("action")
            if (
                isinstance(action, list)
                and len(action) == 2
                and all(isinstance(side, list) and len(side) == 60 for side in action)
            ):
                decks = action
                break
        if decks:
            break
    if decks is None:
        return None
    rewards = episode.get("rewards") or [None, None]
    return {
        "episode_id": episode.get("id"),
        "file": name,
        "teams": (episode.get("info") or {}).get("TeamNames") or ["?", "?"],
        "decks": [sorted(side) for side in decks],
        "rewards": rewards,
        "statuses": episode.get("statuses"),
    }


def deck_signature(deck: list[int]) -> tuple[tuple[int, int], ...]:
    return tuple(sorted(collections.Counter(deck).items()))


def scan(zip_path: Path, workers: int) -> list[dict]:
    with zipfile.ZipFile(zip_path) as z:
        names = [n for n in z.namelist() if n.endswith(".json")]
    with ProcessPoolExecutor(
        max_workers=workers, initializer=_init_worker, initargs=(str(zip_path),)
    ) as pool:
        rows = list(pool.map(_episode_summary, names, chunksize=32))
    return [row for row in rows if row]


def cmd_deck_stats(args: argparse.Namespace) -> None:
    rows = scan(Path(args.zip), args.workers)
    stats: dict = collections.defaultdict(lambda: {"games": 0, "wins": 0, "teams": collections.Counter()})
    skipped = 0
    for row in rows:
        rewards = row["rewards"]
        if rewards is None or None in rewards:
            skipped += 1
            continue
        for seat in (0, 1):
            sig = deck_signature(row["decks"][seat])
            entry = stats[sig]
            entry["games"] += 1
            entry["wins"] += 1 if rewards[seat] > rewards[1 - seat] else 0
            entry["teams"][row["teams"][seat]] += 1
    print(f"episodes={len(rows)} skipped_no_result={skipped} unique_decks={len(stats)}")
    ranked = sorted(stats.items(), key=lambda kv: -kv[1]["games"])
    for sig, entry in ranked[: args.top]:
        rate = entry["wins"] / entry["games"]
        top_teams = ", ".join(f"{t}:{c}" for t, c in entry["teams"].most_common(3))
        key_cards = [f"{cid}x{n}" for cid, n in sig if cid > 100][:8]
        print(f"games={entry['games']:5d} win={rate:.3f} teams=[{top_teams}] cards={key_cards}")
    if args.out:
        payload = [
            {
                "signature": list(map(list, sig)),
                "games": entry["games"],
                "wins": entry["wins"],
                "teams": dict(entry["teams"]),
            }
            for sig, entry in ranked
        ]
        Path(args.out).write_text(json.dumps(payload, indent=1))
        print(f"saved {args.out}")


def cmd_extract(args: argparse.Namespace) -> None:
    required = collections.Counter(json.loads(Path(args.deck).read_text()))
    rows = scan(Path(args.zip), args.workers)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    matched = 0
    with zipfile.ZipFile(args.zip) as z:
        for row in rows:
            seats = [
                seat
                for seat in (0, 1)
                if collections.Counter(row["decks"][seat]) == required
            ]
            if not seats:
                continue
            matched += 1
            meta = {
                "file": row["file"],
                "seats": seats,
                "teams": row["teams"],
                "rewards": row["rewards"],
            }
            (out_dir / row["file"]).write_bytes(z.read(row["file"]))
            (out_dir / (row["file"] + ".meta")).write_text(json.dumps(meta))
    print(f"matched_episodes={matched} -> {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=8)
    commands = parser.add_subparsers(dest="command", required=True)

    stats = commands.add_parser("deck-stats")
    stats.add_argument("--zip", required=True)
    stats.add_argument("--top", type=int, default=15)
    stats.add_argument("--out")
    stats.set_defaults(func=cmd_deck_stats)

    extract = commands.add_parser("extract")
    extract.add_argument("--zip", required=True)
    extract.add_argument("--deck", required=True, help="JSON list of 60 card ids")
    extract.add_argument("--out-dir", required=True)
    extract.set_defaults(func=cmd_extract)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
