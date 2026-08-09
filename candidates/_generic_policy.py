"""Small deck-agnostic legal-action scorer built from the official CABT SDK."""

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


def load_deck() -> list[int]:
    path = Path("deck.csv")
    if not path.is_file():
        path = Path("/kaggle_simulations/agent/deck.csv")
    return [int(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


DECK = load_deck()
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


def option_score(obs, option) -> int:
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


def choose(obs) -> list[int]:
    select = obs.select
    ranked = sorted(range(len(select.option)), key=lambda i: option_score(obs, select.option[i]), reverse=True)
    chosen = []
    for index in ranked:
        if len(chosen) >= select.maxCount:
            break
        if len(chosen) < select.minCount or option_score(obs, select.option[index]) >= 0:
            chosen.append(index)
    return chosen


def agent(obs_dict: dict) -> list[int]:
    obs = to_observation_class(obs_dict)
    if obs.select is None:
        return DECK
    try:
        return choose(obs)
    except Exception:  # noqa: BLE001 - a legal minimum fallback is safer than forfeiting
        return list(range(obs.select.minCount))
