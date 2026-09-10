# The Ladder as the Object of Study

*Draft 2 — 2026-09-02. Target ≤2,000 words. ①–⑨ mark the nine official scoring questions and are removed before submission. Changelog at the end (not counted).*

---

## 1. Approach at a Glance ①

We treated the ladder itself as the object of study. Every build is a **distribution**, not a point (57 submissions across 23 builds). Every change is a **gated experiment** (a 21,975-decision replay regression, zero collateral changes). The metagame is a **dynamical system** we measured well enough to call its endpoint in writing before it arrived.

Our final agent is not a novel learning system. It is a public rule-based agent — Rozen's V10, credited explicitly — improved by five audited surgeries, of which the evidence let only two ship. The originality we claim is in the method, not the policy code.

Final entry: a matched **pair of the same build**. When the ladder stopped (31 Aug) they stood at **742.8 (54.0%)** and **700.2 (53.0%)** over their last 1,000 games, with 1,000-game means of 725.0 and 719.2. Final placement **1,611 / 6,807** (top 24%).

---

## 2. Deck Concept: an Attack That Scales With Your Hand ⑥⑦

We picked the deck by mining daily replay exports for deck signatures and top-pool win rates, not from tier lists.

**The concept is one axis: keep your hand big.** The attacker is Alakazam, a Stage 2 whose damage scales with hand size (20 per card held), on a 4-4-4 Abra–Kadabra–Alakazam line with 3 Rare Candy to skip the middle stage. The support line is a Dunsparce–Dudunsparce draw engine, and 4 Telepath Psychic Energy bring the attacker online off one attachment. Every remaining slot serves that axis: draw supporters, recovery, energy denial to buy setup turns, and 3 Boss's Orders to convert a big hand into a prize.

**Key-card alignment is literal**, because the policy's numeric priorities *are* the deck plan (Figure A). Rare Candy sits at 16,000 because skipping Kadabra is the deck's tempo. Draw supporters outrank almost everything. Boss's Orders is the *only* card allowed to outrank drawing, and only when arithmetic proves it wins the exchange this turn.

**What we learned too late.** By the second week the first- and third-most-played archetypes in the top pool were the two *worst*-performing — a crowd-pick paradox. Ours was one of them (13% share, 44% win rate). An independent post-deadline audit of 23,313 games (Discussion 737107) confirms the skew: 11.4% of the field, but only 6.9% of the top decile.

We kept it for a quantitative reason: the policy is tuned to this deck's card IDs, so a swap would have voided every gate result we owned with no budget left to re-earn them. The counter-evidence: one participant (Discussion 737125) gained ~200 points, 652 → 854, from deck arithmetic alone (HP breakpoints via +20 energy and +30 stadium). Our counterfactual cost was not zero. §5 quantifies the ceiling we accepted.

---

## 3. How the Agent Decides — and Why Only Two of Five Surgeries Shipped ①②

The agent is a **deterministic priority cascade**. Every legal action is scored by a hand-written function of board state; the highest plays; the turn ends when nothing scores positive. No tree search, no learned model — we built both and both lost (§7).

Onto the forked skeleton we attempted five surgeries. Two shipped: **S1**, a light lethal graft (our earlier lethal search takes the turn only when we hold ≤3 prizes; otherwise the fork plays instantly), and **S5**, the tempo gust (mirror 50.0%, n=60; meta 85.0%, n=40; counter-archetype proxy 100%, n=40). Three — **S2** deck-out guard, **S3** mirror-list adaptation, **S4** stall guard — **passed every local no-regression gate (S2's mirror was a 29–31 tie) and never shipped**, because their submission families never cleared the incumbent's ladder band (§4).

**Worked example (S5).** The fork scores the gust supporter *below* draw supporters, usually correctly. But a gust that converts into a same-turn knockout is not a card — it is a prize. S5 adds one guarded branch. It fires only when the attacker is evolved and energized, the target is reachable and killable, and — the clause that makes it safe — the hand *after* paying for the gust still deals lethal:

```
(hand_size - 1) * 20 >= target.hp
```

Only then does the gust's priority jump from 2,262 to 6,000, stepping over the 4,249 draw supporter it displaces. The subtraction is the whole surgery: without it, the agent gusts itself out of the kill it gusted for.

**Verification standard.** We replayed 21,975 recorded decisions through the modified policy and diffed against the incumbent. **65 decisions changed; all 65 were the intended branch; zero collateral changes.** We shipped nothing whose diff we could not enumerate line by line.

---

## 4. Every Build Is a Distribution ③

The engine documents no seed replication, so paired A/B is unavailable. Worse, **one submission's rating is a single draw from a wide distribution.** We measured it directly by submitting the *same build* repeatedly:

- Build A, n = 7: 711.0 – 844.7 — a **134-point spread from identical code**.
- Final build, n = 9: spread 81.

A 60-point "improvement" in one submission is inside the noise. This standard rejected S2–S4.

Others saw this too. Discussion 737125 (8/23) reports a byte-identical tarball submitted seven times: mean 765, sd 51, range 168. Discussion 737435 goes top-down — Bradley-Terry over all public episodes, 500 Monte-Carlo replays of the rating process — and finds wide rank intervals even in the gold zone. Kaggle staff have since said future simulations will re-rate with Bradley–Terry, and that noting this variance in a writeup is welcome (Discussion 738791). Our contribution is what we did with it: we **decomposed the variance into mechanisms**, ran it as a **rejection rule** on our own changes, and **closed it with convergence**.

Three mechanisms, each measured:

1. **Sticky placement.** One instance opened 4–1, spiked to 998 by game 6, and decayed to 750 by game 33. Early luck is amortized, not banked.
2. **New-submission scheduling priority.** In one window a fresh submission played 32 games while an older one played 1; same-day is not same-sample.
3. **Drift control.** An identical build resubmitted three days later scored 825.4 against a pre-period mean of 782 (n = 4). Inside the band: rating inflation rejected, not assumed.

**The closing experiment.** We locked two instances of one build as our final pair and watched 1,000 post-deadline games each. Their 1,000-game means differ by **5.8**, against a same-build spread of 134 at ~50 games. But convergence buys a *band*, not a point: at matched game counts the two sat 19.8 points apart on average, up to 75.6, their 100-game rolling means crossed repeatedly, and the ladder's last read had them 43 apart. That is why we fired zero of five available submissions on the final day: once placement luck is amortized, resubmitting identical code has expected value zero. We held, and logged the hold as a decision.

---

## 5. The Metagame Is a Dynamical System ②④

Daily replay exports let us compute the archetype composition of the top pool at 15 time points. Two caveats. The exports hold only each day's highest-rated episodes, so every share below describes the **top of the ladder, not the field**. And we classify by **evolution-line set**, not highest-rarity card: automatic labels in a public dump name eight of the top twenty decks after a one-of tech card (Discussion 737107); ours cannot.

**Selection pressure is measurable.** Shares moved as a replicator process predicts: low-win-rate crowd picks were culled, high-win-rate archetypes multiplied. We tracked total-variation distance to the *external* human format's equilibrium: **0.407 → 0.431 (peak) → 0.309 → 0.261**, flat early and monotone after the first week.

**The prediction, then the realization.** Two days before the deadline we wrote down a prediction: the final pool would concentrate further in one rising archetype. Realized: that archetype went **6.3% → 27.5%** by the deadline and **→ 32.9%** five days after; the collapsing crowd pick went **30.9% → 9.5% → 0.7%**, arriving at its external equilibrium of ~0. TV distance reached a new low of 0.254. The forecast rested on the mechanism, not extrapolation, and the post-deadline field confirmed it.

**Why this drove our decisions.** Re-weighting our measured matchups by the *forecast* field, expected win rate fell from 45–48% to **40.3%**. Our two worst matchups are public: **24.9% (n=197)** and **29.2% (n=24)**. That arithmetic said the ceiling was structural. So we spent the last week on a general-principle repair (S5) and an early lock, not on counter-tech for a field that had not arrived or a deck swap we could not validate.

**One honesty note.** Our first read of the late field was wrong — a denominator error inflated one share. We found it ourselves, rewrote and re-validated the aggregator, and every number above is from the corrected pipeline.

---

## 6. Consistency and Robustness ③④

- **Both seats, always.** Every evaluation runs both seats with repeated games and a fixed minimum sample.
- **Gates that stopped measuring.** Generic opponents saturated at 85–90% in week one, so we built a distilled-opponent gate that held our search lineage near **52.5%**. By the final lineage it too had saturated (85%); only the incumbent mirror stayed informative at 50%. Figure D shows the saturation; it is why the ladder distribution, not the local gate, became our arbiter.
- **No initial-state dependence.** The cascade branches on board state only — no opening-specific cases, seat-specific tables, or hard-coded turn numbers. Measured by seat (Figure D): mirror 43.3% vs 56.7% (n=30 each), saturated gates 95% vs 90% (n=40 each); the tilt sits inside the interval.
- **Worst cases published.** Both losing matchups are stated with sample sizes and the mechanism that binds them: higher rating means more exposure to the strongest archetype, so the ceiling tightens as you climb.
- **Consistency at scale.** Two locked instances, same code, independent match streams: 54.0% and 53.0% over their last 1,000 games each (95% CI ±3.1 points).

---

## 7. What Didn't Work ②

Our entire first week was a self-built machine-learning stack, and it lost to a public rule-based agent by a wide margin.

- **Replay-distilled policies** (a selection table mined from top-pool replays): ladder 327–571. Distillation regresses to the *average* of a pilot mixture, and the average of good players is a mediocre player.
- **Determinized turn search with a learned value function**: ladder 511–667. The value function reached AUC .736–.742, below the signal already encoded in a hand-tuned priority ordering. Better search over a worse evaluator is not better play.
- **The comparison that forced the pivot**: the public rule-based fork scored **818.8** on its first submission, beating everything we had built. We pivoted that day.
- **Three guards** (S2–S4) that passed every local gate and never translated to the ladder.
- **Three scaling experiments** (3× nodes, wider branching, 8-second budget) all landed inside confidence intervals; one tuned variant was rejected as overfit.
- **No reinforcement learning — a budget decision, not a verdict.** RL works here for teams that first buy throughput: the strongest public RL entry (Discussion 738158) trained a ~12M-parameter entity transformer by self-play PPO on a custom C++ vectorized engine at ~30 games/s and reached 1132. We ran only the official Python engine. The binding constraint was games per second, not algorithm; torch's absence at inference is a deployment constraint, not evidence against RL. At our throughput, excluding RL was right. At theirs, it was not.

---

## 8. Conclusion and Code ⑧

The most transferable result here is not the agent. It is that on a noisy ladder, **a build is a distribution and a single submission is one sample from it** — and that measuring your own noise floor lets you tell a real improvement from a 130-point illusion. That discipline let us reject three of our own changes, hold on the final day, and predict the field we would have to beat.

Code, the full experiment ledger (78 experiments), and one regeneration command per figure are released under MIT.

**Cited participant work.** Rozen, V10 rule-based agent (fork base). Kaggle discussions 737125, 737435, 737107 and 738158, as cited in the text.

---

## Media Gallery captions (entered in the gallery fields, not the body)

*Figure A — the priority cascade with the five surgery sites: two shipped (S1, S5), three passed locally and did not translate (S2–S4).*

*Figure B — one point per submission, grouped by build. Figure E — left: the placement spike and decay; right: the final pair's 1,000-game trajectories.*

*Figure C — top-pool archetype shares at 15 dates vs the external equilibrium; throttled-matchmaking window shaded; lower panel, TV distance.*

*Figure D — final-build win rate per gate and seat, with sample sizes; two of three gates sit at the ceiling.*

---

## Draft 2 changelog (not part of the submission)

Scan checklist (2026-08-31) — 7 of 8 applied: §7 RL claim replaced (738158); §4 prior work cited, contribution redefined as mechanisms / rejection rule / convergence (737125, 737435); §2 counter-example with counterfactual cost (737125); §2 external low-band confirmation (737107); §5 evolution-line classification vs auto-labels, plus "top of the ladder, not the field" caveat (737107). Item 8 (Strategy track = 543 teams) left out of the body for word budget; add to §1 in Draft 3 only if words remain.

Figure-driven corrections (commit a26316c) — 3 of 3 applied: sticky spike 943 → 998 at game 6, 750 by game 33; pair convergence restated as 1,000-game means 6.6 apart with same-moment gap mean 20.2 / max 75.1 ("a band, not a point"); distilled gate 52.5% scoped to the search lineage, 85% saturation in the final lineage stated.

Other: build count 17 → 23 to match Figure B; surgery table folded into prose; Table 1 (card → weight) dropped since Figure A carries it; Table 2 (generation ablation) dropped for budget — reinstate only if words remain; §1 reproducibility sentence merged into §8.

Word count (2026-09-02, markdown stripped, em-dash splits counted): body ≈1,900 without captions, ≈2,000 with the five ~100-word captions. If Kaggle counts captions, trim ~30 words in Draft 3; if not, ~100 words of headroom remain for Table 2 or the 543-team line.

Open for Draft 3: (a) RESOLVED 9/2 — host rulings (Strategy topics 735679/738324/738657): body text only, space-separated count, Media Gallery and text inside figures/tables excluded, decklist as image/CSV attachment allowed, card names and official-visualizer artwork allowed. Form counter measured 9/2: pure whitespace tokens — pipes in markdown tables and image alt text are counted, so a markdown Table 2 would add ~110 counter-words. Actions: move the five captions into Media Gallery entries (body drops to ~1,890 by wc -w), render Table 2 (generation ablation) as an image rather than a markdown table, attach deck.csv, consider naming key cards directly in §2; keep the form counter itself ≤2,000 since judges may see it; (b) external read; (c) rescans 9/6 and 9/10; (d) strip ①–⑨ markers and the italic header before submitting; (e) verify Strategy entry/rules acceptance while logged in before the 9/6 entry deadline.

External review corrections (2026-09-06, Codex blind judge + fact-check, triage in `writeup/review/triage-2026-09-06.md`) — 9 of 9 text fixes applied: §2 "two most-played" → "first- and third-most-played" (Dragapult, 2nd by share, won 58.1%); §3/§7/Figure A "won every local gate" → "passed every local no-regression gate (S2's mirror was a 29–31 tie)"; §5 "two weeks after" → "five days after" (8/21 observation); §4 "at any moment" → "at matched game counts" (script aligns by game index); Figure E rolling window 101 → 100 to match the text; §7 distilled range 484–571 → 327–571 (H-010 hybrid included); §8 "79 rows" → "78 experiments", "script per figure" → "command per figure", "20-point improvement" → "improvement". Figures A and E regenerated. Still open from that review: A4 (final ratings/rank are an 8/31 snapshot; 9/6 read i8 742.8, i9 700.2, rank 1,611 — re-measure 9/10 and date the numbers), plus the judge's additions (card names, S1 definition, top-24% percentile, ±3.1%p CI, seat-split line). wc -w after fixes: 1,997 with captions, 1,908 without.

Judge-driven additions (2026-09-08): §1 "(top 24%)" after placement; §2 card names (Alakazam line, Dunsparce–Dudunsparce engine, Telepath Psychic Energy, Boss's Orders); §3 S1 defined in-line; §4 Kaggle-staff Bradley–Terry / variance remark cited (738791); §6 seat split from Figure D and ±3.1-point CI. The four figure captions moved out of the body into the Media Gallery block above. Body wc -w: 1,969 (captions excluded, separators excluded). Still open: A4 re-measure on 9/10; delete the three empty drafts on the Writeups tab before submitting; re-check SUBMITTED status after submit (bug report 739855).

Final re-measurement (2026-09-10, `watch_rank.py` + `watch_pair.py` + `report_figures.py fetch-ladder`): the ladder's last games for both instances ended 2026-08-31 23:58 UTC and nothing has moved since (9/6 and 9/10 reads identical). Final numbers replace the 8/31 01:00 snapshot: §1 742.8 (54.0%) / 700.2 (53.0%), 1,000-game means 725.0 / 719.2, placement 1,611 / 6,807 (23.7%); §4 mean difference 6.6 → 5.8, same-moment gap 20.2/75.1 → 19.8/75.6, plus the 43-point final-read gap added as further evidence for "a band, not a point"; §6 53.5/52.9 → 54.0/53.0. Figure E regenerated from the refreshed ladder JSONs (window now 8/21–8/31). A4 closed.
