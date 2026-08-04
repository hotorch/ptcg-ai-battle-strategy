"""Rank and fetch high-signal items from the latest Kaggle context snapshot."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.kaggle_ops import (
    COMPETITION,
    CONTEXT,
    ROOT,
    parse_json_output,
    run_kaggle,
    safe_ref,
    write_json,
)

KEYWORDS = {
    "agent",
    "baseline",
    "bug",
    "deck",
    "engine",
    "evaluation",
    "mcts",
    "replay",
    "rl",
    "search",
    "submit",
    "submission",
    "training",
}


def latest_snapshot() -> Path:
    snapshots = CONTEXT / "snapshots"
    values = (
        sorted(path for path in snapshots.iterdir() if path.is_dir()) if snapshots.is_dir() else []
    )
    if not values:
        raise ValueError("run `uv run python scripts/kaggle_ops.py sync-context` first")
    return values[-1]


def load(path: Path) -> list[dict]:
    value = json.loads(path.read_text())
    return value if isinstance(value, list) else []


def keyword_hits(title: str) -> int:
    lowered = title.lower()
    return sum(word in lowered for word in KEYWORDS)


def topic_score(item: dict) -> int:
    return (
        3 * item.get("votes", 0)
        + 2 * item.get("commentCount", 0)
        + 15 * keyword_hits(item.get("title", ""))
    )


def notebook_score(item: dict) -> int:
    return 3 * item.get("totalVotes", 0) + 15 * keyword_hits(item.get("title", ""))


def fetch_topic(item: dict, destination: Path) -> Path:
    ref = f"{COMPETITION}/{item['id']}"
    value = parse_json_output(
        run_kaggle(["competitions", "topics", "show", ref, "--format", "json"])
    )
    output = destination / "topics" / f"{item['id']}.json"
    write_json(output, value)
    return output


def fetch_notebook(item: dict, destination: Path) -> Path:
    output = destination / "notebooks" / safe_ref(item["ref"])
    output.mkdir(parents=True, exist_ok=True)
    run_kaggle(["kernels", "pull", item["ref"], "--path", str(output), "--metadata"])
    write_json(
        output / "source.json",
        {"ref": item["ref"], "url": f"https://www.kaggle.com/code/{item['ref']}"},
    )
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topics", type=int, default=8)
    parser.add_argument("--notebooks", type=int, default=6)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.topics < 0 or args.notebooks < 0:
        parser.error("limits cannot be negative")

    snapshot = latest_snapshot()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    destination = CONTEXT / "curated" / stamp
    destination.mkdir(parents=True)
    topics = sorted(load(snapshot / "recent-topics.json"), key=topic_score, reverse=True)[
        : args.topics
    ]
    notebooks = sorted(load(snapshot / "top-notebooks.json"), key=notebook_score, reverse=True)[
        : args.notebooks
    ]

    lines = [
        f"# Curated Kaggle context — {stamp}",
        "",
        f"snapshot: `{snapshot.name}`",
        "",
        "## Discussion",
    ]
    for item in topics:
        location = ""
        if not args.dry_run:
            location = f" → `{fetch_topic(item, destination).relative_to(ROOT)}`"
        lines.append(
            f"- [{item.get('title', '(no title)')}](https://www.kaggle.com/competitions/{COMPETITION}/discussion/{item['id']}) "
            f"— score {topic_score(item)}, {item.get('votes', 0)}v/{item.get('commentCount', 0)}c{location}"
        )
    lines += ["", "## Notebook"]
    for item in notebooks:
        location = ""
        if not args.dry_run:
            location = f" → `{fetch_notebook(item, destination).relative_to(ROOT)}`"
        lines.append(
            f"- [{item.get('title', '(no title)')}](https://www.kaggle.com/code/{item['ref']}) "
            f"— score {notebook_score(item)}, {item.get('totalVotes', 0)}v{location}"
        )
    report = "\n".join(lines) + "\n"
    (destination / "report.md").write_text(report)
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
