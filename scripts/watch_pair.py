#!/usr/bin/env python3
"""잠금 페어(h036 i8/i9)의 수렴 스냅샷을 기록한다 (마감 후 ~2주 관전용).

에피소드 API에서 레이팅·경기수·승률·최근 궤적을 읽어 한 줄 출력하고
`submissions/pair_convergence.tsv`에 append한다. 아침 세션마다 1회 실행:

    uv run python scripts/watch_pair.py

Writeup §4(빌드=분포)의 최종 수렴 증거 데이터가 여기 쌓인다.
전체 에피소드 원본이 필요하면: scripts/report_figures.py fetch-ladder --submission-ids 55525772,55525773
"""

import json
import math
import sys
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

PAIR = {"i8": 55525772, "i9": 55525773}
ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "submissions" / "pair_convergence.tsv"


def fetch(sid: int) -> dict:
    req = urllib.request.Request(
        "https://www.kaggle.com/api/i/competitions.EpisodeService/ListEpisodes",
        data=json.dumps({"submissionId": sid}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def parse_ts(ts):
    if ts is None:
        return None
    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(ts, tz=UTC)
    try:
        return datetime.fromisoformat(str(ts))
    except ValueError:
        return None


def main() -> int:
    now = datetime.now(UTC)
    stamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    if not LOG.exists():
        LOG.write_text("checked_at_utc\tinstance\tsubmission_id\trating\tgames\twins\twin_rate\tidle_hours\tlast5\n")
    lines = []
    warnings = []
    for name, sid in PAIR.items():
        payload = fetch(sid)
        rows = []
        for ep in payload.get("episodes", []):
            me = next((a for a in ep.get("agents", []) if a.get("submissionId") == sid), None)
            if me is None or me.get("updatedScore") is None:
                continue
            rows.append(
                {
                    "end": parse_ts(ep.get("endTime")),
                    "rating": me["updatedScore"],
                    "reward": me.get("reward"),
                }
            )
        rows.sort(key=lambda r: (r["end"] is None, r["end"]))
        n = len(rows)
        wins = sum(1 for r in rows if (r["reward"] or 0) > 0)
        rating = rows[-1]["rating"] if rows else float("nan")
        last_end = rows[-1]["end"] if rows else None
        idle_h = (now - last_end).total_seconds() / 3600 if last_end else float("nan")
        wr = wins / n if n else 0.0
        tail = ",".join(str(round(r["rating"])) for r in rows[-5:])
        lines.append(
            f"{name} sid={sid} rating={rating:.1f} games={n} wr={100 * wr:.1f}% idle={idle_h:.1f}h last5=[{tail}]"
        )
        with LOG.open("a", encoding="utf-8") as f:
            f.write(
                f"{stamp}\t{name}\t{sid}\t{rating:.1f}\t{n}\t{wins}\t{wr:.4f}\t{idle_h:.2f}\t{tail}\n"
            )
        if n == 0 or (not math.isnan(idle_h) and idle_h > 24):
            warnings.append(f"{name}: 24h+ 무경기 — 스케줄러 이상 가능성, 다음 세션에서 재확인")
    print(f"[{stamp}]")
    for line in lines:
        print(line)
    if warnings:
        print("WARN: " + "; ".join(warnings))
    else:
        print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
