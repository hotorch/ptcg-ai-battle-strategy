#!/usr/bin/env python3
"""일일 LB 순위 스냅샷을 기록한다 (마감 후 수렴 관전 + anti-cheat 퍼지 추적).

공개 리더보드 CSV를 받아 우리 팀(팀ID 16662405, aisamhottman)의 순위·점수와
메달 컷 경계 점수(Kaggle 규칙: 1000팀+ 기준 gold=10+0.2%n, silver=5%n,
bronze=10%n)를 `submissions/rank_history.tsv`에 append한다.

    uv run python scripts/watch_rank.py

계기: 8/22 공식 공지 — anti-cheat 퍼지로 팀이 LB에서 제거되며 순위가 수동
상승할 수 있다(topic 735312). Writeup 서두의 최종 순위 수치가 여기서 나온다.
"""

import csv
import io
import subprocess
import sys
import tempfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path

TEAM_ID = "16662405"
COMPETITION = "pokemon-tcg-ai-battle"
ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "submissions" / "rank_history.tsv"


def fetch_rows() -> list[dict]:
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(
            ["uv", "run", "kaggle", "competitions", "leaderboard", COMPETITION,
             "--download", "-p", tmp],
            check=True, capture_output=True, cwd=ROOT,
        )
        zips = list(Path(tmp).glob("*.zip"))
        if not zips:
            raise RuntimeError("leaderboard zip not downloaded")
        with zipfile.ZipFile(zips[0]) as z:
            name = next(n for n in z.namelist() if n.endswith(".csv"))
            text = z.read(name).decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))


def main() -> int:
    rows = fetch_rows()
    total = len(rows)
    me = next((r for r in rows if r["TeamId"] == TEAM_ID), None)
    if me is None:
        print(f"ERROR: team {TEAM_ID} not on leaderboard ({total} teams)")
        return 1
    gold_n = 10 + int(0.002 * total)
    silver_n = int(0.05 * total)
    bronze_n = int(0.10 * total)
    cuts = {}
    for label, boundary in (("gold", gold_n), ("silver", silver_n), ("bronze", bronze_n)):
        cuts[label] = float(rows[boundary - 1]["Score"]) if boundary <= total else float("nan")
    stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    if not LOG.exists():
        LOG.write_text(
            "checked_at_utc\trank\tteams\tscore\tgold_cut\tsilver_cut\tbronze_cut\n"
        )
    with LOG.open("a", encoding="utf-8") as f:
        f.write(
            f"{stamp}\t{me['Rank']}\t{total}\t{me['Score']}\t"
            f"{cuts['gold']:.1f}\t{cuts['silver']:.1f}\t{cuts['bronze']:.1f}\n"
        )
    print(
        f"[{stamp}] rank={me['Rank']}/{total} score={me['Score']} "
        f"cuts: gold {cuts['gold']:.1f} (top {gold_n}) / silver {cuts['silver']:.1f} "
        f"(top {silver_n}) / bronze {cuts['bronze']:.1f} (top {bronze_n})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
