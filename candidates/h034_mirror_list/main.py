"""H-024b: H-024 리썰 그래프트의 경량 래퍼 (per-decision 오버헤드 제거).

H-024 래더 실측(714/646, 포크 밴드 786~819 대비 열세)의 유력 원인은 지연이다:
로컬 per-move 평균이 바닐라 20~70ms vs H-024 150~390ms — 래퍼가 매 결정마다
to_observation_class 재변환 + 프라이즈 추론을 수행했기 때문. 느린 래더 CPU에서
overage 소모 → 시간 열세로 이어졌다는 가설.

수정: 원시 obs_dict만 보고 리썰 창(내 프라이즈 ≤3인 MAIN 결정, 또는 커밋된
승리 라인 재생 중)인지 선별한다. 창 밖에서는 변환·추론 없이 즉시 포크 정책에
위임한다. 리썰 기계 자체(2결정화 발견 + 신선 재검증 합산 2승 커밋)는 H-024와 동일.

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
_MAIN_CONTEXT = 0  # SelectContext.MAIN — 원시 dict 선별용 상수
_DIAG = {"probe": 0, "commit": 0, "replay": 0, "fallback": 0, "heavy": 0}


def _raw_lethal_window(obs_dict: dict) -> bool:
    """dataclass 변환 없이 리썰 기계가 개입할 수 있는 결정인지 판별한다."""
    if ls._WIN_LINE.get("steps"):  # 커밋된 라인 재생 중 — 모든 select에서 heavy 경로
        return True
    sel = obs_dict.get("select")
    cur = obs_dict.get("current")
    if not isinstance(sel, dict) or not isinstance(cur, dict):
        return False
    context = sel.get("context")  # 주의: MAIN=0은 falsy — `or` 기본값 금지
    if context is None or int(context) != _MAIN_CONTEXT:
        return False
    option = sel.get("option") or []
    if len(option) <= 1 or not obs_dict.get("search_begin_input"):
        return False
    try:
        me = cur["players"][int(cur["yourIndex"])]
        if len(me.get("prize") or []) > LETHAL_PRIZE_TRIGGER:
            return False
    except (KeyError, IndexError, TypeError, ValueError):
        return False
    return float(obs_dict.get("remainingOverageTime") or 600.0) > LETHAL_OVERAGE_FLOOR


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
    # 경량 선별: 리썰 창 밖이면 변환 비용 없이 즉시 포크 위임
    try:
        if not _raw_lethal_window(obs_dict):
            return fork_policy.codex_sol_eclipse_alakazam_v22(obs_dict)
    except Exception:  # noqa: BLE001
        return fork_policy.codex_sol_eclipse_alakazam_v22(obs_dict)

    _DIAG["heavy"] += 1
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
        # 커밋된 승리 라인 재생이 최우선
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


def h024b_light_entry(obs_dict):
    return agent(obs_dict)
