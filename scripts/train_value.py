"""replay (상태, 승패) 쌍으로 로지스틱 가치함수를 학습한다 (H-014).

탐색 평가에 쓸 수 있도록, search 상태(State dataclass)에서 계산 가능한
특징만 사용한다. episode 단위 80/20 분할로 held-out AUC/logloss를 보고
가중치를 value_weights.json 으로 내보낸다.

사용:
  uv run python scripts/train_value.py \
    --episodes data/raw/episodes/majkel_lucario data/raw/episodes/lopunny_pure data/raw/episodes/lopunny_hybrid \
    --out candidates/h013_search_scaled/value_weights.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "data" / "raw" / "sample_submission"))

from cg.api import all_attack, all_card_data  # noqa: E402

CARDS = {c.cardId: c for c in all_card_data()}
ATTACKS = {a.attackId: a for a in all_attack()}

FEATURE_NAMES = [
    "prize_diff",          # 상대 남은 프라이즈 - 내 남은 프라이즈 (앞서면 +)
    "my_prize_left",
    "opp_board_damage",    # 상대 보드 누적 데미지 합 /100
    "my_board_damage",
    "my_energy_total",
    "opp_energy_total",
    "my_mega_count",
    "opp_mega_count",
    "my_stage1plus",
    "opp_stage1plus",
    "my_board_count",
    "opp_board_count",
    "my_hand",
    "opp_hand",
    "my_deck_low",         # max(0, 7 - deckCount)
    "opp_deck_low",
    "my_active_progress",  # 액티브 최고공격 에너지 진행률(0~1) * dmg/100
    "opp_active_progress",
    "my_status_bad",       # 마비/수면
    "turn_norm",           # turn/30
]

# v2 핸드 구성 특징 (H-018): fetch/드로우의 가치를 상태에서 볼 수 있게 한다.
# 학습은 핸드가 보이는(내 결정) 상태로 제한된다.
FEATURE_NAMES_V2 = FEATURE_NAMES + [
    "my_hand_energy",      # 핸드의 에너지 카드 수
    "my_hand_basic",       # 핸드의 베이식 포켓몬 수 (벤치 전개 여력)
    "my_hand_evo_ready",   # 내 보드 포켓몬에서 진화 가능한 핸드 카드 수
    "my_deck_consumed",    # max(0, 46 - deckCount)/10 — 드로우/서치 진행도
]

ENERGY_TYPES = {5, 6}  # BASIC_ENERGY, SPECIAL_ENERGY
NAME_BY_ID = {cid: c.name for cid, c in CARDS.items()}


def hand_features(hand_ids: list[int], board_ids: list[int], deck_count: int) -> list[float]:
    board_names = {NAME_BY_ID.get(i) for i in board_ids}
    energy = basic = evo = 0
    for cid in hand_ids:
        data = CARDS.get(cid)
        if data is None:
            continue
        if int(data.cardType) in ENERGY_TYPES:
            energy += 1
        elif data.basic:
            basic += 1
        if data.evolvesFrom and data.evolvesFrom in board_names:
            evo += 1
    return [float(energy), float(basic), float(evo), max(0.0, 46.0 - deck_count) / 10.0]


def attack_progress(pokemon: dict) -> float:
    data = CARDS.get(pokemon.get("id"))
    if data is None:
        return 0.0
    n_energy = len(pokemon.get("energies") or [])
    best = 0.0
    for attack_id in data.attacks:
        attack = ATTACKS.get(attack_id)
        if attack is None:
            continue
        need = max(len(attack.energies), 1)
        have = min(n_energy, need)
        best = max(best, (attack.damage or 80) / 100.0 * (have / need) ** 2)
    return best


def stage_counts(board: list[dict]) -> tuple[int, int]:
    mega = stage1plus = 0
    for p in board:
        data = CARDS.get(p.get("id"))
        if data is None:
            continue
        if data.megaEx:
            mega += 1
        if data.stage1 or data.stage2:
            stage1plus += 1
    return mega, stage1plus


def featurize(state: dict, mi: int, v2: bool = False) -> list[float] | None:
    players = state.get("players")
    if not players or len(players) != 2:
        return None
    me, opp = players[mi], players[1 - mi]
    if v2 and not isinstance(me.get("hand"), list):
        return None  # v2는 핸드가 보이는 상태만 학습한다

    def board(p):
        return [x for x in (list(p.get("active") or []) + list(p.get("bench") or [])) if x]

    mb, ob = board(me), board(opp)
    my_mega, my_s1 = stage_counts(mb)
    opp_mega, opp_s1 = stage_counts(ob)
    my_active = (me.get("active") or [None])[0]
    opp_active = (opp.get("active") or [None])[0]
    return [
        len(opp.get("prize") or []) - len(me.get("prize") or []),
        len(me.get("prize") or []),
        sum((p.get("maxHp", 0) - p.get("hp", 0)) for p in ob) / 100.0,
        sum((p.get("maxHp", 0) - p.get("hp", 0)) for p in mb) / 100.0,
        float(sum(len(p.get("energies") or []) for p in mb)),
        float(sum(len(p.get("energies") or []) for p in ob)),
        float(my_mega),
        float(opp_mega),
        float(my_s1),
        float(opp_s1),
        float(len(mb)),
        float(len(ob)),
        float(me.get("handCount", 0)),
        float(opp.get("handCount", 0)),
        float(max(0, 7 - me.get("deckCount", 60))),
        float(max(0, 7 - opp.get("deckCount", 60))),
        attack_progress(my_active) if my_active else 0.0,
        attack_progress(opp_active) if opp_active else 0.0,
        float(bool(me.get("paralyzed")) or bool(me.get("asleep"))),
        min(state.get("turn", 0), 30) / 30.0,
    ] + (
        hand_features(
            [h.get("id") for h in me.get("hand") or [] if isinstance(h, dict)],
            [p.get("id") for p in mb],
            me.get("deckCount", 60),
        )
        if v2
        else []
    )


def collect(episodes_dir: Path, holdout_mod: int, v2: bool = False):
    train_x, train_y, hold_x, hold_y = [], [], [], []
    for meta_path in sorted(episodes_dir.glob("*.json.meta")):
        meta = json.loads(meta_path.read_text())
        rewards = meta.get("rewards")
        if rewards is None or None in rewards:
            continue
        episode_id = int(meta["file"].split(".")[0])
        episode = json.loads((episodes_dir / meta["file"]).read_text())
        steps = episode["steps"]
        is_hold = episode_id % holdout_mod == 0
        for seat in (0, 1):  # 시그니처 좌석만이 아니라 양 좌석 모두 학습에 쓴다
            label = 1.0 if rewards[seat] > rewards[1 - seat] else 0.0
            for t in range(0, len(steps), 4):  # 상관 줄이기: 4결정마다 샘플
                st = steps[t][seat]
                obs = st.get("observation") or {}
                cur = obs.get("current")
                if not cur:
                    continue
                yi = cur.get("yourIndex")
                if yi is None:
                    continue
                # observation은 해당 좌석 관점: yourIndex 기준으로 featurize
                feats = featurize(cur, yi if st.get("status") == "ACTIVE" else seat, v2=v2)
                if feats is None:
                    continue
                (hold_x if is_hold else train_x).append(feats)
                (hold_y if is_hold else train_y).append(label)
    return train_x, train_y, hold_x, hold_y


def train_logistic(x: np.ndarray, y: np.ndarray, l2: float = 1e-3, iters: int = 300):
    n, d = x.shape
    w = np.zeros(d)
    b = 0.0
    lr = 0.5
    for it in range(iters):
        z = x @ w + b
        p = 1.0 / (1.0 + np.exp(-z))
        grad_w = x.T @ (p - y) / n + l2 * w
        grad_b = float(np.mean(p - y))
        w -= lr * grad_w
        b -= lr * grad_b
    return w, b


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", nargs="+", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--holdout-mod", type=int, default=5)
    parser.add_argument("--v2", action="store_true", help="핸드 구성 특징 4종 추가 (핸드 가시 상태만 학습)")
    args = parser.parse_args()

    tx, ty, hx, hy = [], [], [], []
    for d in args.episodes:
        a, b, c, e = collect(Path(d), args.holdout_mod, v2=args.v2)
        tx += a; ty += b; hx += c; hy += e
        print(f"{d}: train+={len(a)} hold+={len(c)}")
    x = np.asarray(tx); y = np.asarray(ty)
    hx_a = np.asarray(hx); hy_a = np.asarray(hy)
    mean = x.mean(axis=0); std = x.std(axis=0) + 1e-6
    xn = (x - mean) / std
    w, b = train_logistic(xn, y)

    def evaluate(xe, ye):
        z = ((xe - mean) / std) @ w + b
        p = 1.0 / (1.0 + np.exp(-z))
        eps = 1e-9
        logloss = float(-np.mean(ye * np.log(p + eps) + (1 - ye) * np.log(1 - p + eps)))
        order = np.argsort(p)
        ranks = np.empty_like(order, dtype=float); ranks[order] = np.arange(len(p))
        pos = ye == 1
        auc = (ranks[pos].mean() - (pos.sum() - 1) / 2) / max((~pos).sum(), 1)
        acc = float(np.mean((p > 0.5) == ye))
        return logloss, float(auc), acc

    tr = evaluate(x, y); ho = evaluate(hx_a, hy_a)
    print(f"train: logloss={tr[0]:.4f} auc={tr[1]:.4f} acc={tr[2]:.4f}  (n={len(y)})")
    print(f"hold : logloss={ho[0]:.4f} auc={ho[1]:.4f} acc={ho[2]:.4f}  (n={len(hy_a)})")
    names = FEATURE_NAMES_V2 if args.v2 else FEATURE_NAMES
    payload = {
        "features": names,
        "mean": mean.tolist(),
        "std": std.tolist(),
        "weights": w.tolist(),
        "bias": b,
    }
    Path(args.out).write_text(json.dumps(payload))
    print(f"saved {args.out}")
    for name, weight in sorted(zip(names, w), key=lambda kv: -abs(kv[1])):
        print(f"  {name:22s} {weight:+.3f}")


if __name__ == "__main__":
    main()
