"""H-022 포크의 alak_w.json 가중치 CEM 튜닝.

세대마다 K개 설정을 로그정규 섭동으로 샘플하고, 고정 상대 풀에 대한 승수로
엘리트를 뽑아 평균·분산을 갱신한다. 각 설정은 evaluate.py를 서브프로세스로
호출해 양 좌석 경기로 측정한다(비결정 엔진 → 표본 규율 유지).

사용:
  uv run python scripts/tune_alak.py --generations 6 --pop 16 --games-per-seat 6 \
    --opponents candidates/opp_meta0d,candidates/h022_alak_fork \
    --out research_loop/tune_alak
"""

from __future__ import annotations

import argparse
import json
import math
import random
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "candidates" / "h022_alak_fork"

# 전체 70개 중 게임플레이 우선순위에 큰 영향을 주는 축만 섭동한다.
# (카드 존재 여부와 무관한 구조 가중치는 제외해 탐색 차원을 낮춘다)
TUNE_KEYS = [
    "play_pokemon_base", "play_bench_penalty", "poffin_early", "poffin_late",
    "pokepad_early", "pokepad_need", "rare_candy", "boss_kill", "hilda",
    "dawn_emergency", "dawn", "evolve_base", "ability_default", "ability_dudun",
    "ability_fez", "attack_base", "attack_powerful", "attack_psybolt_kill",
    "attack_psybolt", "attack_teleport", "retreat_kadabra", "retreat_promote",
    "hammer_target", "hammer_any", "night_stretcher_mon", "night_stretcher_energy",
    "sacred_ash_hi", "sacred_ash_lo", "cage_counter", "cage_snipe", "jamming_tools",
    "jamming_counter", "nz_ex", "nz_counter", "energy_retreat", "energy_abra",
]


def load_defaults() -> dict:
    import re

    text = (BASE / "main.py").read_text()
    weights: dict = {}
    for m in re.finditer(r'"([a-z_0-9]+)":\s*(-?\d+(?:\.\d+)?)', text):
        weights.setdefault(m.group(1), float(m.group(2)))
    missing = [k for k in TUNE_KEYS if k not in weights]
    if missing:
        raise SystemExit(f"missing keys in main.py: {missing}")
    return {k: weights[k] for k in TUNE_KEYS}


def eval_config(config: dict, opponents: str, games_per_seat: int, tag: str) -> dict:
    """설정을 임시 후보로 만들어 evaluate.py로 측정, 요약을 돌려준다."""
    cand = ROOT / "research_loop" / "tune_alak" / f"cand_{tag}"
    if cand.exists():
        shutil.rmtree(cand)
    cand.mkdir(parents=True)
    for name in ("main.py", "deck.csv"):
        shutil.copy(BASE / name, cand / name)
    (cand / "alak_w.json").write_text(json.dumps(config))
    run = subprocess.run(
        [
            sys.executable, str(ROOT / "scripts" / "evaluate.py"),
            "--candidate", str(cand),
            "--opponents", opponents,
            "--games-per-seat", str(games_per_seat),
        ],
        capture_output=True, text=True, cwd=ROOT, timeout=7200, check=False,
    )
    out = run.stdout.strip().splitlines()
    run_path = None
    for line in reversed(out):
        if line.startswith("run: "):
            run_path = ROOT / line[len("run: "):]
            break
    if run_path is None or not run_path.exists():
        return {"wins": -1, "games": 0, "error": run.stderr[-400:]}
    payload = json.loads(run_path.read_text())
    total = payload["summary"]
    return {"wins": total["wins"], "games": total["games"], "win_rate": total["win_rate"]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generations", type=int, default=6)
    parser.add_argument("--pop", type=int, default=16)
    parser.add_argument("--elite", type=int, default=4)
    parser.add_argument("--games-per-seat", type=int, default=6)
    parser.add_argument("--sigma", type=float, default=0.25, help="로그공간 초기 표준편차")
    parser.add_argument("--opponents", default="candidates/opp_meta0d,candidates/h022_alak_fork")
    parser.add_argument("--out", default="research_loop/tune_alak")
    args = parser.parse_args()

    out_dir = ROOT / args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "cem_log.jsonl"

    defaults = load_defaults()
    mu = {k: math.log(max(v, 1.0)) for k, v in defaults.items()}
    sigma = {k: args.sigma for k in TUNE_KEYS}
    rng = random.Random(20260809)

    best = {"score": -1.0, "config": None}
    for gen in range(args.generations):
        population = []
        for i in range(args.pop):
            if gen == 0 and i == 0:
                config = dict(defaults)  # 엘리트 보존: 기본값 자체를 항상 후보에 포함
            else:
                config = {k: round(math.exp(rng.gauss(mu[k], sigma[k])), 2) for k in TUNE_KEYS}
            result = eval_config(config, args.opponents, args.games_per_seat, f"g{gen}i{i}")
            score = result.get("win_rate", 0.0) if result.get("games") else 0.0
            population.append((score, config, result))
            print(f"gen{gen} cand{i}: {score:.3f} ({result.get('wins')}/{result.get('games')})", flush=True)
        population.sort(key=lambda t: -t[0])
        # 승자의 저주 방지: 1차 상위 2*elite를 신선한 표본으로 재평가해
        # 재평가 점수만으로 엘리트를 선발한다 (선택 노이즈 증폭 차단).
        finalists = population[: args.elite * 2]
        rescored = []
        for j, (_, config, _) in enumerate(finalists):
            re_result = eval_config(config, args.opponents, args.games_per_seat, f"g{gen}re{j}")
            re_score = re_result.get("win_rate", 0.0) if re_result.get("games") else 0.0
            rescored.append((re_score, config, re_result))
            print(f"gen{gen} re-eval{j}: {re_score:.3f}", flush=True)
        rescored.sort(key=lambda t: -t[0])
        elites = rescored[: args.elite]
        for k in TUNE_KEYS:
            values = [math.log(max(c[k], 1.0)) for _, c, _ in elites]
            mean = sum(values) / len(values)
            var = sum((v - mean) ** 2 for v in values) / len(values)
            mu[k] = mean
            sigma[k] = max(0.05, min(0.4, math.sqrt(var) + 0.02))
        gen_best = elites[0]
        if gen_best[0] > best["score"]:
            best = {"score": gen_best[0], "config": gen_best[1]}
        with log_path.open("a") as f:
            f.write(json.dumps({
                "gen": gen,
                "scores": [round(s, 3) for s, _, _ in population],
                "best_score": best["score"],
            }) + "\n")
        (out_dir / "best_alak_w.json").write_text(json.dumps(best["config"], indent=1))
        print(f"gen{gen} done: elite={[round(s,3) for s,_,_ in elites]} best={best['score']:.3f}", flush=True)

    print(f"final best {best['score']:.3f} -> {out_dir/'best_alak_w.json'}")


if __name__ == "__main__":
    main()
