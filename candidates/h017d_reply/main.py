"""Search + learned value function on Majkel Lucario (H-014).

MAIN 결정마다 공식 search API로 현재 상태를 결정화(determinize)해 주입하고,
내 턴이 끝날 때까지의 행동 시퀀스를 best-first로 탐색해 프라이즈/보드 평가를
최대화하는 첫 수를 선택한다. 숨은 정보는 (1) 내 덱: 덱리스트-관측 차집합으로
정확 복원, (2) 상대: replay 마이닝한 메타 덱 시그니처와 관측 카드의 겹침으로
아키타입을 추정해 샘플링한다. 증류 선택률 표는 move-ordering 프라이어와
비-MAIN/실패 시 fallback 정책으로 쓴다.
"""

import heapq
import itertools
import json
import random
import time as _time
from pathlib import Path

from cg.api import (
    AreaType,
    CardType,
    OptionType,
    Pokemon,
    SelectContext,
    all_attack,
    all_card_data,
    search_begin,
    search_end,
    search_step,
    to_observation_class,
)


def _local(name: str) -> Path:
    path = Path(name)
    if not path.is_file():
        path = Path(__file__).resolve().parent / name if "__file__" in globals() else path
    if not path.is_file():
        path = Path("/kaggle_simulations/agent") / name
    return path


def load_deck() -> list[int]:
    return [int(line) for line in _local("deck.csv").read_text(encoding="utf-8").splitlines() if line]


def load_table() -> dict:
    path = _local("policy_table.json")
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


DECK = load_deck()
TABLE = load_table()
CARDS = {card.cardId: card for card in all_card_data()}
ATTACKS = {attack.attackId: attack for attack in all_attack()}


def get_card(obs, area, index, player_index):
    if area is None or index is None:
        return None
    state = obs.current
    player_index = state.yourIndex if player_index is None else player_index
    player = state.players[player_index]
    zones = {
        AreaType.HAND: player.hand,
        AreaType.DISCARD: player.discard,
        AreaType.ACTIVE: player.active,
        AreaType.BENCH: player.bench,
        AreaType.PRIZE: player.prize,
        AreaType.STADIUM: state.stadium,
        AreaType.LOOKING: state.looking,
        AreaType.DECK: obs.select.deck,
    }
    zone = zones.get(area)
    return zone[index] if zone is not None and 0 <= index < len(zone) else None


def prizes(pokemon) -> int:
    data = CARDS[pokemon.id]
    return 3 if data.megaEx else 2 if data.ex else 1


def card_score(card) -> int:
    if card is None:
        return -100_000
    data = CARDS[card.id]
    if data.cardType == CardType.POKEMON:
        return 4_000 + data.hp + 500 * data.stage2 + 250 * data.stage1
    if data.cardType in (CardType.BASIC_ENERGY, CardType.SPECIAL_ENERGY):
        return 2_500
    if data.cardType == CardType.SUPPORTER:
        return 3_500
    if data.cardType == CardType.TOOL:
        return 3_000
    return 3_200


def attack_damage(attack_id) -> int:
    attack = ATTACKS.get(attack_id)
    return attack.damage if attack else 0


def ready_damage(pokemon) -> int:
    if pokemon is None:
        return 0
    best = 0
    for attack_id in CARDS[pokemon.id].attacks:
        attack = ATTACKS.get(attack_id)
        if attack and len(pokemon.energies) >= len(attack.energies):
            best = max(best, attack.damage or 80)
    return best


def target_score(pokemon) -> int:
    if not isinstance(pokemon, Pokemon):
        return -100_000
    return prizes(pokemon) * 10_000 + len(pokemon.energies) * 800 + (pokemon.maxHp - pokemon.hp) * 20 - pokemon.hp


def active_score(obs, pokemon) -> int:
    if not isinstance(pokemon, Pokemon):
        return -100_000
    score = ready_damage(pokemon) * 100 + len(pokemon.energies) * 1_000 + pokemon.hp
    opponent = obs.current.players[1 - obs.current.yourIndex]
    opponent_active = opponent.active[0] if opponent.active else None
    if opponent_active and opponent_active.id == 345 and CARDS[pokemon.id].ex:
        score -= 100_000  # Crustle prevents attack damage from Pokemon ex.
    return score


def drains_deck(card) -> bool:
    text = " ".join(skill.text.lower() for skill in CARDS[card.id].skills)
    return "draw " in text or "search your deck" in text or "look at" in text


def main_score(obs, option) -> int:
    state = obs.current
    me = state.players[state.yourIndex]
    opponent = state.players[1 - state.yourIndex]
    active = me.active[0] if me.active else None
    opponent_active = opponent.active[0] if opponent.active else None

    if option.type == OptionType.ATTACK:
        if active and opponent_active and opponent_active.id == 345 and CARDS[active.id].ex:
            return 1_000
        return 100_000 + attack_damage(option.attackId)
    if option.type == OptionType.ABILITY:
        return 85_000
    if option.type == OptionType.EVOLVE:
        card = get_card(obs, option.area, option.index, state.yourIndex)
        return 75_000 + card_score(card)
    if option.type == OptionType.ATTACH:
        pokemon = get_card(obs, option.inPlayArea, option.inPlayIndex, state.yourIndex)
        return 65_000 + active_score(obs, pokemon) - (len(pokemon.energies) * 2_000 if pokemon else 0)
    if option.type == OptionType.PLAY:
        card = get_card(obs, AreaType.HAND, option.index, state.yourIndex)
        if card is None:
            return -1
        data = CARDS[card.id]
        if me.deckCount <= len(me.prize) + 3 and drains_deck(card):
            return -1
        if data.cardType == CardType.POKEMON:
            return 60_000 + data.hp + max((attack_damage(a) for a in data.attacks), default=0)
        return 55_000 + card_score(card)
    if option.type == OptionType.RETREAT:
        bench_ready = max((active_score(obs, p) for p in me.bench), default=-100_000)
        return 70_000 if bench_ready > active_score(obs, active) else -1
    if option.type == OptionType.END:
        return 0
    return 10_000


def generic_score(obs, option) -> int:
    select = obs.select
    state = obs.current
    context = select.context
    mine = option.playerIndex in (None, state.yourIndex)

    if context == SelectContext.MAIN:
        return main_score(obs, option)
    if option.type == OptionType.NUMBER:
        return option.number or 0
    if option.type == OptionType.YES:
        return -1 if context == SelectContext.IS_FIRST else 1
    if option.type == OptionType.NO:
        return 1 if context == SelectContext.IS_FIRST else 0
    if option.type == OptionType.ATTACK:
        return 100_000 + attack_damage(option.attackId)
    if option.type in (OptionType.ENERGY, OptionType.ENERGY_CARD, OptionType.TOOL_CARD):
        return 1
    if option.type != OptionType.CARD:
        return 1

    card = get_card(obs, option.area, option.index, option.playerIndex)
    if context in (SelectContext.SETUP_ACTIVE_POKEMON, SelectContext.SWITCH, SelectContext.TO_ACTIVE):
        return active_score(obs, card) if mine else target_score(card)
    if context in (SelectContext.SETUP_BENCH_POKEMON, SelectContext.TO_BENCH, SelectContext.TO_FIELD):
        return active_score(obs, card)
    if context in (SelectContext.DAMAGE, SelectContext.DAMAGE_COUNTER, SelectContext.DAMAGE_COUNTER_ANY):
        return target_score(card) if not mine else -target_score(card)
    if context in (SelectContext.HEAL, SelectContext.REMOVE_DAMAGE_COUNTER):
        return (card.maxHp - card.hp) * 100 + prizes(card) * 1_000 if isinstance(card, Pokemon) else -1
    if context == SelectContext.ATTACH_FROM:
        return active_score(obs, card) - len(card.energies) * 2_000 if isinstance(card, Pokemon) else -1
    if context in (SelectContext.DISCARD, SelectContext.TO_DECK, SelectContext.TO_DECK_BOTTOM):
        return -card_score(card)
    if context in (SelectContext.TO_HAND, SelectContext.ATTACH_TO, SelectContext.LOOK):
        return card_score(card)
    return active_score(obs, card) if isinstance(card, Pokemon) else card_score(card)


def type_name(kind) -> str:
    try:
        return OptionType(kind).name
    except ValueError:
        return str(int(kind))


def describe(obs, option) -> str:
    """replay 집계와 런타임 랭킹이 공유하는 option descriptor."""
    state = obs.current
    kind = option.type
    if kind == OptionType.NUMBER:
        return f"NUM:{option.number}"
    if kind == OptionType.YES:
        return "YES"
    if kind == OptionType.NO:
        return "NO"
    if kind == OptionType.PLAY:
        card = get_card(obs, AreaType.HAND, option.index, state.yourIndex)
        return f"PLAY:{card.id if card else '?'}"
    if kind == OptionType.ATTACH:
        pokemon = get_card(obs, option.inPlayArea, option.inPlayIndex, state.yourIndex)
        return f"ATTACH:{pokemon.id if pokemon else '?'}"
    if kind == OptionType.EVOLVE:
        card = get_card(obs, option.area, option.index, state.yourIndex)
        return f"EVOLVE:{card.id if card else '?'}"
    if kind == OptionType.ABILITY:
        card = get_card(obs, option.area, option.index, state.yourIndex)
        return f"ABILITY:{card.id if card else '?'}"
    if kind == OptionType.ATTACK:
        return f"ATTACK:{option.attackId}"
    if kind == OptionType.RETREAT:
        return "RETREAT"
    if kind == OptionType.END:
        return "END"
    if kind == OptionType.CARD:
        mine = option.playerIndex in (None, state.yourIndex)
        card = get_card(obs, option.area, option.index, option.playerIndex)
        return f"CARD:{card.id if card else '?'}:{'m' if mine else 'o'}"
    if kind == OptionType.DISCARD:
        card = get_card(obs, option.area, option.index, state.yourIndex)
        return f"DISC:{card.id if card else '?'}"
    if kind == OptionType.SKILL:
        return f"SKILL:{option.cardId}"
    if kind == OptionType.SPECIAL_CONDITION:
        return f"SC:{option.specialConditionType}"
    return type_name(kind)


def select_key(select) -> str:
    return f"{int(select.type)}|{int(select.context)}"


def sub_key(obs) -> str:
    """상태 특징을 붙인 세분화 키. turn 버킷 + (MAIN이면) 에너지/서포터 사용 여부."""
    state = obs.current
    turn = state.turn or 0
    bucket = 0 if turn <= 2 else (1 if turn <= 6 else 2)
    base = select_key(obs.select)
    if int(obs.select.context) == int(SelectContext.MAIN):
        me = state.players[state.yourIndex]
        active = me.active[0] if me.active else None
        can_attack = int(ready_damage(active) > 0)
        return (
            f"{base}#{bucket}{int(bool(state.energyAttached))}"
            f"{int(bool(state.supporterPlayed))}{can_attack}"
        )
    return f"{base}#{bucket}"


def pick_rate(entries: list, desc: str, option_type) -> float:
    """P(선택 | 제시). 세분화 키 → 기본 키 → option type 평균 순서로 fallback."""
    prior = 0.15
    for entry in reversed(entries):  # 넓은 키의 type 평균부터 좁은 키로 덮어쓴다.
        if not entry:
            continue
        agg = entry.get(f"~{type_name(option_type)}")
        if agg and agg[1] >= 3:
            prior = agg[0] / agg[1]
    for entry in entries:  # 좁은 키의 descriptor 통계를 우선 사용한다.
        if not entry:
            continue
        stat = entry.get(desc)
        if stat and stat[1] >= 2:
            return (stat[0] + prior) / (stat[1] + 1)
    return prior


def is_ex(card) -> bool:
    if not isinstance(card, Pokemon):
        return False
    data = CARDS[card.id]
    return bool(data.ex or data.megaEx)


# Crustle(345)이 ex 공격을 봉쇄할 때의 대체 공격축. Riolu(677)는 ex 진화 전용이라 제외.
NONEX_ATTACKERS = {673, 674, 675, 676}


def adjust(obs, option, base: float) -> float:
    """replay에 없는 상황의 하드 오버라이드: Crustle 봉쇄, mill 방어, lethal."""
    state = obs.current
    me = state.players[state.yourIndex]
    opponent = state.players[1 - state.yourIndex]
    active = me.active[0] if me.active else None
    opponent_active = opponent.active[0] if opponent.active else None
    crustle_block = opponent_active is not None and opponent_active.id == 345
    low_deck = me.deckCount <= max(len(me.prize) + 3, 12)
    context = obs.select.context

    if context == SelectContext.MAIN:
        options = obs.select.option
        attach_available = not state.energyAttached and any(
            o.type == OptionType.ATTACH for o in options
        )
        if option.type == OptionType.ATTACK:
            blocked = crustle_block and is_ex(active)
            if blocked:
                return base * 0.01
            damage = attack_damage(option.attackId)
            if opponent_active is not None and damage >= opponent_active.hp:
                return max(base, 0.97)  # lethal은 항상 실행
            if attach_available:
                return base * 0.3  # 부착부터 하고 공격한다
            if crustle_block and damage > 0:
                return max(base, 0.8)  # 비-ex 공격으로 봉쇄를 뚫는다
            return base
        if option.type == OptionType.END:
            if attach_available:
                return base * 0.05  # 에너지 부착을 남기고 턴을 끝내지 않는다
            usable_attack = any(
                o.type == OptionType.ATTACK
                and attack_damage(o.attackId) > 0
                and not (crustle_block and is_ex(active))
                for o in options
            )
            if usable_attack:
                return base * 0.1  # 공격 가능하면 END는 마지막
            return base
        if (
            option.type == OptionType.RETREAT
            and crustle_block
            and is_ex(active)
            and any(not is_ex(p) and ready_damage(p) > 0 for p in me.bench)
        ):
            return max(base, 0.85)
        if option.type == OptionType.ATTACH and crustle_block:
            target = get_card(obs, option.inPlayArea, option.inPlayIndex, state.yourIndex)
            if target is not None:
                if target.id in NONEX_ATTACKERS:
                    return max(base, 0.7)
                return base * 0.1
        if option.type == OptionType.PLAY:
            mill_opponent = any(
                p.id in (58, 345)  # Great Tusk mill / Crustle wall
                for p in list(opponent.active) + list(opponent.bench)
            )
            if low_deck or (mill_opponent and me.deckCount <= 25):
                card = get_card(obs, AreaType.HAND, option.index, state.yourIndex)
                if (
                    card is not None
                    and CARDS[card.id].cardType != CardType.POKEMON
                    and drains_deck(card)
                ):
                    return base * (0.01 if low_deck else 0.3)
    elif context in (SelectContext.SWITCH, SelectContext.TO_ACTIVE):
        if crustle_block and option.type == OptionType.CARD:
            card = get_card(obs, option.area, option.index, option.playerIndex)
            if option.playerIndex in (None, state.yourIndex) and isinstance(card, Pokemon):
                if card.id in NONEX_ATTACKERS:
                    return max(base, 0.7)
                if is_ex(card):
                    return base * 0.2
    return base


def choose(obs) -> list[int]:
    select = obs.select
    options = select.option
    entries = [TABLE.get(sub_key(obs)), TABLE.get(select_key(select))]

    def score(i: int) -> float:
        base = pick_rate(entries, describe(obs, options[i]), options[i].type)
        base = adjust(obs, options[i], base)
        tie = max(-100_000, min(100_000, generic_score(obs, options[i]))) / 100_000
        return base * 1_000_000 + tie * 100

    ranked = sorted(range(len(options)), key=score, reverse=True)

    target = select.minCount
    for entry in entries:
        if entry and entry.get("_pick") and entry["_pick"][1] >= 3:
            target = round(entry["_pick"][0] / entry["_pick"][1])
            break
    target = max(select.minCount, min(select.maxCount, target))

    return ranked[:target]


# ---------------------------------------------------------------------------
# H-011 search layer
# ---------------------------------------------------------------------------

def _load_meta_decks() -> list[dict]:
    path = _local("meta_decks.json")
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return []


META_DECKS = _load_meta_decks()


def _load_value():
    path = _local("value_weights.json")
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


VALUE = _load_value()


def _load_opp_table():
    path = _local("opp_reply_table.json")
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


OPP_TABLE = _load_opp_table()
SEARCH_BUDGET_NODES = 2400
SEARCH_BUDGET_SECONDS = 5.0
DETERMINIZATION_SAMPLES = 3  # 숨은 정보 샘플 수. 투표로 단일 샘플 노이즈를 상쇄한다.
# 실제 제약은 remainingOverageTime 뱅크 600초다. 잔량 기반으로 결정당 예산을 줄이고
# 150초 미만이면 탐색을 끄고 증류 정책으로 버틴다.
GAME_SEARCH_SECONDS_CAP = 450.0
OVERAGE_FLOOR = 150.0
_search_spent = {"seconds": 0.0}
_DIAG = {"search_ok": 0, "search_none": 0, "search_fail": 0, "nodes": 0}
_DIAG_LOG = Path("/tmp/h011_diag.log")


def _card_ids_of(card) -> list[int]:
    """보드 위 Pokemon 하나가 점유한 실제 카드 id 목록(본체+에너지+도구+진화 전 단계)."""
    ids = [card.id]
    for c in getattr(card, "energyCards", None) or []:
        ids.append(c.id)
    for c in getattr(card, "tools", None) or []:
        ids.append(c.id)
    for c in getattr(card, "preEvolution", None) or []:
        ids.append(c.id)
    return ids


def _remove_seen(pool: list[int], seen: list[int]) -> list[int]:
    pool = list(pool)
    for cid in seen:
        if cid in pool:
            pool.remove(cid)
    return pool


def _pad_to(pool: list[int], n: int, filler: int) -> list[int]:
    if len(pool) < n:
        pool = pool + [filler] * (n - len(pool))
    return pool[:n]


def _seen_ids(player, include_hand: bool) -> list[int]:
    seen = []
    if include_hand and player.hand:
        seen += [c.id for c in player.hand if c is not None]
    seen += [c.id for c in player.discard if c is not None]
    for p in list(player.active) + list(player.bench):
        if p is not None:
            seen += _card_ids_of(p)
    seen += [c.id for c in player.prize if c is not None]
    return seen


def _match_meta_deck(opp_seen: list[int]) -> list[int]:
    """관측된 상대 카드와 겹침이 최대인 메타 덱을 고른다."""
    if not META_DECKS:
        return list(DECK)
    import collections as _c

    seen_count = _c.Counter(opp_seen)
    best, best_score = None, -1.0
    for entry in META_DECKS:
        sig = _c.Counter(entry["deck"])
        overlap = sum(min(n, sig.get(cid, 0)) for cid, n in seen_count.items())
        score = overlap * 1000 + entry["games"] / 100.0
        if score > best_score:
            best, best_score = entry["deck"], score
    return list(best)


def _basic_pokemon_of(deck: list[int]) -> int:
    import collections as _c

    counts = _c.Counter(deck)
    best, best_n = None, -1
    for cid, n in counts.items():
        data = CARDS.get(cid)
        if data is not None and data.cardType == CardType.POKEMON and not data.stage1 and not data.stage2:
            if n > best_n:
                best, best_n = cid, n
    return best if best is not None else deck[0]


def _determinize(obs):
    state = obs.current
    mi = state.yourIndex
    me = state.players[mi]
    opp = state.players[1 - mi]

    my_pool = _remove_seen(DECK, _seen_ids(me, include_hand=True))
    random.shuffle(my_pool)
    filler = DECK[0]
    n_prize = sum(1 for c in me.prize if c is None)
    my_prize = _pad_to(my_pool[:n_prize], len(me.prize), filler)
    rest = my_pool[n_prize:]
    my_deck = [] if obs.select.deck is not None else _pad_to(rest, me.deckCount, filler)

    opp_seen = _seen_ids(opp, include_hand=False)
    opp_sig = _match_meta_deck(opp_seen)
    opp_pool = _remove_seen(opp_sig, opp_seen)
    random.shuffle(opp_pool)
    opp_filler = opp_sig[0]
    opp_hand = _pad_to(opp_pool[: opp.handCount], opp.handCount, opp_filler)
    rest = opp_pool[opp.handCount:]
    opp_prize = _pad_to(rest[: len(opp.prize)], len(opp.prize), opp_filler)
    opp_deck = _pad_to(rest[len(opp.prize):], opp.deckCount, opp_filler)

    opp_active = []
    if opp.active and opp.active[0] is None:
        opp_active = [_basic_pokemon_of(opp_sig)]
    return my_deck, my_prize, opp_deck, opp_prize, opp_hand, opp_active


def _attack_progress(pokemon) -> float:
    """최고 공격 대비 에너지 진행률 부분 점수. 지평선 밖의 셋업 가치를 평가에 반영한다."""
    data = CARDS[pokemon.id]
    best = 0.0
    for attack_id in data.attacks:
        attack = ATTACKS.get(attack_id)
        if attack is None:
            continue
        need = max(len(attack.energies), 1)
        have = min(len(pokemon.energies), need)
        best = max(best, (attack.damage or 80) * (have / need) ** 2)
    return best


def _stage_value(pokemon) -> float:
    data = CARDS[pokemon.id]
    if data.megaEx:
        return 9_000.0
    if data.stage2:
        return 4_000.0
    if data.stage1:
        return 1_500.0
    return 0.0


def _stage_counts(board):
    mega = stage1plus = 0
    for p in board:
        data = CARDS.get(p.id)
        if data is None:
            continue
        if data.megaEx:
            mega += 1
        if data.stage1 or data.stage2:
            stage1plus += 1
    return mega, stage1plus


def _vf_features(state, mi: int) -> list[float]:
    me = state.players[mi]
    opp = state.players[1 - mi]
    mb = [p for p in list(me.active) + list(me.bench) if p is not None]
    ob = [p for p in list(opp.active) + list(opp.bench) if p is not None]
    my_mega, my_s1 = _stage_counts(mb)
    opp_mega, opp_s1 = _stage_counts(ob)
    my_active = me.active[0] if me.active else None
    opp_active = opp.active[0] if opp.active else None
    return [
        float(len(opp.prize) - len(me.prize)),
        float(len(me.prize)),
        sum(p.maxHp - p.hp for p in ob) / 100.0,
        sum(p.maxHp - p.hp for p in mb) / 100.0,
        float(sum(len(p.energies) for p in mb)),
        float(sum(len(p.energies) for p in ob)),
        float(my_mega),
        float(opp_mega),
        float(my_s1),
        float(opp_s1),
        float(len(mb)),
        float(len(ob)),
        float(me.handCount),
        float(opp.handCount),
        float(max(0, 7 - me.deckCount)),
        float(max(0, 7 - opp.deckCount)),
        _attack_progress(my_active) / 100.0 * 1.0 if my_active else 0.0,
        _attack_progress(opp_active) / 100.0 * 1.0 if opp_active else 0.0,
        float(bool(me.paralyzed) or bool(me.asleep)),
        min(state.turn or 0, 30) / 30.0,
    ]


def _eval_state(state, mi: int) -> float:
    if state.result == mi:
        return 1e9
    if state.result == 1 - mi:
        return -1e9
    if VALUE is not None:
        feats = _vf_features(state, mi)
        z = VALUE["bias"]
        for f, m, sd, w in zip(feats, VALUE["mean"], VALUE["std"], VALUE["weights"]):
            z += w * (f - m) / sd
        return z * 100_000.0
    me = state.players[mi]
    opp = state.players[1 - mi]
    score = (len(opp.prize) - len(me.prize)) * 100_000.0
    opp_board = [p for p in list(opp.active) + list(opp.bench) if p is not None]
    score += sum(p.maxHp - p.hp for p in opp_board) * 30
    mine = [p for p in list(me.active) + list(me.bench) if p is not None]
    score += sum(len(p.energies) for p in mine) * 500
    score += sum(_stage_value(p) for p in mine)
    score += max((_attack_progress(p) for p in mine), default=0.0) * 40
    if me.active and me.active[0] is not None:
        score += _attack_progress(me.active[0]) * 60
    if me.paralyzed or me.asleep:
        score -= 2_000
    score += len(mine) * 800
    score += me.handCount * 120
    if me.deckCount <= 6:
        score -= (7 - me.deckCount) * 8_000
    if opp.deckCount <= 6:
        score += (7 - opp.deckCount) * 8_000
    return score


def _candidate_selects(obs, cap: int) -> list[list[int]]:
    """프라이어 순으로 정렬한 후보 select 목록."""
    select = obs.select
    options = select.option
    entries = [TABLE.get(sub_key(obs)), TABLE.get(select_key(select))]

    def prior(i: int) -> float:
        base = pick_rate(entries, describe(obs, options[i]), options[i].type)
        return adjust(obs, options[i], base)

    ranked = sorted(range(len(options)), key=prior, reverse=True)
    if select.maxCount <= 1:
        return [[i] for i in ranked[:cap]]
    target = max(select.minCount, min(select.maxCount, select.minCount or 1))
    combo = ranked[:target]
    alt = ranked[1: target + 1] if len(ranked) > target else None
    picks = [combo]
    if alt and alt != combo:
        picks.append(alt)
    return picks


def _greedy_reply(ss, mi: int, step_limit: int = 30, deadline: float | None = None):
    """상대 턴을 generic scorer로 그리디 롤아웃해 응수 반영 상태를 돌려준다."""
    for _ in range(step_limit):
        if deadline is not None and _time.perf_counter() >= deadline:
            return ss
        o = ss.observation
        st = o.current
        if st is None or st.result != -1 or st.yourIndex == mi:
            return ss
        if o.select is None or not o.select.option:
            return ss
        options = o.select.option
        entries = [OPP_TABLE.get(select_key(o.select))]

        def opp_score(i):
            rate = pick_rate(entries, describe(o, options[i]), options[i].type)
            tie = max(-100_000, min(100_000, generic_score(o, options[i]))) / 100_000
            return rate * 1_000 + tie

        ranked = sorted(range(len(options)), key=opp_score, reverse=True)
        take = max(o.select.minCount, min(o.select.maxCount, o.select.minCount or 1))
        try:
            ss = search_step(ss.searchId, ranked[:take] if take else [ranked[0]])
        except Exception:  # noqa: BLE001
            return ss
    return ss


def _greedy_self(ss, mi: int, step_limit: int = 40, deadline: float | None = None):
    """응수 이후의 내 다음 턴을 그리디 롤아웃한다. fetch해 온 진화체·자원의
    다음 턴 가치를 리프 평가에 드러내기 위한 지평선 연장이다."""
    for _ in range(step_limit):
        if deadline is not None and _time.perf_counter() >= deadline:
            return ss
        o = ss.observation
        st = o.current
        if st is None or st.result != -1 or st.yourIndex != mi:
            return ss
        if o.select is None or not o.select.option:
            return ss
        options = o.select.option
        ranked = sorted(range(len(options)), key=lambda i: generic_score(o, options[i]), reverse=True)
        take = max(o.select.minCount, min(o.select.maxCount, o.select.minCount or 1))
        try:
            ss = search_step(ss.searchId, ranked[:take] if take else [ranked[0]])
        except Exception:  # noqa: BLE001
            return ss
    return ss


PRIOR_BLEND = 0.0  # 증류 선택률을 탐색 가치에 더하는 가중치(평가 단위, 프라이즈 1개=100k).


def _root_prior(obs) -> dict:
    """루트 후보 행동별 증류 프라이어. 어빌리티류 지연 가치를 탐색 평가에 보완한다."""
    select = obs.select
    entries = [TABLE.get(sub_key(obs)), TABLE.get(select_key(select))]
    priors = {}
    for i, option in enumerate(select.option):
        base = pick_rate(entries, describe(obs, option), option.type)
        priors[(i,)] = adjust(obs, option, base)
    return priors


def _search_choose(obs, budget_seconds: float = SEARCH_BUDGET_SECONDS) -> list[int] | None:
    """다중 결정화 투표: K개 숨은정보 샘플 각각을 탐색해 행동 가치를 평균한다."""
    start = _time.perf_counter()
    priors = _root_prior(obs)
    votes: dict = {}
    for _ in range(DETERMINIZATION_SAMPLES):
        remaining = start + budget_seconds - _time.perf_counter()
        if remaining <= 0.2:
            break
        values = _search_once(obs, min(remaining, budget_seconds / DETERMINIZATION_SAMPLES + 0.4))
        for key, value in values.items():
            entry = votes.setdefault(key, [0, 0.0])
            entry[0] += 1
            entry[1] += value
    if not votes:
        return None
    # 행동별 평균 탐색 가치 + 증류 프라이어 블렌드. 동률이면 다수 샘플에서 탐색된 행동.
    def score(item):
        key, (count, total) = item
        return (total / count + PRIOR_BLEND * priors.get(key, 0.0), count)

    best_key = max(votes.items(), key=score)[0]
    return list(best_key)


def _search_once(obs, budget_seconds: float) -> tuple[list[int] | None, float]:
    start = _time.perf_counter()
    mi = obs.current.yourIndex
    det = _determinize(obs)
    root = search_begin(obs, *det)
    counter = itertools.count()
    values: dict = {}
    budget = SEARCH_BUDGET_NODES // DETERMINIZATION_SAMPLES
    deadline = start + budget_seconds
    heap = [(0.0, next(counter), root, None)]
    try:
        while heap and budget > 0 and _time.perf_counter() < deadline:
            _, _, ss, first = heapq.heappop(heap)
            o = ss.observation
            st = o.current
            if st is None:
                continue
            if st.result != -1 or st.yourIndex != mi or o.select is None or not o.select.option:
                value = _eval_state(st, mi)
                if st.result == -1 and st.yourIndex != mi:
                    # 3지평 평균: 내턴 종료 / 상대 응수 후 / 내 다음 턴 롤아웃 후.
                    # 마지막 항이 fetch·전개의 다음 턴 가치를 드러낸다.
                    replied = _greedy_reply(ss, mi, deadline=deadline + 0.5)
                    replied_state = replied.observation.current
                    if replied_state is not None:
                        v_reply = _eval_state(replied_state, mi)
                        nxt = _greedy_self(replied, mi, deadline=deadline + 0.7)
                        nxt_state = nxt.observation.current
                        v_next = _eval_state(nxt_state, mi) if nxt_state is not None else v_reply
                        value = (value + v_reply + v_next) / 3.0
                if first is not None:
                    key = tuple(sorted(first))
                    values[key] = max(values.get(key, float("-inf")), value)
                continue
            if o.select.context == SelectContext.MAIN:
                cap = 12
            elif first is None:
                cap = 8  # 하위 선택이 루트일 때는 후보를 넓게 본다
            else:
                cap = 5
            for sel in _candidate_selects(o, cap):
                if budget <= 0 or _time.perf_counter() >= deadline:
                    break
                budget -= 1
                _DIAG["nodes"] += 1
                try:
                    child = search_step(ss.searchId, sel)
                except Exception:  # noqa: BLE001 - 불법 시퀀스는 가지치기
                    continue
                child_first = first if first is not None else sel
                child_state = child.observation.current
                value = _eval_state(child_state, mi) if child_state else float("-inf")
                if child_first is not None and value > float("-inf"):
                    key = tuple(sorted(child_first))
                    values[key] = max(values.get(key, float("-inf")), value)
                heapq.heappush(heap, (-value, next(counter), child, child_first))
    finally:
        search_end()
        _search_spent["seconds"] += _time.perf_counter() - start
    return values


# Mega Lucario 라인(격투 약점 최악 매치업)에서는 탐색보다 증류 모방이 강했다
# (full 500경기: 증류 23% vs 탐색 5%). 감지 시 증류 정책으로 전환한다.
FIGHTING_LINE = set()  # 학습 가치 탐색은 미러에서도 증류보다 강했다(57.5%) — fallback 제거


def _fighting_matchup(obs) -> bool:
    state = obs.current
    opp = state.players[1 - state.yourIndex]
    for card in list(opp.discard) + list(opp.active) + list(opp.bench):
        if card is not None and card.id in FIGHTING_LINE:
            return True
    return False


def agent(obs_dict: dict) -> list[int]:
    obs = to_observation_class(obs_dict)
    if obs.select is None:
        return DECK
    try:
        overage = float(obs_dict.get("remainingOverageTime") or 600.0)
        # 잔여 시간 뱅크에 맞춰 결정당 예산을 줄인다.
        if overage > 400:
            budget = SEARCH_BUDGET_SECONDS
        elif overage > 250:
            budget = 3.0
        else:
            budget = 1.5
        if (
            obs.search_begin_input is not None
            and obs.select.option is not None
            and len(obs.select.option) > 1
            and overage > OVERAGE_FLOOR
            and _search_spent["seconds"] < GAME_SEARCH_SECONDS_CAP
            and not _fighting_matchup(obs)  # Lucario 미러는 모방이 강하다 (full 40% vs 증류 기대 50%)
        ):
            try:
                picked = _search_choose(obs, budget)
                if picked is None:
                    _DIAG["search_none"] += 1
                else:
                    _DIAG["search_ok"] += 1
                try:
                    _DIAG_LOG.write_text(str(_DIAG))
                except Exception:
                    pass
                if picked is not None:
                    n = len(obs.select.option)
                    if (
                        obs.select.minCount <= len(picked) <= obs.select.maxCount
                        and all(0 <= i < n for i in picked)
                    ):
                        return picked
            except Exception as _exc:  # noqa: BLE001 - 탐색 실패는 증류 정책으로 흡수
                _DIAG["search_fail"] += 1
                try:
                    import traceback as _tb
                    _DIAG_LOG.write_text(str(_DIAG) + "\n" + _tb.format_exc())
                except Exception:
                    pass
        return choose(obs)
    except Exception:  # noqa: BLE001 - a legal minimum fallback is safer than forfeiting
        return list(range(obs.select.minCount))
