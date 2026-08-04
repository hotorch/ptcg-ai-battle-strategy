"""Create a non-overwriting daily journal from the experiment and submission ledgers."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
JOURNAL = ROOT / "docs" / "ptcg" / "journal"
SEOUL = ZoneInfo("Asia/Seoul")


def rows_for_day(path: Path, compact_day: str) -> list[str]:
    if not path.is_file():
        return []
    lines = path.read_text().strip().splitlines()
    return [line for line in lines[1:] if line.startswith(compact_day)]


def build(day: str) -> str:
    compact = day.replace("-", "")
    experiments = rows_for_day(ROOT / "research_loop" / "results.tsv", compact)
    submissions = rows_for_day(ROOT / "submissions" / "history.tsv", compact)
    return "\n".join(
        [
            f"# 일일 기록 — {day}",
            "",
            "## 실험",
            *(f"- `{row}`" for row in experiments),
            *(["(없음)"] if not experiments else []),
            "",
            "## 제출",
            *(f"- `{row}`" for row in submissions),
            *(["(없음)"] if not submissions else []),
            "",
            "## 한 일과 이유",
            "",
            "(작성)",
            "",
            "## 배운 것",
            "",
            "(작성)",
            "",
            "## 내일 우선순위",
            "",
            "1. (다음 세션이 바로 실행할 일)",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default=datetime.now(SEOUL).strftime("%Y-%m-%d"))
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    content = build(args.date)
    print(content)
    if args.write:
        destination = JOURNAL / f"{args.date}.md"
        if destination.exists():
            print(f"already exists: {destination.relative_to(ROOT)}")
        else:
            destination.write_text(content)
            print(f"created: {destination.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
