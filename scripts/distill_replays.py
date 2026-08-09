"""Majkel Lucario replay를 (문맥, descriptor) 선택률 표로 증류한다 (H-006R).

episode를 80/20으로 나눠 train으로 policy_table.json을 만들고,
held-out에서 후보 정책과 실제 선택의 일치율을 잰다.

사용:
  uv run python scripts/distill_replays.py \
    --episodes data/raw/episodes/majkel_lucario \
    --candidate candidates/h006r_majkel_lucario
"""

from __future__ import annotations

import argparse
import collections
import importlib.util
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_candidate(candidate_dir: Path):
    sys.path.insert(0, str(ROOT / "data" / "raw" / "sample_submission"))
    previous = Path.cwd()
    os.chdir(candidate_dir)
    try:
        spec = importlib.util.spec_from_file_location("h006r_policy", candidate_dir / "main.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        os.chdir(previous)
    return module


def iter_decisions(episode: dict, seat: int):
    steps = episode["steps"]
    for t in range(len(steps) - 1):
        state = steps[t][seat]
        if state["status"] != "ACTIVE":
            continue
        obs = state["observation"]
        select = obs.get("select")
        if not select or not select.get("option"):
            continue
        action = steps[t + 1][seat]["action"]
        if action is None or not isinstance(action, list):
            continue
        n = len(select["option"])
        if any(not isinstance(i, int) or i < 0 or i >= n for i in action):
            continue
        yield obs, action


def load_episodes(
    episodes_dir: Path,
    teams: set[str] | None = None,
    winning_only: bool = False,
) -> list[tuple[int, dict, list[int]]]:
    """다중 파일럿 replay에서 좌석 품질 필터를 지원한다.

    teams: 지정 시 해당 팀이 조종한 좌석만 사용한다.
    winning_only: 승리한 좌석만 사용한다(패자 모방 방지).
    """
    rows = []
    for meta_path in sorted(episodes_dir.glob("*.json.meta")):
        meta = json.loads(meta_path.read_text())
        seats = list(meta["seats"])
        if teams is not None:
            seats = [s for s in seats if meta["teams"][s] in teams]
        if winning_only:
            rewards = meta.get("rewards")
            if rewards is None or None in rewards:
                continue
            seats = [s for s in seats if rewards[s] > rewards[1 - s]]
        if not seats:
            continue
        episode = json.loads((episodes_dir / meta["file"]).read_text())
        episode_id = int(meta["file"].split(".")[0])
        rows.append((episode_id, episode, seats))
    return rows


def build_table(module, decisions) -> dict:
    table: dict = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    for obs_dict, action in decisions:
        obs = module.to_observation_class(obs_dict)
        if obs.select is None:
            continue
        chosen = set(action)
        for key in (module.select_key(obs.select), module.sub_key(obs)):
            entry = table[key]
            for i, option in enumerate(obs.select.option):
                desc = module.describe(obs, option)
                hit = 1 if i in chosen else 0
                entry[desc][0] += hit
                entry[desc][1] += 1
                agg = entry[f"~{module.type_name(option.type)}"]
                agg[0] += hit
                agg[1] += 1
            entry["_pick"][0] += len(action)
            entry["_pick"][1] += 1
    return {key: {desc: list(v) for desc, v in descs.items()} for key, descs in table.items()}


def agreement(module, decisions) -> dict:
    per_context = collections.defaultdict(lambda: [0, 0])
    total = [0, 0]
    for obs_dict, action in decisions:
        obs = module.to_observation_class(obs_dict)
        if obs.select is None:
            continue
        try:
            predicted = module.choose(obs)
        except Exception:  # noqa: BLE001 - 후보의 런타임 fallback과 동일하게 취급한다.
            predicted = []
        match = 1 if set(predicted) == set(action) else 0
        label = f"{int(obs.select.type)}|{int(obs.select.context)}"
        per_context[label][0] += match
        per_context[label][1] += 1
        total[0] += match
        total[1] += 1
    return {"total": total, "per_context": dict(per_context)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--holdout-mod", type=int, default=5)
    parser.add_argument("--teams", help="쉼표 구분 팀명. 해당 팀 좌석만 증류")
    parser.add_argument("--winning-only", action="store_true", help="승리 좌석만 증류")
    parser.add_argument(
        "--extra-episodes",
        help="train에만 합칠 추가 episode 디렉토리(다른 시그니처의 유사 아키타입). holdout은 --episodes에서만 뽑는다",
    )
    args = parser.parse_args()

    candidate_dir = Path(args.candidate).resolve()
    teams = set(args.teams.split(",")) if args.teams else None
    episodes = load_episodes(Path(args.episodes), teams=teams, winning_only=args.winning_only)
    train_decisions, holdout_decisions = [], []
    for episode_id, episode, seats in episodes:
        bucket = holdout_decisions if episode_id % args.holdout_mod == 0 else train_decisions
        for seat in seats:
            bucket.extend(iter_decisions(episode, seat))
    if args.extra_episodes:
        for _, episode, seats in load_episodes(
            Path(args.extra_episodes), teams=teams, winning_only=args.winning_only
        ):
            for seat in seats:
                train_decisions.extend(iter_decisions(episode, seat))
    print(f"episodes={len(episodes)} train_decisions={len(train_decisions)} holdout_decisions={len(holdout_decisions)}")

    module = load_candidate(candidate_dir)
    table = build_table(module, train_decisions)
    out = candidate_dir / "policy_table.json"
    out.write_text(json.dumps(table))
    print(f"table keys={len(table)} size={out.stat().st_size/1024:.0f}KiB -> {out}")

    module.TABLE.clear()
    module.TABLE.update(table)
    result = agreement(module, holdout_decisions)
    match, n = result["total"]
    print(f"holdout agreement: {match}/{n} = {match/max(n,1):.3f}")
    main_key = "0|0"
    for label, (m, c) in sorted(result["per_context"].items(), key=lambda kv: -kv[1][1])[:12]:
        note = "  <-- MAIN" if label == main_key else ""
        print(f"  key {label}: {m}/{c} = {m/max(c,1):.3f}{note}")


if __name__ == "__main__":
    main()
