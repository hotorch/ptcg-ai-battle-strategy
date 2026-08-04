"""Run the current submission through the same self-play shape Kaggle validates."""

from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    deck = [int(line) for line in (ROOT / "deck.csv").read_text().splitlines() if line]
    assert len(deck) == 60, f"deck.csv must contain 60 cards, got {len(deck)}"

    agent_path = str(ROOT / "main.py")
    env = make("cabt", debug=True)
    env.run([agent_path, agent_path])
    final = env.steps[-1]
    statuses = [state.status for state in final]
    rewards = [state.reward for state in final]
    assert statuses == ["DONE", "DONE"], (statuses, rewards)
    assert all(reward is not None for reward in rewards), rewards
    print(f"cabt self-play OK: steps={len(env.steps) - 1}, rewards={rewards}")


if __name__ == "__main__":
    main()
