# PTCG AI Battle Research

English | [한국어](README.ko.md)

Reproducible research workspace for the [Kaggle Pokémon Trading Card Game AI Battle Challenge](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle). The project studies how a rule-based agent behaves on a noisy ladder, then turns specific decision failures into small, testable repairs.

## Competition overview

The competition asks participants to build an AI agent that plays the Pokémon Trading Card Game in Kaggle's CABT simulation environment. Agents are evaluated through repeated games and ranked by a rating-based leaderboard. Results depend on policy quality, deck construction, opponent pool, matchmaking, game count, and the stochastic engine, so one submission rating is not a complete estimate of strength.

This repository covers two connected deliverables:

- **Simulation research:** candidate agents, 60-card decks, both-seat evaluation, and submission packaging for the [PTCG AI Battle Challenge Simulation](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle).
- **Strategy writeup:** the documented analysis submitted to the [PTCG AI Battle Challenge Strategy](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy), with code shared in the [Kaggle discussion post](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/discussion/741120).

The final writeup reports two matched final-build submissions at **742.8** and **700.2**, with final placement **1,611 / 6,807 (top 24%)** at the recorded ladder cutoff. Five changes were tested; two were retained. The strongest evidence is behavioral: on 21,975 recorded decisions from 168 episodes, the retained repair produced 65 intended action changes and zero observed collateral changes. The local match tests did not establish a general win-rate improvement, so the writeup keeps that limitation explicit.

## Repository map

| Path | Purpose |
|---|---|
| `candidates/h036_tempo_boss/` | Final H036 agent and deck used in the strategy writeup |
| `main.py`, `deck.csv` | Current root research baseline; use the candidate path above for the final H036 pair |
| `scripts/evaluate.py` | Non-deterministic CABT evaluation from both seats |
| `scripts/package_submission.py` | Validate and build a Kaggle submission archive |
| `scripts/kaggle_ops.py` | Context synchronization, status checks, and guarded submission operations |
| `scripts/curate_context.py` | Select and collect relevant Kaggle discussions and notebooks |
| `research_loop/results.tsv` | Experiment result ledger |
| `docs/ptcg/` | Competition facts, protocol, hypotheses, and submission notes |

## Quick start

```bash
uv sync
uv run python scripts/kaggle_ops.py fetch-sdk
uv run python scripts/smoke_test.py
uv run pytest -q
```

Run a small two-seat evaluation with the documented candidate interface:

```bash
uv run python scripts/evaluate.py \
  --candidate candidates/h036_tempo_boss \
  --bundle smoke \
  --workers 2
```

Validate and package a candidate before submitting:

```bash
uv run python scripts/package_submission.py \
  --source candidates/h036_tempo_boss \
  --output submission.tar.gz
```

The local CABT engine is stochastic. Treat repeated runs, seat balance, sample size, and uncertainty as part of the result; do not infer causality from one game or one rating.

## Data and omitted artifacts

Competition Data is for competition use only and is not redistributed here. Replay-derived participant deck snapshots, raw traces, and named-card metadata are omitted from the repository and its history. The final agent runs without them. When permitted, the analysis scripts can be regenerated with a participant's own local competition data; see `docs/ptcg/` for the corresponding commands.

Pokémon card names, images, and other Pokémon Elements remain the property of their respective rights holders. This repository's original code and documentation are released under the [MIT License](LICENSE). The credited policy base is [Rozen's V10 notebook](https://www.kaggle.com/code/romanrozen/strong-start-baseline-agent-v10-lb-950).

## Links

- [Submitted strategy writeup](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/writeups/new-writeup-1786172403257)
- [Solution and evaluation code discussion](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/discussion/741120)
- [Competition](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle)
