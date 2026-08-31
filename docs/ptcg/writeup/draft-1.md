# The Ladder as the Object of Study

*Draft 1 — 2026-08-31. Target ≤2,000 words. Section titles mirror the nine official scoring questions (①–⑨) for checklist scoring; those markers are drafting scaffolding and are removed before submission.*

---

## 1. Approach at a Glance ①

We treated the ladder itself as the object of study. Every build is a **distribution**, not a point (57 submissions across 17 builds). Every change is a **gated experiment** (a 21,975-decision replay regression, zero collateral changes). The metagame is a **dynamical system** we measured well enough to call its endpoint in writing before it arrived.

Our final agent is not a novel learning system, and we will not claim it is. It is a strong public rule-based agent — Rozen's V10, credited explicitly — improved by five audited surgeries, of which the evidence permitted only two to ship. The originality we are claiming is in the experimental method, not the policy code.

Final entry: a matched **pair of the same build**. Over the post-deadline convergence window they played 1,000 games each and finished **740.2 (53.5%)** and **731.9 (52.9%)** — 8.3 rating points apart. Final placement **1,649 / 6,807**.

Everything below is reproducible: the experiment ledger (`results.tsv`, 79 rows), the submission log, and one script per figure.

---

## 2. Deck Concept: an Attack That Scales With Your Hand ⑥⑦

We picked the deck by mining the daily replay exports — aggregating deck signatures and their win rates in the top pool — rather than by reading tier lists.

**The concept is one axis: keep your hand big.** The attacker is a Stage 2 whose damage scales with hand size (20 per card held), built on a 4-4-4 line with 3 Rare Candy to skip the middle stage. The support Pokémon line is a draw engine, and 4 copies of the special Psychic energy bring the attacker online off a single attachment. Every remaining slot serves that axis: draw supporters, recovery, and 3 copies of the gust supporter to convert a big hand into a prize.

**Key-card alignment is literal here**, because the policy's numeric priorities *are* the deck plan (§3). Rare Candy sits at 16,000 — near the top of the cascade — because skipping the Stage 1 is the deck's tempo. Draw supporters outrank almost everything. The gust supporter is the *only* card allowed to outrank drawing, and only when arithmetic proves it wins the exchange this turn. Energy denial (3 Enhanced Hammer, plus a supporter) exists to buy the turns the Stage 2 needs.

**What we learned too late.** By the second week the two most-played archetypes in the top pool were the two *worst*-performing — a crowd-pick paradox. Ours was one of them (13% share, 44% win rate). We kept it, and the reason is quantitative rather than sentimental: the policy is tuned to this deck's specific card IDs, so a deck swap would have invalidated every gate result we owned at a point where the remaining budget could not re-earn them. §5 quantifies exactly what that decision cost.

*Table 1: key cards → role → the cascade weight that implements it.*

---

## 3. How the Agent Decides — and Why Only Two of Five Surgeries Shipped ①②

The agent is a **deterministic priority cascade**. Every legal action is scored by a hand-written function conditioned on board state; the highest score is played; the turn ends when no positively-scored action remains. The final build contains no tree search and no learned model — we built both and both lost (§7).

Onto the forked skeleton we attempted five surgeries:

| # | Surgery | Local gate | Shipped |
|---|---|---|---|
| S1 | light lethal graft | won | **yes** |
| S2 | deck-out guard | won | no |
| S3 | mirror-list adaptation | won | no |
| S4 | stall guard | won | no |
| S5 | tempo gust | mirror 50.0% (n=60), meta 85.0% (n=40), proxy 100% (n=40) | **yes** |

Three surgeries that **won every local gate never shipped**, because their submission families never cleared the incumbent's ladder band (§4). That gap — local win, ladder silence — is the single most useful thing we measured.

**Worked example (S5, the tempo gust).** The fork scored the gust supporter *below* draw supporters, which is usually correct: drawing compounds, gusting does not. But when the gust converts into a knockout on the same turn, it is not a card — it is a prize. S5 adds one guarded branch. It fires only when the attacker is already the evolved Stage 2, already energized, the target is reachable and killable, and — the clause that makes it safe — the hand *after* paying for the gust still deals lethal:

```
(hand_size - 1) * 20 >= target.hp
```

Only then does the gust's priority jump from 2,262 to 6,000, stepping over the 4,249 draw supporter it displaces. The subtraction is the whole surgery: without it, the agent gusts itself out of the kill it gusted for.

**Verification standard.** We re-ran the modified policy across 21,975 recorded decisions from stored replays and diffed it against the incumbent. **65 decisions changed; all 65 were the intended branch; zero collateral changes anywhere else.** We shipped nothing whose diff we could not enumerate line by line.

*Figure A: the priority cascade with the five surgery sites marked (two green, three rejected).*

---

## 4. Every Build Is a Distribution ③

The engine documents no seed replication, so paired A/B testing is unavailable. The deeper problem is that **one submission's rating is a single draw from a wide distribution.** We measured that distribution directly, by submitting the *same build* repeatedly:

- Build A, n = 7: 711.0, 736.2, 739.7, 778.9, 793.6, 825.4, 844.7 — a **134-point spread from identical code**.
- Final build, n = 9: 674.0 – 756.6.

A 60-point "improvement" observed from one submission is inside the noise. This is the standard that rejected S2–S4.

Three ladder mechanisms we identified and measured:

1. **Sticky placement.** One instance opened 4–1, spiked to 943.1, then decayed to 750.1 over roughly 30 games. Early luck is amortized, not banked.
2. **New-submission scheduling priority.** In one matched window a fresh submission played 32 games while an older one played 1 — so same-day comparisons are not same-sample comparisons.
3. **Drift control.** We resubmitted an identical build three days later: 825.4 against a pre-period mean of 782 (n = 4). Inside the band, so we rejected the rating-inflation hypothesis rather than assuming it.

**The closing experiment.** We locked two instances of the same build as our final pair. Over the two-week convergence window they played 1,000 games each and landed **8.3 points apart** — against a same-build spread of 134 at ~50 games. The distribution is real, and convergence collapses it. That is also why we fired zero of five available submissions on the final day: once convergence erases placement luck, resubmitting identical code has expected value zero. We held, and reported the hold as a decision rather than an absence.

*Figure B: per-build instance strip plot. Figure E: the pair's rating trajectory with event annotations.*

---

## 5. The Metagame Is a Dynamical System ②④

Daily replay exports let us compute the archetype composition of the top pool at 15 time points. Two results.

**Selection pressure is measurable.** Shares moved the way a replicator process predicts: low-win-rate crowd picks were culled, high-win-rate archetypes multiplied. We used the equilibrium of the *external* human format as a leading indicator and tracked total-variation distance to it: **0.407 → 0.431 (peak) → 0.309 → 0.261**, flat early and monotone after the first week.

**The prediction, then the realization.** Two days before the deadline we recorded a written prediction that the final pool would be substantially more concentrated in one rising archetype. Realized: that archetype went **6.3% → 27.5%** by the deadline and **→ 32.9%** in the two weeks after; the collapsing crowd pick went **30.9% → 9.5% → 0.7%**, arriving at the external equilibrium of roughly zero. TV distance reached a new low of 0.254. The forecast was made on the mechanism, not on extrapolation, and the post-deadline field confirmed it.

**Why this drove our decisions.** Re-weighting our measured matchups by the *forecast* field rather than the current one, our expected win rate fell from 45–48% to **40.3%**. Our two worst matchups are public: **24.9% (n=197)** and **29.2% (n=24)**. That arithmetic said the ceiling was structural — no reachable tuning would out-run a field moving that direction. It is precisely why we spent the last week on a general-principle repair (S5) and an early lock, instead of counter-tech against a field that had not arrived yet or a deck swap we could no longer validate.

**One honesty note.** Our first read of the late field was wrong — a denominator error that inflated one share. We found it ourselves, corrected it in the repository with the aggregator rewritten and validated against an earlier reproduction, and every number above comes from the corrected pipeline.

*Figure C: 15-point share time series with the prediction arrow replaced by measured outcome; throttled sampling window shaded.*

---

## 6. Consistency and Robustness ③④

- **Both seats, always.** Every evaluation runs both seats with repeated games and a fixed minimum sample. No result in the ledger comes from a single seat.
- **Non-saturating gates.** Generic opponents saturated at 85–90%, which measures nothing. We built a distilled-opponent gate that holds the incumbent near **52.5%**, so a real improvement has room to show and a regression has room to fall.
- **No initial-state dependence.** The cascade branches on board state only — there are no opening-specific special cases, no seat-specific tables, and no hard-coded turn numbers.
- **Worst cases published, not hidden.** Both losing matchups are stated above with their sample sizes, together with the exposure mechanism that makes them bind: rising rating raises exposure to the strongest archetype, so the ceiling tightens as you climb.
- **Consistency, measured at scale.** The two locked instances, same code, independent match streams: 53.5% and 52.9% over 1,000 games each.

*Figure D: seat × archetype win-rate matrix.*

---

## 7. What Didn't Work ②

Our entire first week was a self-built machine-learning stack, and it lost to a public rule-based agent by a wide margin.

- **Replay-distilled policies** (a selection table mined from top-pool replays): ladder 484–571. Diagnosis — distillation regresses to the *average* of a mixture of pilots, and the average of good players is a mediocre player.
- **Determinized turn search with a learned value function**: ladder 511–667, best 667. Diagnosis — the value function reached AUC .736–.742, which is simply below the signal already encoded in a hand-tuned priority ordering. Better search over a worse evaluator is not better play.
- **The comparison that forced the pivot**: the public rule-based fork scored **818.8** on its first submission, beating everything we had built. We pivoted the same day and said so.
- **Three guards** (S2–S4) that won every local gate and never translated to the ladder.
- **Three scaling experiments** (3× nodes, wider search branching, 8-second budget) all landed inside confidence intervals, and one tuned variant was rejected as overfit.
- **No reinforcement learning**, on evidence: every public RL attempt we could find underperformed rule-based agents in this environment.

*Table 2: generation-by-generation ablation — key change, local gate, converged ladder rating.*

---

## 8. Conclusion and Code ⑧

The most transferable result here is not the agent. It is that on a noisy ladder, **a build is a distribution and a single submission is one sample from it** — and that a team which measures its own noise floor can tell a real 20-point improvement from a 130-point illusion. That discipline is what let us reject three of our own changes, hold on the final day, and predict the field we would have to beat.

Code, the full experiment ledger, and one regeneration script per figure are released under MIT.

---

*Word count target check pending — see drafting notes below.*
