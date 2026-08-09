"""H-024: 공개 룰 정책(fork_policy) + 검증형 리썰 커밋 탐색 그래프트.

일반 턴은 포크의 가중치 룰 정책이 결정한다. 내 잔여 프라이즈가 3 이하인 MAIN
결정에서만 결정화 탐색으로 "이번 턴 승리 라인"을 찾고, 신선한 결정화 재검증으로
2회 이상 승리가 확인될 때만 라인 전체를 커밋해 descriptor 기준으로 재생한다.
(1341 공개 에이전트의 "Normal turns rules, winning turns search" 공식 +
우리 H-019에서 검증한 커밋·재생·프라이즈 추론 기계를 결합)

출처: 룰 정책은 romanrozen/strong-start-baseline-agent-v10-lb-950 (jazivxt 파생),
리썰 기계는 우리 h019_lethal_prize.
"""

import importlib.util
import sys
import time as _time
from pathlib import Path

_HERE = Path(__file__).resolve().parent if "__file__" in globals() else Path(".").resolve()


def _load_module(name: str):
    """실행 환경별 경로 체인에서 동봉 모듈을 찾는다(__file__ 부재 대응)."""
    if name in sys.modules:
        return sys.modules[name]
    for base in (_HERE, Path.cwd(), Path("/kaggle_simulations/agent")):
        path = Path(base) / f"{name}.py"
        if path.is_file():
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            return module
    raise ImportError(f"bundled module not found: {name}")


fork_policy = _load_module("fork_policy")  # 포크 룰 정책 (최종 진입: codex_sol_eclipse_alakazam_v22)
ls = _load_module("lethal_search")  # h019 탐색·리썰·프라이즈 추론 기계

LETHAL_PRIZE_TRIGGER = 3  # 내 잔여 프라이즈가 이하일 때만 리썰 탐색
LETHAL_BUDGET_SECONDS = 2.6
LETHAL_OVERAGE_FLOOR = 200.0
_DIAG = {"probe": 0, "commit": 0, "replay": 0, "fallback": 0}


def _lethal_probe(obs, budget_seconds: float = LETHAL_BUDGET_SECONDS):
    """승리 종단만 노리는 2결정화 탐색 + 재검증 커밋. 없으면 None."""
    start = _time.perf_counter()
    win_votes: dict = {}
    win_paths: dict = {}
    for _ in range(2):
        remaining = start + budget_seconds - _time.perf_counter()
        if remaining <= 0.3:
            break
        _values, wins = ls._search_once(obs, min(remaining, budget_seconds / 2 + 0.2))
        for key, path in wins.items():
            win_votes[key] = win_votes.get(key, 0) + 1
            if key not in win_paths or len(path) < len(win_paths[key]):
                win_paths[key] = path
    if not win_votes:
        return None
    key, count = max(win_votes.items(), key=lambda kv: kv[1])
    path = win_paths[key]
    if count < 2:
        count += ls._verify_win_line(obs, path, tries=2)
    if count >= 2:
        ls._WIN_LINE["turn"] = obs.current.turn
        ls._WIN_LINE["steps"] = list(path[1:]) or None
        _DIAG["commit"] += 1
        return list(key)
    return None


def agent(obs_dict: dict):
    try:
        obs = ls.to_observation_class(obs_dict)
    except Exception:  # noqa: BLE001
        return fork_policy.codex_sol_eclipse_alakazam_v22(obs_dict)
    if obs.select is None or obs.current is None:
        return fork_policy.codex_sol_eclipse_alakazam_v22(obs_dict)
    try:
        try:
            ls._update_prize_inference(obs)
        except Exception:  # noqa: BLE001
            pass
        # 커밋된 승리 라인 재생이 최우선 (모든 select 컨텍스트에서)
        step = ls._pop_win_step(obs)
        if step is not None:
            n = len(obs.select.option or [])
            if all(0 <= i < n for i in step):
                _DIAG["replay"] += 1
                return step
        state = obs.current
        me = state.players[state.yourIndex]
        overage = float(obs_dict.get("remainingOverageTime") or 600.0)
        if (
            obs.search_begin_input is not None
            and obs.select.option
            and len(obs.select.option) > 1
            and int(obs.select.context) == int(ls.SelectContext.MAIN)
            and len(me.prize) <= LETHAL_PRIZE_TRIGGER
            and overage > LETHAL_OVERAGE_FLOOR
        ):
            _DIAG["probe"] += 1
            picked = _lethal_probe(obs)
            if picked is not None:
                n = len(obs.select.option)
                if (
                    obs.select.minCount <= len(picked) <= obs.select.maxCount
                    and all(0 <= i < n for i in picked)
                ):
                    return picked
    except Exception:  # noqa: BLE001 - 그래프트 실패는 포크 정책으로 흡수
        _DIAG["fallback"] += 1
    return fork_policy.codex_sol_eclipse_alakazam_v22(obs_dict)


def h024_lethal_graft_entry(obs_dict):
    return agent(obs_dict)
