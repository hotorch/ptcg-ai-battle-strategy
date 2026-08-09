"""Mega Lopunny + Mega Froslass replay-distilled policy (H-010).

상위 replay에서 집계한 (문맥, option descriptor)별 선택률로 option을 랭킹한다.
ATTACK/END는 매 MAIN 결정마다 제시되지만 턴 마지막에만 선택되므로 선택률이
낮게 학습되어 자연스럽게 terminal action이 된다. 표에 없는 상태는 generic
scorer 점수를 tie-break/fallback으로 쓴다.
"""

import json
from pathlib import Path

from cg.api import (
    AreaType,
    CardType,
    OptionType,
    Pokemon,
    SelectContext,
    all_attack,
    all_card_data,
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


# Crustle(345)이 ex 공격을 봉쇄할 때의 대체 공격축: Dunsparce 라인과 Fan Rotom.
NONEX_ATTACKERS = {66, 174, 305}


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


def agent(obs_dict: dict) -> list[int]:
    obs = to_observation_class(obs_dict)
    if obs.select is None:
        return DECK
    try:
        return choose(obs)
    except Exception:  # noqa: BLE001 - a legal minimum fallback is safer than forfeiting
        return list(range(obs.select.minCount))
