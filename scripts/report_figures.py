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
import re
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


# limitless TEF-POR all-time 셰어 (8/14 수집, top-agent-observation.md 결과 4).
# Grimmsnarl·Slowking은 상위 15위 밖 → 0 처리 (TV도 같은 규약).
_META_BALANCE = {
    "Dragapult": 42.7,
    "Grimmsnarl": 0.0,
    "Alakazam": 4.9,
    "Meganium/TapuBulu": 2.3,
    "Slowking": 0.0,
    "MegaLucario": 3.0,
}
_META_LINES = [
    ("Dragapult", SERIES[0]),
    ("Grimmsnarl", SERIES[1]),
    ("Alakazam", SERIES[2]),
    ("Meganium/TapuBulu", SERIES[3]),
    ("Slowking", SERIES[4]),
    ("MegaLucario", "#9a9996"),
]


def cmd_meta(args: argparse.Namespace) -> None:
    """그림 C: 상위 풀 아키타입 셰어 시계열 + limitless 균형점(예측→실현).

    입력: mine_episodes deck-stats --out 덤프(scratch/decks_YYYY-MM-DD.json).
    분모 = 덱-게임 수(2×에피소드), 집계 규약은 archetype_shares.py와 동일.
    """
    import datetime as dt

    from archetype_shares import classify

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    dates, shares = [], {name: [] for name, _c in _META_LINES}
    tvs = []
    for path in sorted(Path().glob(args.dumps)):
        rows = json.loads(Path(path).read_text())
        total = sum(r["games"] for r in rows)
        agg: dict = {}
        for r in rows:
            name = classify({cid for cid, _n in r["signature"]})
            agg[name] = agg.get(name, 0) + r["games"]
        date = dt.date.fromisoformat(Path(path).stem.replace("decks_", ""))
        dates.append(date)
        for name, series in shares.items():
            series.append(100.0 * agg.get(name, 0) / total)
        tvs.append(
            0.5 * sum(abs(100.0 * agg.get(n, 0) / total - q) for n, q in _META_BALANCE.items()) / 100.0
        )

    fig, (ax, ax_tv) = plt.subplots(
        2, 1, figsize=(7, 5.2), sharex=True, height_ratios=[3, 1]
    )
    # 균형점 라벨 y 위치: 겹침 방지를 위해 아래에서부터 최소 간격을 강제한다.
    label_y, floor = {}, -3.5
    for name, eq in sorted(_META_BALANCE.items(), key=lambda kv: kv[1]):
        label_y[name] = max(eq, floor + 3.2)
        floor = label_y[name]
    for name, color in _META_LINES:
        ys = shares[name]
        eq = _META_BALANCE[name]
        ax.plot(dates, ys, color=color, linewidth=2, marker="o", markersize=3, label=name)
        # 예측→실현: 마지막 관측치에서 limitless 균형점으로 향하는 화살표.
        if abs(eq - ys[-1]) >= 3.0:
            ax.annotate(
                "",
                xy=(dates[-1] + dt.timedelta(days=1.4), eq),
                xytext=(dates[-1] + dt.timedelta(days=0.3), ys[-1]),
                arrowprops={"arrowstyle": "->", "color": color, "linewidth": 1.1, "linestyle": ":"},
            )
        ax.plot(
            [dates[-1] + dt.timedelta(days=1.4), dates[-1] + dt.timedelta(days=2.2)],
            [eq, eq], color=color, linewidth=1.4, linestyle=":",
        )
        ax.annotate(
            f"eq {eq:.1f}%" if eq else "eq ~0%",
            (dates[-1] + dt.timedelta(days=2.4), label_y[name]),
            color=color,
            fontsize=7.5,
            va="center",
        )
        if name in ("Dragapult", "Grimmsnarl"):
            ax.annotate(
                f"{ys[-1]:.1f}",
                (dates[-1], ys[-1]),
                textcoords="offset points",
                xytext=(-4, 7),
                color=color,
                fontsize=8,
                fontweight="bold",
            )
    deadline = dt.date(2026, 8, 16)
    if dates[-1] > deadline:
        for a in (ax, ax_tv):
            a.axvline(deadline, color=TEXT_2, linewidth=1.0, linestyle="--", alpha=0.7)
            # 8/17~19 데일리는 매치메이킹 스로틀 구간(공식 수정 8/20, topic 735822)
            # 의 표집이라 상위 풀 구성이 흔들린다 — 아티팩트임을 그림에 명시.
            a.axvspan(dt.date(2026, 8, 16, ), dt.date(2026, 8, 19), color=GRID, alpha=0.45, zorder=0)
        ax.annotate(
            "submission deadline",
            (deadline, -3), ha="right", va="bottom", rotation=90,
            color=TEXT_2, fontsize=7.5, xytext=(-3, 0), textcoords="offset points",
        )
        ax.annotate(
            "matchmaking\nthrottled\n(fixed 8/20)",
            (dt.date(2026, 8, 17) + dt.timedelta(hours=12), 45), ha="center", va="top",
            color=TEXT_2, fontsize=7,
        )
    ax.set_xlim(dates[0] - dt.timedelta(days=0.5), dates[-1] + dt.timedelta(days=5.2))
    ax.set_ylim(-4, 47)
    ax.set_ylabel("share of top-pool deck-games (%)")
    ax.set_title("Top-pool meta converges toward the external (limitless) equilibrium", fontsize=10)
    ax.legend(frameon=False, fontsize=8, ncol=2, loc="upper left")
    ax.set_xticks(dates)
    ax.set_xticklabels([d.strftime("%m/%d") for d in dates], fontsize=8)
    ax_tv.tick_params(axis="x", labelrotation=45)

    ax_tv.plot(dates, tvs, color=TEXT, linewidth=2, marker="o", markersize=3)
    for i in (0, len(tvs) - 1):
        ax_tv.annotate(
            f"{tvs[i]:.3f}",
            (dates[i], tvs[i]),
            textcoords="offset points",
            xytext=(0, 7),
            color=TEXT_2,
            fontsize=7.5,
            ha="center",
        )
    ax_tv.set_ylabel("TV distance\nto equilibrium")
    ax_tv.set_xlabel("daily top-episodes dataset date (2026)")
    fig.tight_layout()
    out = FIG_DIR / "fig_meta_convergence.png"
    fig.savefig(out, dpi=200)
    print(f"saved {out}")
    for d, tv in zip(dates, tvs):
        print(f"  {d} TV={tv:.3f} " + " ".join(f"{n}={shares[n][dates.index(d)]:.1f}%" for n, _ in _META_LINES))


# 그림 A 색: 최종 빌드 포함 수술 vs 로컬 게이트만 통과(래더 미번역).
_SHIPPED = "#1baf7a"
_REJECTED = "#eb6834"


def cmd_cascade(args: argparse.Namespace) -> None:
    """그림 A: 결정 파이프라인(포크 골격 + 우선순위 캐스케이드)과 5개 수술 부위.

    구조 출처: candidates/h036_tempo_boss/{main.py,fork_policy.py} (h024b와의
    diff는 boss_kill_now 1건), 가드 수술은 candidates/h030·h034·h035 diff.
    """
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9.2, 6.4))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    def box(x, y, w, h, text, fc=SURFACE, ec=GRID, fs=8.5, color=TEXT, lw=1.2):
        ax.add_patch(
            plt.Rectangle((x, y), w, h, facecolor=fc, edgecolor=ec, linewidth=lw, zorder=2)
        )
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=color, zorder=3)

    def badge(x, y, label, color):
        ax.add_patch(plt.Circle((x, y), 2.6, facecolor=color, edgecolor="none", zorder=4))
        ax.text(x, y, label, ha="center", va="center", fontsize=7.5, color="white", fontweight="bold", zorder=5)

    def arrow(x0, y0, x1, y1):
        ax.annotate(
            "", xy=(x1, y1), xytext=(x0, y0),
            arrowprops={"arrowstyle": "->", "color": TEXT_2, "linewidth": 1.2}, zorder=1,
        )

    ax.text(
        27, 98, "one decision pipeline, five surgeries",
        ha="center", fontsize=11, fontweight="bold",
    )

    # -- 왼쪽: 결정 파이프라인 --
    box(4, 88, 46, 6, "main.py entrypoint (raw obs_dict)", fs=9)
    arrow(27, 88, 27, 84.5)
    box(4, 77, 46, 7, "lethal window?\nmy prizes ≤ 3 in MAIN, or committed kill-line replay", fs=8)
    badge(50, 84, "S1", _SHIPPED)
    box(58, 75.5, 38, 8.5, "h019 lethal machine\ncrystallized-turn search; kill committed\nonly after 2-of-2 fresh re-verification", fs=8)
    arrow(50, 80.5, 58, 80)
    ax.text(54, 82, "yes", fontsize=7.5, color=TEXT_2)
    arrow(27, 77, 27, 73.5)
    ax.text(29, 74.8, "no", fontsize=7.5, color=TEXT_2)

    box(4, 66, 46, 7, "Rozen V10 fork — score every legal option,\nplay the max (memetic-tuned weights)", fs=8.5)
    arrow(27, 66, 27, 63.5)

    tiers = [
        ("draw abilities (Dudunsparce / Fezandipiti)", "30k–38k", [("S2", _REJECTED), ("S4", _REJECTED)]),
        ("bench Pokémon", "~20k", []),
        ("stadium counters", "18.5k–19.5k", []),
        ("setup items (Poffin / Poke Pad / Rare Candy)", "12k–18k", []),
        ("recovery (Night Stretcher / Sacred Ash)", "11k–13.5k", []),
        ("evolve · tools · energy attach", "4k–9.8k", []),
        ("supporters: draw 3k–4.2k · Boss's Orders 2.3k", "", [("S5", _SHIPPED)]),
        ("retreat 2k–2.5k · attack ≤ 1k", "", []),
    ]
    y = 58.5
    for label, rng, badges in tiers:
        text = f"{label}   {rng}" if rng else label
        box(7, y, 40, 4.6, text, fs=7.5, ec="#d4d3cf")
        for i, (blabel, bcolor) in enumerate(badges):
            badge(50 + i * 5.5, y + 2.3, blabel, bcolor)
        y -= 5.4
    ax.annotate(
        "", xy=(5.2, 21), xytext=(5.2, 62),
        arrowprops={"arrowstyle": "->", "color": TEXT_2, "linewidth": 1.0}, zorder=1,
    )
    ax.text(3.4, 41, "priority", rotation=90, va="center", fontsize=7.5, color=TEXT_2)

    box(4, 8, 46, 5.5, "deck.csv — Alakazam list (fixed all run)", fs=8.5)
    badge(50, 10.8, "S3", _REJECTED)

    # -- 오른쪽: 수술 범례 --
    entries = [
        ("S1", _SHIPPED, "H-024b light lethal graft", "raw-dict gate delegates instantly outside the\nlethal window (kills the 150–390 ms overhead)"),
        ("S5", _SHIPPED, "H-036 tempo boss", "Boss's Orders 2262 → 6000 when the gust-kill\nis certain this turn (beats draw supporters)"),
        ("S2", _REJECTED, "H-030 deck-out guard", "ban ACTIVATE draw prompts of all four\n3-card draw abilities when deck margin < 3"),
        ("S4", _REJECTED, "H-035 stall guard", "stall_lock (turn ≥ 8, opp. 0 prizes, deck ≤ 18)\nfreezes every draw channel, draws only"),
        ("S3", _REJECTED, "H-034 mirror list", "swap deck.csv to the reconstructed\nmirror-winner list (policy already supports it)"),
    ]
    ly = 66
    for blabel, color, title, desc in entries:
        badge(60, ly + 1.5, blabel, color)
        ax.text(64, ly + 3.2, title, fontsize=8.5, fontweight="bold", color=TEXT, va="top")
        ax.text(64, ly - 0.2, desc, fontsize=7.3, color=TEXT_2, va="top")
        ly -= 11.5
    ax.add_patch(plt.Rectangle((57, 2.5), 40, 8.2, facecolor="none", edgecolor=GRID, linewidth=1))
    ax.add_patch(plt.Circle((60, 8.2), 1.6, facecolor=_SHIPPED, edgecolor="none"))
    ax.text(62.5, 8.2, "in the final build (h036 = fork + S1 + S5)", fontsize=7.5, va="center")
    ax.add_patch(plt.Circle((60, 4.8), 1.6, facecolor=_REJECTED, edgecolor="none"))
    ax.text(62.5, 4.8, "won every local gate, did not translate to ladder", fontsize=7.5, va="center")

    fig.tight_layout()
    out = FIG_DIR / "fig_cascade_surgeries.png"
    fig.savefig(out, dpi=200)
    print(f"saved {out}")


RATING_HISTORY = ROOT / "submissions" / "rating_history.tsv"
PAIR_CONVERGENCE = ROOT / "submissions" / "pair_convergence.tsv"
BUILD_RE = re.compile(r"^(?:\d{8}-)?(H-?[A-Za-z0-9]+?)(?:-\d+)?\s*[:—-]")


def _build_key(description: str) -> str:
    m = BUILD_RE.match(description or "")
    return m.group(1).replace("-", "").upper() if m else "?"


def _build_families() -> tuple[dict[str, list[float]], dict[str, str]]:
    """rating_history.tsv의 제출별 최신 레이팅을 빌드 가족으로 묶는다."""
    import csv

    latest: dict[str, dict] = {}
    order: dict[str, str] = {}
    with RATING_HISTORY.open(encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            if row["public_score"]:
                latest[row["submission_id"]] = row
    families: dict[str, list[float]] = {}
    for row in latest.values():
        key = _build_key(row["description"])
        families.setdefault(key, []).append(float(row["public_score"]))
        stamp = (row["description"] or "")[:8]
        if key not in order or stamp < order[key]:
            order[key] = stamp
    return families, order


def cmd_dist(args: argparse.Namespace) -> None:
    """그림 B: 빌드별 인스턴스 레이팅 분포 스트립 플롯."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    families, order = _build_families()
    keys = sorted(families, key=lambda k: (order.get(k, "99999999"), k))
    total = sum(len(v) for v in families.values())

    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    rng_state = 12345
    for i, key in enumerate(keys):
        vals = families[key]
        # 결정론적 지터(재현성 보장 — Math.random 불가 원칙과 동일 취지)
        jitter = [((rng_state * (j + 7) * (i + 3)) % 41 - 20) / 190.0 for j in range(len(vals))]
        big = len(vals) >= 5
        ax.scatter(
            [i + dx for dx in jitter],
            vals,
            s=44 if big else 30,
            color=SERIES[0] if big else TEXT_2,
            alpha=0.85 if big else 0.45,
            zorder=3,
            linewidths=0,
        )
        if len(vals) >= 3:
            lo, hi = min(vals), max(vals)
            ax.plot([i, i], [lo, hi], color=SERIES[0] if big else GRID, linewidth=1.4, zorder=2)
            mean = sum(vals) / len(vals)
            ax.plot(
                [i - 0.26, i + 0.26],
                [mean, mean],
                color=SERIES[1],
                linewidth=2.2,
                zorder=4,
                solid_capstyle="butt",
            )
            if big:
                ax.annotate(
                    f"n={len(vals)}\nspread {hi - lo:.0f}",
                    (i, hi),
                    textcoords="offset points",
                    xytext=(0, 9),
                    ha="center",
                    fontsize=8,
                    color=TEXT_2,
                )

    # 마감 후 수렴 페어를 별도 마커로 겹쳐 그린다.
    pair = _final_pair()
    if pair and "H036" in keys:
        x = keys.index("H036")
        ax.scatter(
            [x, x],
            pair,
            marker="*",
            s=210,
            color=SERIES[2],
            zorder=6,
            linewidths=0,
            label=f"final pair after 1,000 games each (gap {abs(pair[0] - pair[1]):.1f})",
        )
        ax.legend(frameon=False, loc="lower right", fontsize=9)

    ax.set_xticks(range(len(keys)))
    ax.set_xticklabels(keys, rotation=60, ha="right", fontsize=8)
    ax.set_ylabel("final ladder rating")
    ax.set_xlabel(f"build (chronological) — {total} submissions across {len(keys)} builds")
    ax.set_title(
        "Every build is a distribution: identical code, repeated submissions",
        fontsize=11,
        loc="left",
        pad=14,
    )
    fig.tight_layout()
    out = FIG_DIR / "fig_build_distribution.png"
    fig.savefig(out, dpi=200)
    print(f"saved {out}")
    for key in keys:
        vals = sorted(families[key])
        if len(vals) >= 3:
            mean = sum(vals) / len(vals)
            print(f"  {key:<8} n={len(vals):<2} {vals[0]:6.1f}~{vals[-1]:6.1f} mean={mean:6.1f} spread={vals[-1] - vals[0]:5.1f}")


OPPONENT_LABELS = {
    "candidates/h024b_light": "mirror\n(previous build)",
    "candidates/opp_meta0d": "distilled-opponent\ngate",
    "candidates/opp_grimmsnarl": "counter-archetype\nproxy",
}


def cmd_matrix(args: argparse.Namespace) -> None:
    """그림 D: 좌석 × 상대 승률 행렬. 두 좌석 모두에서 성립하는지가 강건성 주장의 핵심."""
    import collections

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    runs = _load_runs(args.runs)
    cells: dict[tuple[str, int], collections.Counter] = collections.defaultdict(collections.Counter)
    for run in runs:
        for rec in run["records"]:
            cells[(rec["opponent"], int(rec["candidate_seat"]))][rec["outcome"]] += 1

    opponents = sorted({k[0] for k in cells}, key=lambda o: OPPONENT_LABELS.get(o, o))
    fig, ax = plt.subplots(figsize=(6.4, 0.9 * len(opponents) + 2.0))
    for j, opp in enumerate(opponents):
        for seat in (0, 1):
            c = cells.get((opp, seat))
            if not c:
                continue
            games = sum(c.values())
            wr = c["win"] / games if games else 0.0
            # 0.5를 중심으로 발산 색상: 파랑(우세) / 주황(열세)
            mag = min(abs(wr - 0.5) / 0.35, 1.0)
            color = SERIES[0] if wr >= 0.5 else SERIES[1]
            ax.barh(j + (seat - 0.5) * 0.38, 1.0, height=0.34, color=GRID, zorder=1)
            ax.barh(j + (seat - 0.5) * 0.38, wr, height=0.34, color=color, alpha=0.25 + 0.65 * mag, zorder=2)
            ax.annotate(
                f"seat {seat}   {wr * 100:.1f}%   n={games}",
                (0.015, j + (seat - 0.5) * 0.38),
                va="center",
                fontsize=9,
                color=TEXT,
                zorder=3,
            )
    ax.axvline(0.5, color=TEXT_2, linewidth=1.0, linestyle="--", zorder=4)
    ax.set_yticks(range(len(opponents)))
    ax.set_yticklabels([OPPONENT_LABELS.get(o, Path(o).name) for o in opponents], fontsize=9)
    ax.set_xlim(0, 1)
    ax.set_xlabel("win rate (dashed line = 50%)")
    ax.invert_yaxis()
    ax.grid(False)
    ax.set_title(
        "Every gate, both seats — and the two that saturated",
        fontsize=10,
        loc="left",
        pad=12,
    )
    fig.tight_layout()
    out = FIG_DIR / "fig_seat_matrix.png"
    fig.savefig(out, dpi=200)
    print(f"saved {out}")
    for opp in opponents:
        for seat in (0, 1):
            c = cells.get((opp, seat))
            if c:
                g = sum(c.values())
                print(f"  {Path(opp).name:<18} seat{seat}  {c['win'] / g * 100:5.1f}%  n={g}")


def cmd_convergence(args: argparse.Namespace) -> None:
    """그림 E: 좌 = sticky placement 스파이크, 우 = 동일 코드 페어의 1,000경기 수렴."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    spike_sid = int(args.spike)
    pair_sids = [int(s) for s in args.pair.split(",")]

    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(10, 3.9), gridspec_kw={"width_ratios": [1, 2.1]})

    rows = _ladder_rows(spike_sid)
    ratings = [r["rating"] for r in rows]
    ax_l.plot(range(1, len(ratings) + 1), ratings, color=SERIES[3], linewidth=2)
    if ratings:
        peak = max(ratings)
        peak_x = ratings.index(peak) + 1
        ax_l.annotate(
            f"{peak:.0f} after a 4–1 start",
            (peak_x, peak),
            textcoords="offset points",
            xytext=(6, 4),
            fontsize=8,
            color=TEXT_2,
        )
        ax_l.annotate(
            f"{ratings[-1]:.0f} by game {len(ratings)}",
            (len(ratings), ratings[-1]),
            textcoords="offset points",
            xytext=(-10, -14),
            ha="right",
            fontsize=8,
            color=TEXT_2,
        )
    ax_l.set_title("Placement luck is amortized, not banked", fontsize=10, loc="left")
    ax_l.set_xlabel("ladder game #")
    ax_l.set_ylabel("rating")

    finals, series = [], []
    for i, sid in enumerate(pair_sids):
        rows = _ladder_rows(sid)
        ratings = [r["rating"] for r in rows]
        if not ratings:
            continue
        finals.append(ratings[-1])
        series.append(ratings)
        ax_r.plot(range(1, len(ratings) + 1), ratings, color=SERIES[i], linewidth=0.7, alpha=0.35)
        window = 101
        smooth = [
            sum(ratings[max(0, k - window + 1) : k + 1]) / len(ratings[max(0, k - window + 1) : k + 1])
            for k in range(len(ratings))
        ]
        mean = sum(ratings) / len(ratings)
        ax_r.plot(
            range(1, len(ratings) + 1),
            smooth,
            color=SERIES[i],
            linewidth=2.2,
            label=f"instance {i + 8} — 1,000-game mean {mean:.1f}",
        )

    if len(series) == 2:
        n = min(len(series[0]), len(series[1]))
        gaps = [abs(series[0][k] - series[1][k]) for k in range(n)]
        mean_gap = abs(sum(series[0]) / len(series[0]) - sum(series[1]) / len(series[1]))
        ax_r.annotate(
            f"difference in 1,000-game means: {mean_gap:.1f}\n"
            f"same-moment gap: mean {sum(gaps) / n:.1f}, max {max(gaps):.1f}",
            (0.985, 0.06),
            xycoords="axes fraction",
            ha="right",
            va="bottom",
            fontsize=8.5,
            color=TEXT,
        )

    ax_r.set_title(
        "…but 1,000 games buys a band, not a point estimate",
        fontsize=10,
        loc="left",
    )
    ax_r.set_xlabel("post-deadline ladder game #")
    ax_r.legend(frameon=False, loc="upper left", fontsize=8)

    fig.tight_layout()
    out = FIG_DIR / "fig_convergence.png"
    fig.savefig(out, dpi=200)
    print(f"saved {out}")


def _final_pair() -> list[float]:
    """pair_convergence.tsv의 마지막 스냅샷에서 i8/i9 최종 레이팅을 읽는다."""
    if not PAIR_CONVERGENCE.exists():
        return []
    lines = [ln.strip().split("\t") for ln in PAIR_CONVERGENCE.read_text(encoding="utf-8").splitlines() if ln.strip()]
    body = [ln for ln in lines if len(ln) > 3 and ln[0][:1].isdigit()]
    if len(body) < 2:
        return []
    stamp = body[-1][0]
    return [float(ln[3]) for ln in body if ln[0] == stamp]


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

    meta = commands.add_parser("meta")
    meta.add_argument("--dumps", default="scratch/decks_*.json")
    meta.set_defaults(func=cmd_meta)

    cascade = commands.add_parser("cascade")
    cascade.set_defaults(func=cmd_cascade)

    dist = commands.add_parser("dist")
    dist.set_defaults(func=cmd_dist)

    matrix = commands.add_parser("matrix")
    matrix.add_argument("--runs", nargs="+", required=True)
    matrix.set_defaults(func=cmd_matrix)

    conv = commands.add_parser("convergence")
    conv.add_argument("--pair", default="55525772,55525773")
    conv.add_argument("--spike", default="55515319")
    conv.set_defaults(func=cmd_convergence)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
