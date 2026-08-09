"""후보의 전체 에이전트 결정(agent())을 상위 파일럿의 실제 선택과 비교한다.

distill_replays의 held-out 일치율은 choose()(증류 경로)만 쟀다. 이 프로브는
search 경로를 포함한 agent() 전체를 replay의 실제 결정 상태(search_begin_input
포함) 위에서 실행해, 경기 없이 결정 수준에서 정책을 검증한다.

사용:
  uv run python scripts/agreement_probe.py --episodes data/raw/episodes/majkel_lucario \
    --candidate candidates/h013_search_scaled --limit 300
"""

from __future__ import annotations

import argparse
import collections
import random
import time
from pathlib import Path

from distill_replays import iter_decisions, load_candidate, load_episodes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--holdout-mod", type=int, default=5, help="episode_id %% mod == 0 만 사용")
    parser.add_argument("--limit", type=int, default=300, help="샘플링할 MAIN 결정 수")
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    module = load_candidate(Path(args.candidate).resolve())
    episodes = load_episodes(Path(args.episodes))
    decisions = []
    for episode_id, episode, seats in episodes:
        if episode_id % args.holdout_mod != 0:
            continue
        for seat in seats:
            for obs_dict, action in iter_decisions(episode, seat):
                select = obs_dict.get("select") or {}
                if select.get("context") == 0 and obs_dict.get("search_begin_input"):
                    decisions.append((obs_dict, action))
    random.Random(args.seed).shuffle(decisions)
    decisions = decisions[: args.limit]
    print(f"probing {len(decisions)} held-out MAIN decisions (agent() incl. search path)")

    match = total = 0
    per_type = collections.defaultdict(lambda: [0, 0])
    started = time.perf_counter()
    for obs_dict, action in decisions:
        if hasattr(module, "_search_spent"):
            module._search_spent["seconds"] = 0.0  # 경기 단위 캡이 프로브에 누적되지 않게 리셋
        try:
            predicted = module.agent(obs_dict)
        except Exception:  # noqa: BLE001
            predicted = []
        obs = module.to_observation_class(obs_dict)
        hit = set(predicted) == set(action)
        total += 1
        match += hit
        if action and obs.select and action[0] < len(obs.select.option):
            label = module.type_name(obs.select.option[action[0]].type)
            per_type[label][0] += hit
            per_type[label][1] += 1
    elapsed = time.perf_counter() - started
    print(f"agreement: {match}/{total} = {match/max(total,1):.3f} ({elapsed:.0f}s, {elapsed/max(total,1)*1000:.0f}ms/decision)")
    for label, (m, c) in sorted(per_type.items(), key=lambda kv: -kv[1][1]):
        print(f"  pilot chose {label}: {m}/{c} = {m/max(c,1):.3f}")


if __name__ == "__main__":
    main()
