## 1. Approach at a Glance

We treated the ladder itself as the object of study: **measure rating variability, test a specific decision error, and retain only changes we could explain**. Across 57 submissions in 23 experiment families, we learned why a promising local result need not become a stronger ladder agent.

Our final agent combines Rozen's public V10 policy with our selective lethal-search wrapper and a guarded knockout priority. We tested five changes and retained two. Our contribution is the measurement and decision-repair workflow, rather than a new learning architecture.

We submitted two instances of the same final build. At the ladder's last update on 31 August, their ratings were **742.8 and 700.2**; their last 1,000 games yielded **54.0% and 53.0% wins**, with mean ratings of 725.0 and 719.2. Final placement: **1,611 / 6,807 (top 24%)**. This is a study of an imperfect agent, including where our evidence failed to justify improvement.

## 2. Deck Concept: Turn Hand Size into Knockouts

**Alakazam converts each card in hand into 20 damage through damage counters.** Our 4-4-4 Abra–Kadabra–Alakazam line supports repeated attackers. Three Rare Candy provide a faster evolution route; retaining four Kadabra also preserves the normal route and its two-card evolution draw. Alakazam's evolution draws three more cards. The tradeoff is deliberate: evolving and drawing compete for resources but jointly build the next knockout.

The supporting engine uses **three Dunsparce and four Dudunsparce**. Dudunsparce draws three cards and returns itself to the deck, supporting repeated draw cycles. Four Buddy-Buddy Poffin establish small Basics; four Poké Pad find non-Rule-Box Pokémon. Four Hilda and four Dawn search evolution resources instead of relying only on random draws.

**Four Telepath Psychic Energy plus two basic Psychic Energy** support Alakazam's one-energy attack. Telepath also searches Basic Psychic Pokémon when attached to a Psychic Pokémon. Three Night Stretcher, one Sacred Ash and one Lana's Aid recover resources. Three Boss's Orders turn a reachable bench target into an immediate prize opportunity. Three Enhanced Hammer disrupt special-energy opponents, but offer no such benefit against basic-energy-only decks. Three Xerosic's Machinations compress the opponent's hand; one Lillie's Determination resets a poor hand. One Neutralization Zone protects non-Rule-Box Pokémon from opposing ex/V attack damage, while also benefiting eligible opposing Pokémon.

This is the retained list, not a claim that every count is optimal. We tested a reconstructed alternative list: it won 36/60 against its incumbent locally but did not establish a ladder advantage. Switching archetypes would also require rebuilding card-specific policy and evaluation coverage. We kept Alakazam with its weaknesses documented (§5). The attached deck files provide exact counts; Figure A connects its card roles to policy priorities.

## 3. How the Agent Decides

The fork ranks legal actions using board-state heuristics. Its shallow **2-ply determinized search** can override that ranking on eligible main-phase decisions. A determinization samples hidden information; it is not access to the opponent's actual hand. There is no learned evaluator in the final agent.

Our five changes are marked in Figure A. **S1**, retained, invokes our lethal search selectively when at most three prizes remain and time permits, or replays an already committed line. It requires two supporting sampled outcomes, using additional verification when initial votes are insufficient. Failure falls back to the fork. Selective invocation avoids converting observations and running prize inference on every decision; sampled agreement does not guarantee a win under all hidden states.

**S5**, retained, repairs a hand-size interaction. **S2** deck-out guard, **S3** alternative deck list and **S4** stall guard passed our operational local gates and were tested on the ladder, but were excluded from the final build. Their submission families did not show a convincing advantage over the incumbent's observed range.

**Worked example: S5.** Boss's Orders switches an opposing bench Pokémon into the active spot. Its original priority, 2,262, was below Lana's Aid at 4,249. The repair raises Boss to 6,000 only when the active Alakazam is ready to attack, the target passes the existing reachability and knockout checks, and the hand remaining after playing Boss still meets:

```
(hand_size - 1) * 20 >= target.hp
```

With eight cards and a 140-HP target, seven remaining cards meet the threshold exactly. With seven cards, the remaining six provide only 120, so this priority promotion does not fire. Other board-state guards must also hold. The decision is about **spending one card to cash in the rest of the hand**, rather than blindly preferring gust over recovery or draw.

**Verification.** On 21,975 recorded decisions from 168 episodes, comparison with the incumbent found **65 intended action changes and zero other changes**. This establishes the observed scope of the repair, not its effect on future trajectories. Match tests yielded 30/60 against the incumbent, 34/40 against a distilled opponent and 40/40 against a counter-archetype proxy. These passed our screening gates; they did **not** establish an overall win-rate gain.

## 4. Every Build Is a Distribution

Our engine workflow lacked documented seed replication, preventing matched-initial-state A/B tests. We instead repeated both-seat tests and measured the variability of repeated ladder submissions:

- **H024B:** seven submissions of the same build, 711.0–844.7: a 134-point range.
- **H036, the final build:** nine submissions, an 81-point range.

Figure B groups submissions by experiment family; only the highlighted families represent the identical-build comparisons above. Ratings are each submission's last recorded value, with differing game counts and dates. The ranges include scheduling and opponent-pool effects, not just random play. A single 60-point increase was therefore insufficient evidence for promotion; the observed range is a screening reference, not a statistical significance threshold.

Participant analysis in Discussion 737435 independently found broad rank uncertainty using Bradley–Terry modeling and rating-process simulations. We used our own observations to make operational decisions:

1. **Placement transients.** One submission opened 4–1, reached 998 at game six, and fell to 750 by game 33 (Figure E, left).
2. **Unequal exposure.** In one window a fresh submission played 32 games while an older one played one. Equal elapsed time did not mean equal evidence.
3. **Possible drift.** A repeat three days later scored 825.4 against four earlier submissions averaging 782. This small comparison could not separate drift from ordinary variation.

Our final pair then accumulated 1,000 post-deadline games each. Mean ratings differed by **5.8**, but at matched game counts their absolute gap averaged **19.8**, reaching **75.6**. Their final ratings remained **42.7** apart (Figure E). Similar long-run averages did not make individual ratings precise. These statistics describe two trajectories, not a controlled estimate of convergence rate.

We used none of our five submission slots on the final day. Without a validated policy change, we had no demonstrated lasting benefit from another identical-code submission. That was a resource decision, not proof that resubmitting has zero expected value.

## 5. Metagame Observation: A Forecast and Its Limits

We aggregated daily top-episode exports at **15 dates**, classifying decks by evolution-line sets. These are shares of exported **top-pool deck-games**, not the whole ladder. This avoids the particular tech-card labeling problem reported in Discussion 737107, since corrected, but does not eliminate sampling bias or all classification ambiguity.

On 14 August, following another participant's observation of the changing meta, we recorded a directional forecast: the post-deadline pool would become more Dragapult-heavy. The latest 8/13 sample showed 19.7% Dragapult; the 8/15 sample reached 27.5%, and 8/21 reached 32.9%. Grimmsnarl fell from 19.3% to 9.5% to 0.7%. The subsequent samples supported that directional forecast. They did not identify whether selection, imitation or matchmaking caused the changes.

**The stronger convergence hypothesis did not fully hold.** Figure C compares the samples with a Limitless TEF–POR reference collected on 8/14. Total-variation distance includes six named archetypes **and Other**, so both distributions sum to one. It fell from **0.426 on 8/04 to 0.370 on 8/15**, then rose to **0.393 on 8/21**. Grimmsnarl and Slowking were outside the reference's top 15 and were approximated as zero; this limits the comparison. The external distribution is a reference, not a demonstrated simulator equilibrium.

**Strategic implication.** In 1,129 exported Alakazam games across multiple pilots, the Dragapult matchup won **24.9% (n=197)** and Slowking **29.2% (n=24)**. These are archetype-level observations, not our final agent's measured matchups. They identified likely exposure risks, not a proven ceiling on our agent. Its actual 53–54% ladder win rates came from a different opponent pool.

The replay study also pointed to early knockouts of setup Pokémon, motivating S5's opponent-independent condition. We favored this bounded repair over an unvalidated archetype switch. During analysis we corrected a share-denominator error; during final review we also added the previously omitted Other term to TV. Figure C and the conclusions use the corrected calculation.

## 6. Consistency and Robustness

**Local repeatability.** Figure D separates the final tests by opponent and seat. Against the previous build, seat win rates were 43.3% and 56.7% (30 games each). Against the distilled opponent they were 90% and 80%; against the proxy, 100% in both seats (20 games per seat per opponent). The proxy's ceiling is evidence of an easy test, not strength against top pilots of that archetype.

**Operational gates, not equivalence tests.** S5's mirror threshold was 45%, and its distilled-opponent threshold 75%; observed results cleared both. These permissive screens can miss regressions. The 30/60 mirror result has a roughly 38–62% Wilson interval, leaving substantial uncertainty about relative strength.

**Initial-state coverage.** The fork uses board-state conditions and early-turn setup priorities. We tested both seats, but did not stratify opening hands or prove independence from favorable starts. S5 does not name an opponent archetype, although the inherited policy contains matchup-specific logic.

**Ladder evidence.** The two final instances won 540/1,000 and 530/1,000 games. A simple independent-game binomial approximation gives 95% intervals of about ±3.1 percentage points. Changing opponents and temporal dependence are not captured by that approximation. Repeated games are valuable evidence, but these streams are not controlled stable-condition trials.

## 7. What Didn't Work

Our first week centered on learned policies and search:

- **Replay-distilled action tables:** ladder 327–571. Pooling pilots and reducing their choices to selection frequencies did not reproduce their strategic strength.
- **Determinized turn search with a learned evaluator:** ladder 511–667, despite held-out evaluator AUC of .736–.742. Predictive discrimination did not translate into strong action selection.
- **The pivot:** the public fork's first result was 818.8, substantially above those families. We adopted it as the stronger starting point while continuing to measure submission variability.
- **Scaling:** three experiments increasing nodes, branching or time budget did not establish improvements; a variant tuned to one opponent lost against the incumbent.

We did not attempt reinforcement learning within the remaining budget. Discussion 738158 describes a participant's successful self-play PPO approach using a custom C++ engine at about 30 games per second. That comparison suggests a different throughput investment, not that RL is unsuitable for this game.

## 8. Conclusion and Code

The transferable workflow is **observe a strategic failure, repair a bounded decision, test both seats, and distinguish behavioral correctness from demonstrated competitive improvement**. Our strongest evidence is the enumerated S5 repair and repeated evaluation; our limitations include weak proxy opponents, uncertain matchup transfer and a convergence hypothesis that required narrowing.

The public [MIT repository](https://github.com/hotorch/ptcg-ai-battle-strategy) contains the experiment ledger (78 experiments) and analysis code. The final agent is in `candidates/h036_tempo_boss/`; replay-derived inputs are omitted. Rozen's [V10 notebook](https://www.kaggle.com/code/romanrozen/strong-start-baseline-agent-v10-lb-950) is the credited policy base. Participant discussions 737107, 737435 and 738158 are cited where used; figure captions provide source details.
