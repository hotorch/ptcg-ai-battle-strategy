"""Minimal legal-action baseline for environment and submission checks."""

from pathlib import Path
from random import sample


def load_deck() -> list[int]:
    # Kaggle executes source without defining __file__, from the submission root.
    path = Path("deck.csv")
    if not path.is_file():
        path = Path("/kaggle_simulations/agent/deck.csv")
    return [int(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


DECK = load_deck()


def agent(obs: dict) -> list[int]:
    selection = obs["select"]
    if selection is None:
        return DECK
    return sample(range(len(selection["option"])), selection["maxCount"])
