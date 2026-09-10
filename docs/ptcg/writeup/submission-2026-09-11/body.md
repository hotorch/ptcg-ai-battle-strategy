## 1. Approach at a Glance

We treated the ladder itself as the object of study. Every build is a **distribution**, not a point (57 submissions across 23 builds). Every change is a **gated experiment** (a 21,975-decision replay regression, zero collateral changes). The metagame is a **dynamical system** we measured well enough to call its endpoint in writing before it arrived.

Our final agent is not a novel learning system. It is a public rule-based agent — Rozen's V10, credited explicitly — improved by five audited surgeries, of which the evidence let only two ship. The originality we claim is in the method, not the policy code.

Final entry: a matched **pair of the same build**. When the ladder stopped (31 Aug) they stood at **742.8 (54.0%)** and **700.2 (53.0%)** over their last 1,000 games, with 1,000-game means of 725.0 and 719.2. Final placement **1,611 / 6,807** (top 24%).

## 2. Deck Concept: an Attack That Scales With Your Hand

We picked the deck by mining daily replay exports for deck signatures and top-pool win rates, not from tier lists.

**The concept is one axis: keep your hand big.** The attacker is Alakazam, a Stage 2 whose damage scales with hand size (20 per card held), on a 4-4-4 Abra–Kadabra–Alakazam line with 3 Rare Candy to skip the middle stage. The support line is a Dunsparce–Dudunsparce draw engine, and 4 Telepath Psychic Energy bring the attacker online off one attachment. Every remaining slot serves that axis: draw supporters, recovery, energy denial to buy setup turns, and 3 Boss's Orders to convert a big hand into a prize.

**Key-card alignment is literal**, because the policy's numeric priorities *are* the deck plan (Figure A). Rare Candy sits at 16,000 because skipping Kadabra is the deck's tempo. Draw supporters outrank almost everything. Boss's Orders is the *only* Supporter allowed to outrank a draw Supporter, and only when arithmetic proves it wins the exchange this turn.

**What we learned too late.** By the second week the first- and third-most-played archetypes in the top pool were the two *worst*-performing — a crowd-pick paradox. Ours was one of them (13% share, 44% win rate). An independent post-deadline audit of 23,313 games (Discussion 737107) confirms the skew: 11.4% of the field, but only 6.9% of the top decile.

We kept it for a quantitative reason: the policy is tuned to this deck's card IDs, so a swap would have voided every gate result we owned with no budget left to re-earn them. The counter-evidence: one participant (Discussion 737125) gained ~200 points, 652 → 854, from deck arithmetic alone (HP breakpoints via +20 energy and +30 stadium). Our counterfactual cost was not zero. §5 quantifies the ceiling we accepted.

## 3. How the Agent Decides — and Why Only Two of Five Surgeries Shipped

The agent is a **priority cascade**. Every legal action is scored by a hand-written function of board state; the highest plays; the turn ends when nothing scores positive. The fork's only lookahead is a shallow 2-ply determinized check on main-phase choices; no learned model; our own deeper search with a learned evaluator lost (§7).

Onto the forked skeleton we attempted five surgeries. Two shipped: **S1**, a light lethal graft (our earlier lethal search takes the turn only when we hold ≤3 prizes; otherwise the fork decides), and **S5**, the tempo gust (mirror 50.0%, n=60; meta 85.0%, n=40; counter-archetype proxy 100%, n=40). Three — **S2** deck-out guard, **S3** mirror-list adaptation, **S4** stall guard — **passed every local no-regression gate (S2's mirror was a 29–31 tie) and never shipped**, because their submission families never cleared the incumbent's ladder band (§4).

**Worked example (S5).** The fork scores the gust supporter *below* draw supporters, usually correctly. But a gust that converts into a same-turn knockout is not a card — it is a prize. S5 adds one guarded branch. It fires only when the attacker is evolved and energized, the target is reachable and killable, and — the clause that makes it safe — the hand *after* paying for the gust still deals lethal:

```
(hand_size - 1) * 20 >= target.hp
```

Only then does the gust's priority jump from 2,262 to 6,000, stepping over the 4,249 draw supporter it displaces. The subtraction is the whole surgery: without it, the agent gusts itself out of the kill it gusted for.

**Verification standard.** We replayed 21,975 recorded decisions through the modified policy and diffed against the incumbent. **65 decisions changed; all 65 were the intended branch; zero collateral changes.** We shipped nothing whose diff we could not enumerate line by line.

## 4. Every Build Is a Distribution

The engine documents no seed replication, so paired A/B is unavailable. Worse, **one submission's rating is a single draw from a wide distribution.** We measured it directly by submitting the *same build* repeatedly:

- Build A, n = 7: 711.0 – 844.7 — a **134-point spread from identical code** (Figure B).
- Final build, n = 9: spread 81.

A 60-point "improvement" in one submission is inside the noise. This standard rejected S2–S4.

Others saw this too. Discussion 737125 (8/23) reports a byte-identical tarball submitted seven times: mean 765, sd 51, range 168. Discussion 737435 goes top-down — Bradley-Terry over all public episodes, 500 Monte-Carlo replays of the rating process — and finds wide rank intervals even in the gold zone. Kaggle staff have since said future simulations will re-rate with Bradley–Terry, and that noting this variance in a writeup is welcome (Discussion 738791). Our contribution is what we did with it: we **decomposed the variance into mechanisms**, ran it as a **rejection rule** on our own changes, and **closed it with convergence**.

Three mechanisms, each measured:

1. **Sticky placement.** One instance opened 4–1, spiked to 998 by game 6, and decayed to 750 by game 33 (Figure E, left). Early luck is amortized, not banked.
2. **New-submission scheduling priority.** In one window a fresh submission played 32 games while an older one played 1; same-day is not same-sample.
3. **Drift control.** An identical build resubmitted three days later scored 825.4 against a pre-period mean of 782 (n = 4). Inside the band: rating inflation rejected, not assumed.

**The closing experiment.** We locked two instances of one build as our final pair and watched 1,000 post-deadline games each (Figure E, right). Their 1,000-game means differ by **5.8**, against a same-build spread of 134 at ~50 games. But convergence buys a *band*, not a point: at matched game counts the two sat 19.8 points apart on average, up to 75.6, their 100-game rolling means crossed repeatedly, and the ladder's last read had them 43 apart. That is why we fired zero of five available submissions on the final day: once placement luck is amortized, resubmitting identical code has expected value zero.

## 5. The Metagame Is a Dynamical System

Daily replay exports let us compute the archetype composition of the top pool at 15 time points. Two caveats. The exports hold only each day's highest-rated episodes, so every share below describes the **top of the ladder, not the field**. And we classify by **evolution-line set**, not highest-rarity card: automatic labels in a public dump name eight of the top twenty decks after a one-of tech card (Discussion 737107); ours cannot.

**Selection pressure is measurable.** Shares moved as a replicator process predicts: low-win-rate crowd picks were culled, high-win-rate archetypes multiplied. We tracked total-variation distance to the *external* human format's equilibrium: **0.407 → 0.431 (peak) → 0.309 → 0.261** (Figure C), flat in week one, then falling monotonically through the deadline.

**The prediction, then the realization.** Two days before the deadline we wrote down a prediction: the final pool would concentrate further in one rising archetype. Realized: that archetype went **6.3% → 27.5%** by the deadline and **→ 32.9%** five days after; the collapsing crowd pick went **30.9% → 9.5% → 0.7%**, arriving at its external equilibrium of ~0. TV distance closed at 0.254, below every pre-deadline reading. The forecast rested on the mechanism, not extrapolation, and the post-deadline field confirmed it.

**Why this drove our decisions.** Re-weighting our measured matchups by the *forecast* field, expected win rate fell from 45–48% to **40.3%**. Our two worst matchups are public: **24.9% (n=197)** and **29.2% (n=24)**. That arithmetic said the ceiling was structural. So we spent the last week on a general-principle repair (S5) and an early lock, not on counter-tech for a field that had not arrived or a deck swap we could not validate.

**One honesty note.** Our first read of the late field was wrong — a denominator error inflated one share. We found it ourselves, rewrote and re-validated the aggregator, and every number above is from the corrected pipeline.

## 6. Consistency and Robustness

- **Both seats, always.** Every evaluation runs both seats with repeated games and a fixed minimum sample.
- **Gates that stopped measuring.** Generic opponents saturated at 85–90% in week one, so we built a distilled-opponent gate that held our search lineage near **52.5%**. By the final lineage it too had saturated (85%); only the incumbent mirror stayed informative at 50%. Figure D shows the saturation; it is why the ladder distribution, not the local gate, became our arbiter.
- **No initial-state dependence.** The cascade branches on board state — no seat-specific tables or opening scripts; the only turn-indexed rules are the fork's turn-1–2 setup priorities. Measured by seat (Figure D): mirror 43.3% vs 56.7% (n=30 each), saturated gates 95% vs 90% (n=40 each); the tilt sits inside the interval.
- **Worst cases published.** Both losing matchups are stated with sample sizes and the mechanism that binds them: higher rating means more exposure to the strongest archetype, so the ceiling tightens as you climb.
- **Consistency at scale.** Two locked instances, same code, independent match streams: 54.0% and 53.0% over their last 1,000 games each (95% CI ±3.1 points).

## 7. What Didn't Work

Our entire first week was a self-built machine-learning stack, and it lost to a public rule-based agent by a wide margin.

- **Replay-distilled policies** (a selection table mined from top-pool replays): ladder 327–571. Distillation regresses to the *average* of a pilot mixture, and the average of good players is a mediocre player.
- **Determinized turn search with a learned value function**: ladder 511–667. The value function reached AUC .736–.742, below the signal already encoded in a hand-tuned priority ordering. Better search over a worse evaluator is not better play.
- **The comparison that forced the pivot**: the public rule-based fork scored **818.8** on its first submission, beating everything we had built. We pivoted that day.
- **Three guards** (S2–S4) that passed every local gate and never translated to the ladder.
- **Three scaling experiments** (3× nodes, wider branching, 8-second budget) all landed inside confidence intervals; one tuned variant was rejected as overfit.
- **No reinforcement learning — a budget decision, not a verdict.** RL works here for teams that first buy throughput: the strongest public RL entry (Discussion 738158) trained a ~12M-parameter entity transformer by self-play PPO on a custom C++ vectorized engine at ~30 games/s and reached 1132. We ran only the official Python engine. The binding constraint was games per second, not algorithm. At our throughput, excluding RL was right. At theirs, it was not.

## 8. Conclusion and Code

The most transferable result here is not the agent. It is that on a noisy ladder, **a build is a distribution and a single submission is one sample from it** — and that measuring your own noise floor lets you tell a real improvement from a 130-point illusion. That discipline let us reject three of our own changes, hold on the final day, and predict the field we would have to beat.

Code, the full experiment ledger (78 experiments), and one regeneration command per figure are MIT-licensed; the repository opens at the hackathon's close.

**Cited participant work.** Rozen, V10 rule-based agent (fork base). Kaggle discussions 737125, 737435, 737107 and 738158, as cited in the text.
