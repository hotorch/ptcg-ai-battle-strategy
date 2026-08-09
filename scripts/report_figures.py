"""Strategy Writeup용 그림을 원장 데이터에서 재생성한다.

모든 그림은 자체 제작 차트만 사용한다(카드 이미지 금지 규정).

사용:
  uv run python scripts/report_figures.py fetch-ladder --submission-ids 55256596,55263771
  uv run python scripts/report_figures.py ladder
  uv run python scripts/report_figures.py opponents --runs <run.json> [<run.json> ...]
  uv run python scripts/report_figures.py seats --runs <run.json> [<run.json> ...]

fetch-ladder는 Kaggle 공개 엔드포인트에서 제출별 episode를 받아
research_loop/ladder/<submission_id>.json 에 캐시한다. 나머지 서브커맨드는
오프라인 캐시·원장만 읽으므로 언제든 같은 그림을 다시 만들 수 있다.
"""

from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
LADDER_DIR = ROOT / "research_loop" / "ladder"
FIG_DIR = ROOT / "docs" / "ptcg" / "figures"

# dataviz 기본 팔레트(검증 완료된 고정 순서 categorical slot 1..3)
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]
SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
TEXT_2 = "#52514e"
GRID = "#e5e4e0"

plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "text.color": TEXT,
        "axes.labelcolor": TEXT_2,
        "xtick.color": TEXT_2,
        "ytick.color": TEXT_2,
        "axes.edgecolor": GRID,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "font.size": 10,
    }
)


def fetch_ladder(submission_ids: list[int]) -> None:
    LADDER_DIR.mkdir(parents=True, exist_ok=True)
    for sid in submission_ids:
        req = urllib.request.Request(
            "https://www.kaggle.com/api/i/competitions.EpisodeService/ListEpisodes",
            data=json.dumps({"submissionId": sid}).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            payload = json.load(r)
        out = LADDER_DIR / f"{sid}.json"
        out.write_text(json.dumps(payload))
        print(f"saved {out} episodes={len(payload.get('episodes', []))}")


def _ladder_rows(sid: int) -> list[dict]:
    payload = json.loads((LADDER_DIR / f"{sid}.json").read_text())
    rows = []
    for ep in payload.get("episodes", []):
        me = next((a for a in ep.get("agents", []) if a.get("submissionId") == sid), None)
        if me is None or me.get("updatedScore") is None:
            continue
        rows.append({"end": ep.get("endTime"), "rating": me["updatedScore"]})
    rows.sort(key=lambda r: r["end"] or "")
    return rows


def cmd_ladder(args: argparse.Namespace) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 3.6))
    labels = dict(pair.split("=", 1) for pair in args.labels.split(",")) if args.labels else {}
    paths = [p for p in sorted(LADDER_DIR.glob("*.json")) if p.stem.isdigit()]
    for i, path in enumerate(paths):
        sid = path.stem
        rows = _ladder_rows(int(sid))
        if not rows:
            continue
        label = labels.get(sid, sid)
        ax.plot(
            range(1, len(rows) + 1),
            [r["rating"] for r in rows],
            color=SERIES[i % len(SERIES)],
            linewidth=2,
            label=label,
        )
        ax.annotate(
            f"{rows[-1]['rating']:.0f}",
            (len(rows), rows[-1]["rating"]),
            textcoords="offset points",
            xytext=(6, 0),
            color=TEXT_2,
            fontsize=9,
        )
    ax.set_xlabel("ladder game #")
    ax.set_ylabel("rating")
    ax.legend(frameon=False)
    fig.tight_layout()
    out = FIG_DIR / "fig_ladder_trajectory.png"
    fig.savefig(out, dpi=200)
    print(f"saved {out}")


def _load_runs(paths: list[str]) -> list[dict]:
    return [json.loads(Path(p).read_text()) for p in paths]


def _run_label(run: dict) -> str:
    experiment = run.get("experiment_id") or ""
    name = Path(run["candidate"]).name
    return f"{name} ({experiment})" if experiment else name


def cmd_opponents(args: argparse.Namespace) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    runs = _load_runs(args.runs)
    opponents = sorted({opp for run in runs for opp in run["summary"]["by_opponent"]})
    fig, ax = plt.subplots(figsize=(7, 0.55 * len(opponents) * max(len(runs), 1) + 1.6))
    height = 0.8 / max(len(runs), 1)
    for i, run in enumerate(runs):
        stats = run["summary"]["by_opponent"]
        ys, xs, err_lo, err_hi = [], [], [], []
        for j, opp in enumerate(opponents):
            v = stats.get(opp)
            if not v:
                continue
            ys.append(j + i * height)
            xs.append(v["win_rate"])
            err_lo.append(v["win_rate"] - v["ci95_low"])
            err_hi.append(v["ci95_high"] - v["win_rate"])
        ax.barh(ys, xs, height=height * 0.9, color=SERIES[i % len(SERIES)], label=_run_label(run))
        ax.errorbar(xs, ys, xerr=[err_lo, err_hi], fmt="none", ecolor=TEXT_2, elinewidth=1, capsize=2)
    ax.set_yticks([j + 0.4 for j in range(len(opponents))])
    ax.set_yticklabels([Path(o).name for o in opponents])
    ax.axvline(0.5, color=TEXT_2, linewidth=0.8, linestyle="--")
    ax.set_xlim(0, 1)
    ax.set_xlabel("win rate (CI95)")
    ax.invert_yaxis()
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    out = FIG_DIR / "fig_by_opponent.png"
    fig.savefig(out, dpi=200)
    print(f"saved {out}")


def cmd_seats(args: argparse.Namespace) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    runs = _load_runs(args.runs)
    fig, ax = plt.subplots(figsize=(6, 3))
    width = 0.35
    for seat in (0, 1):
        xs, ys = [], []
        for i, run in enumerate(runs):
            v = run["summary"]["by_seat"][str(seat)]
            games = v["win"] + v["loss"] + v["draw"]
            xs.append(i + (seat - 0.5) * width)
            ys.append(v["win"] / max(games, 1))
        ax.bar(xs, ys, width=width * 0.9, color=SERIES[seat], label=f"seat {seat}")
    ax.axhline(0.5, color=TEXT_2, linewidth=0.8, linestyle="--")
    ax.set_xticks(range(len(runs)))
    ax.set_xticklabels([_run_label(r) for r in runs], fontsize=8)
    ax.set_ylabel("win rate by seat")
    ax.set_ylim(0, 1)
    ax.legend(frameon=False)
    fig.tight_layout()
    out = FIG_DIR / "fig_seat_split.png"
    fig.savefig(out, dpi=200)
    print(f"saved {out}")


def _archetype_label(signature: list[list[int]]) -> str:
    """시그니처의 대표 포켓몬(진화 단계·HP 최고) 이름으로 아키타입 라벨을 만든다."""
    import sys

    sdk = ROOT / "data" / "raw" / "sample_submission"
    if str(sdk) not in sys.path:
        sys.path.insert(0, str(sdk))
    from cg.api import CardType, all_card_data

    cards = {c.cardId: c for c in all_card_data()}
    best, best_key = None, (-1, -1)
    for cid, _n in signature:
        data = cards.get(cid)
        if data is None or data.cardType != CardType.POKEMON:
            continue
        key = (2 if data.megaEx else (1 if data.stage2 or data.stage1 else 0), data.hp or 0)
        if key > best_key:
            best, best_key = data, key
    return best.name if best is not None else "unknown"


def cmd_deck_field(args: argparse.Namespace) -> None:
    """일일 deck_stats N일 합산 → 상위 덱 승률 분포. 우리 덱만 강조색."""
    import collections

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    merged: dict = collections.defaultdict(lambda: {"games": 0, "wins": 0})
    for path in sorted((ROOT / "data" / "raw" / "episodes").glob("deck_stats_*.json")):
        for entry in json.loads(path.read_text()):
            sig = tuple(tuple(x) for x in entry["signature"])
            merged[sig]["games"] += entry["games"]
            merged[sig]["wins"] += entry["wins"]
    our_deck = json.loads(Path(args.our_deck).read_text())
    our_sig = tuple(sorted(collections.Counter(our_deck).items()))
    top = sorted(merged.items(), key=lambda kv: -kv[1]["games"])[: args.top]
    if our_sig not in [sig for sig, _ in top]:
        top.append((our_sig, merged[our_sig]))
    rows = []
    for sig, entry in top:
        rate = entry["wins"] / max(entry["games"], 1)
        rows.append((_archetype_label([list(p) for p in sig]), rate, entry["games"], sig == our_sig))
    rows.sort(key=lambda r: r[1])
    fig, ax = plt.subplots(figsize=(7, 0.42 * len(rows) + 1.4))
    ys = range(len(rows))
    colors = [SERIES[0] if ours else "#c9c8c4" for _, _, _, ours in rows]
    ax.barh(ys, [r[1] for r in rows], color=colors, height=0.62)
    for y, (label, rate, games, ours) in zip(ys, rows):
        ax.annotate(
            f"{rate:.1%} (n={games:,})",
            (rate, y),
            textcoords="offset points",
            xytext=(4, -3),
            color=TEXT if ours else TEXT_2,
            fontsize=8,
            fontweight="bold" if ours else "normal",
        )
    ax.axvline(0.5, color=TEXT_2, linewidth=0.8, linestyle="--")
    ax.set_yticks(list(ys))
    ax.set_yticklabels(
        [("★ " if ours else "") + label for label, _, _, ours in rows], fontsize=8
    )
    ax.set_xlabel("field win rate (daily top-episode datasets, merged)")
    ax.set_xlim(0, 1)
    fig.tight_layout()
    out = FIG_DIR / "fig_deck_field.png"
    fig.savefig(out, dpi=200)
    print(f"saved {out}")


def main() -> None:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)

    fetch = commands.add_parser("fetch-ladder")
    fetch.add_argument("--submission-ids", required=True)
    fetch.set_defaults(func=lambda a: fetch_ladder([int(s) for s in a.submission_ids.split(",")]))

    ladder = commands.add_parser("ladder")
    ladder.add_argument("--labels", help="submission_id=라벨 쌍을 쉼표로 나열")
    ladder.set_defaults(func=cmd_ladder)

    opponents = commands.add_parser("opponents")
    opponents.add_argument("--runs", nargs="+", required=True)
    opponents.set_defaults(func=cmd_opponents)

    seats = commands.add_parser("seats")
    seats.add_argument("--runs", nargs="+", required=True)
    seats.set_defaults(func=cmd_seats)

    field = commands.add_parser("deck-field")
    field.add_argument("--our-deck", default="data/raw/episodes/majkel_lucario_deck.json")
    field.add_argument("--top", type=int, default=10)
    field.set_defaults(func=cmd_deck_field)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
