# Pass A

## 1. Approach articulation and rationale

**Score: 4/5**

> The metagame is a **dynamical system** we measured well enough to call its endpoint in writing before it arrived.

A judge would want the timestamped prediction stated verbatim and a clearer causal link from the forecast to the final policy decisions.

## 2. Originality and technical soundness

**Score: 4/5**

> The originality we claim is in the method, not the policy code.

A judge would want the specific novel methodological contributions distinguished explicitly from practices already described in the cited discussions.

## 3. Repeated-match consistency

**Score: 4/5**

> **Consistency at scale.** Two locked instances, same code, independent match streams: 53.5% and 52.9% over 1,000 games each.

A judge would want confidence intervals, draw handling, dates, opponent-pool comparability, and evidence that the two streams represent stable conditions.

## 4. Robustness against situational advantages

**Score: 3/5**

> The cascade branches on board state only — no opening-specific cases, seat-specific tables, or hard-coded turn numbers.

A judge would want results stratified by seat, opening quality, archetype, and relevant initial-state categories because absence of special-case code does not establish empirical robustness.

## 5. Competition-track performance

**Score: 3/5**

> Final placement **1,649 / 6,807**.

A judge would want percentile, relevant track-only rank, baseline comparisons, and an explanation of how the final ratings relate to the reported 53% win rates.

## 6. Deck concept and strategic alignment

**Score: 4/5**

> Every remaining slot serves that axis: draw supporters, recovery, energy denial to buy setup turns, and 3 copies of the gust supporter to convert a big hand into a prize.

A judge would want the actual card names, complete counts, and a compact explanation of how each package advances the hand-size plan.

## 7. Key-card selection and utilization

**Score: 3/5**

> Rare Candy sits at 16,000 because skipping the Stage 1 is the deck's tempo.

A judge would want the priority scale explained and card-level ablations or activation statistics showing that the chosen counts and priorities improve outcomes.

## 8. Clarity, organization, and readability

**Score: 4/5**

> Two shipped: **S1**, a light lethal graft, and **S5**, the tempo gust (mirror 50.0%, n=60; meta 85.0%, n=40; counter-archetype proxy 100%, n=40).

A judge would want S1 and each evaluation population defined in plain language before presenting their results.

## 9. Figures, tables, and examples

**Score: 2/5**

> *Figure A — the priority cascade with the five surgery sites: two shipped (S1, S5), three won locally and did not translate (S2–S4).*

A judge would want the referenced figure actually included, with readable labels, samples, uncertainty, and enough annotation to verify the claim.

# Pass B

## 1. Approach articulation and rationale

**Score: 4/5**

> Every change is a **gated experiment** (a 21,975-decision replay regression, zero collateral changes).

A judge would want the full gate sequence, advancement thresholds, and distinction between behavioral regression testing and evidence of match-level improvement.

## 2. Originality and technical soundness

**Score: 3/5**

> Our contribution is what we did with it: we **decomposed the variance into mechanisms**, ran it as a **rejection rule** on our own changes, and **closed it with convergence**.

A judge would want formal methods and stronger evidence that the three observational patterns constitute a variance decomposition rather than plausible anecdotes.

## 3. Repeated-match consistency

**Score: 4/5**

> Their 1,000-game means differ by **6.6**, against a same-build spread of 134 at ~50 games.

A judge would want like-for-like uncertainty estimates because a range from short submissions is not directly comparable with the difference between long-run means.

## 4. Robustness against situational advantages

**Score: 3/5**

> **Worst cases published.** Both losing matchups are stated with sample sizes and the mechanism that binds them: higher rating means more exposure to the strongest archetype, so the ceiling tightens as you climb.

A judge would want the complete matchup matrix, uncertainty intervals, and evidence for the claimed rating-dependent scheduling mechanism.

## 5. Competition-track performance

**Score: 3/5**

> Re-weighting our measured matchups by the *forecast* field, expected win rate fell from 45–48% to **40.3%**.

A judge would want this forecast reconciled with the final 52.9–53.5% results and tied to a clearly defined evaluation population.

## 6. Deck concept and strategic alignment

**Score: 4/5**

> We kept it for a quantitative reason: the policy is tuned to this deck's card IDs, so a swap would have voided every gate result we owned with no budget left to re-earn them.

A judge would want evidence that retaining the deck was the strongest strategic choice, rather than merely the least disruptive engineering choice.

## 7. Key-card selection and utilization

**Score: 3/5**

> The gust supporter is the *only* card allowed to outrank drawing, and only when arithmetic proves it wins the exchange this turn.

A judge would want activation frequency, knockout conversion rate, failure cases, and an ablation isolating the benefit of this priority change.

## 8. Clarity, organization, and readability

**Score: 4/5**

> Discussion 737125 (8/23) reports a byte-identical tarball submitted seven times: mean 765, sd 51, range 168.

A judge would want “8/23” and the discussion’s relevance explained without requiring forum knowledge.

## 9. Figures, tables, and examples

**Score: 2/5**

> *Figure B — one point per submission, grouped by build. Figure E — left: the placement spike and decay; right: the final pair's 1,000-game trajectories.*

A judge would want the missing plots embedded and the unusual A/B/E/C/D figure order corrected.

# Claims a skeptical judge may doubt or find unsupported

- “57 submissions across 23 builds” is not accompanied by a ledger summary or definition of a build.
- The 21,975 replay decisions are not characterized by source, opponent distribution, dates, or coverage.
- “Zero collateral changes” establishes output equivalence on recorded states, not safety in downstream states or improved match results.
- The claimed advance prediction is neither quoted nor timestamped in the writeup.
- The precise differences from Rozen V10 are incomplete, especially because S1 is never explained.
- “Five audited surgeries” is stronger than the evidence shown for all five.
- The final ratings, snapshot win rates, and “1,000-game means” use different statistics whose relationship is unclear.
- “After 1,000 post-deadline games” may reflect a different field from the scored competition period.
- Rank 1,649/6,807 is not contextualized against the Strategy track, baselines, or percentile.
- Replay-export mining is vulnerable to the acknowledged top-pool sampling bias.
- Deck-signature extraction and archetype-classification accuracy are not reported.
- The deck and its important cards remain unnamed, preventing direct verification.
- Priority values such as 16,000, 6,000, 4,249, and 2,262 lack scale derivation or calibration evidence.
- The “crowd-pick paradox” is observational; popularity is not shown to cause poor performance.
- Discussion 737107 is described as an independent audit, but its methodology is not summarized.
- The participant’s reported 200-point gain cannot safely be attributed to “deck arithmetic alone” without controls.
- S5’s local samples are small, especially the 100% result at \(n=40\), and no intervals are given.
- The lethal formula may omit modifiers, prevention effects, prizes, retreat costs, or other game-state constraints; “reachable and killable” is not formalized.
- Replay decision diffs do not test counterfactual trajectories caused by earlier changed actions.
- “No seed replication” does not by itself explain every limitation on matched or blocked experimental designs.
- Same-build rating spread mixes randomness, unequal game counts, scheduling, and metagame drift.
- Rejecting any single 60-point change as noise is not formally supported by the observed range alone.
- The three claimed variance “mechanisms” are illustrated with isolated observations rather than estimated contributions.
- One 4–1 opening does not establish sticky placement as a general mechanism.
- One 32-games-versus-1 window does not establish general scheduling priority.
- The drift-control comparison has only four prior observations and cannot strongly reject rating inflation.
- Similar long-run averages do not prove convergence under equivalent opponent exposure.
- “Expected value zero” for resubmission is asserted without modelling submission retention rules, selection options, or uncertainty.
- Fifteen metagame time points lack per-date sample counts and coverage information.
- The “external human format’s equilibrium” is not defined, sourced, or justified as a valid target distribution.
- Replicator-process language is stronger than the descriptive share movements shown.
- Total-variation calculations lack a formula, category mapping, uncertainty, and treatment of unclassified decks.
- The forecast may have predicted only direction rather than the reported magnitude.
- Post-deadline movement may not validate a deadline-period prediction if participation or matchmaking changed.
- The 40.3% expected win rate is not reconciled with the reported 53% final performance.
- The 29.2% matchup estimate has only 24 games and substantial uncertainty.
- The two losing archetypes are not named.
- “The ceiling was structural” is plausible but not demonstrated by a complete matchup or deck counterfactual analysis.
- The corrected denominator pipeline has no displayed validation check.
- “Fixed minimum sample” never states the minimum.
- The distilled opponent, counter-archetype proxy, search lineage, and gate construction are unspecified.
- Lack of opening-specific code does not prove lack of initial-state dependence.
- “Higher rating means more exposure to the strongest archetype” is not directly evidenced.
- ML ladder ranges lack trial counts, match counts, and like-for-like evaluation conditions.
- The causal explanations for distillation and search failure are hypotheses, not isolated experimental findings.
- AUC .736–.742 lacks dataset, split, calibration, and connection to policy value.
- Pivoting after the public fork’s first 818.8 submission conflicts with the writeup’s warning against interpreting one submission.
- Scaling experiments are said to fall within confidence intervals, but neither estimates nor intervals are shown.
- The RL comparison relies on a participant report and does not establish that throughput was the only binding constraint.
- The released code, 79-row ledger, and regeneration scripts are claimed but not linked or represented in this file.
- Figures A–E are referenced, but only captions are present in the reviewed file.

# Unclear without competition-forum context

- Rozen’s V10 and what its original policy already contained.
- The identities and mechanics of the attacker, support line, special Psychic Energy, draw supporters, and gust supporter.
- “Top pool,” “field,” “external human format,” and “external equilibrium.”
- “Build,” “submission family,” “incumbent,” “ladder band,” and “final pair.”
- S1–S5, especially “light lethal graft,” “tempo gust,” “mirror-list adaptation,” and “stall guard.”
- “Mirror,” “meta,” “counter-archetype proxy,” “distilled-opponent gate,” and “search lineage.”
- Whether percentages are match win rates, score rates including draws, or another measure.
- Why current ratings differ from 1,000-game mean ratings.
- Discussion numbers and the meaning of “8/23.”
- The priority-number scale and how ties or repeated actions are resolved.
- “Paying for the gust” and why exactly one card is subtracted.
- Evolution-line-set classification and one-of tech-card mislabelling.
- Replicator process, total-variation distance, Bradley–Terry, rating-process replay, AUC, PPO, and entity transformer.
- “Throttled-matchmaking window.”
- What “five available submissions” means operationally.
- How Strategy-track ranking differs from overall placement.

# Three highest-impact edits

1. Embed Figures A–E at first reference, with legible axes, dates, samples, and uncertainty; captions alone cannot substantiate the central evidence.
2. After placement add: “Top 24.2%; against [baseline], each identical entry achieved [result] with 95% intervals [values] during [defined window].”
3. Name the attacker, draw engine, Energy, and gust supporter, then add a compact 60-card list with one-sentence role mapping.

| Question | Pass A score | Pass B score |
|---:|---:|---:|
| 1 | 4 | 4 |
| 2 | 4 | 3 |
| 3 | 4 | 4 |
| 4 | 3 | 3 |
| 5 | 3 | 3 |
| 6 | 4 | 4 |
| 7 | 3 | 3 |
| 8 | 4 | 4 |
| 9 | 2 | 2 |

Codex session ID: 01a07730-d45b-75a3-ab2c-347009329bec
Resume in Codex: codex resume 01a07730-d45b-75a3-ab2c-347009329bec
