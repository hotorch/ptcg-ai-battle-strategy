| section | claim (verbatim) | status (VERIFIED / MISMATCH / NOT FOUND) | evidence location (file path + line or record id) | note |
|---|---|---|---|---|
| §3 | “The agent is a **deterministic priority cascade**. Every legal action is scored by a hand-written function of board state; the highest plays” | MISMATCH | `candidates/h036_tempo_boss/fork_policy.py:666-679,926-1051,1068-1093`; `candidates/h036_tempo_boss/main.py:72-95,130-146` | 최종 에이전트는 `random.shuffle` 기반 결정화와 탐색을 실행하며, 탐색 결과가 최고 휴리스틱 점수를 덮어쓸 수 있다. |
| §3 | “No tree search, no learned model — we built both and both lost” | MISMATCH | `candidates/h036_tempo_boss/fork_policy.py:674-679,926-1051`; `candidates/h036_tempo_boss/main.py:72-95`; `candidates/h036_tempo_boss/lethal_search.py:15-17,962` | 학습 모델이 없다는 부분은 맞지만, 일반 2-ply 탐색과 S1 lethal search가 최종 빌드에 모두 포함된다. |
| §6 | “No initial-state dependence. The cascade branches on board state only — no opening-specific cases, seat-specific tables, or hard-coded turn numbers.” | MISMATCH | `candidates/h036_tempo_boss/fork_policy.py:255,304,420,441,452,458,608,935` | `turn <= 2`, `turn >= 2`, `turn < 2` 등 명시적인 초반·턴 번호 분기가 다수 존재한다. 좌석 전용 테이블은 발견되지 않았다. |
| §2 | “Boss's Orders is the *only* card allowed to outrank drawing” | MISMATCH | `candidates/h036_tempo_boss/fork_policy.py:20-31,45` | Rare Candy 16,000, Poffin 18,000, Poké Pad 17,000, Dawn emergency 16,500 등 여러 카드가 4,249 이하의 드로 서포터보다 높다. “only non-draw Supporter in this comparison”처럼 범위를 좁혀야 한다. |
| §5 | “flat early and monotone after the first week” | MISMATCH | `scratch/decks_2026-08-04.json`–`scratch/decks_2026-08-21.json`; `scripts/report_figures.py:289-303` | 전체 15시점 TV는 8/15 이후 0.261→0.267→0.226→0.324→0.285→0.265→0.254로 단조가 아니다. 8/08–8/15 구간만 단조 감소한다. |
| §8 | “Code, the full experiment ledger (78 experiments), and one regeneration command per figure are released under MIT.” | NOT FOUND | `LICENSE:1-20`; `research_loop/results.tsv:1-79`; `scripts/report_figures.py:774-823`; Git index: `LICENSE` has no tracked record | 78개 실험과 그림별 명령은 확인된다. MIT 파일은 존재하지만 현재 untracked여서 공개된 저장소 릴리스에 포함됐다는 증거는 없다. |
| §1 | “57 submissions across 23 builds” | VERIFIED | `submissions/history.tsv:1-58`; `submissions/rating_history.tsv`; `scripts/report_figures.py:497-524,527-532` | 57개 제출 레코드와 23개 정규화된 빌드 그룹이 재계산된다. |
| §1 | “a 21,975-decision replay regression, zero collateral changes” | VERIFIED | `docs/ptcg/journal/2026-08-14.md:17,26` | 21,975결정, 의도된 65개 변경, 부수 변경 0, 오류 0. |
| §1 | “The metagame is a dynamical system we measured well enough to call its endpoint in writing before it arrived.” | VERIFIED | `docs/ptcg/research/top-agent-observation.md:77-96,117-120`; `docs/ptcg/writeup/draft-context.md:62` | 8/14 예측과 8/21 후속 관측이 기록돼 있다. |
| §1 | “a public rule-based agent — Rozen's V10, credited explicitly” | VERIFIED | `docs/ptcg/09-submission-log.md:22,57`; `candidates/h036_tempo_boss/main.py:12-13` | 포크 출처와 크레딧이 명시돼 있다. 단, 최종 실행 경로는 순수 룰 캐스케이드만은 아니다. |
| §1 | “improved by five audited surgeries, of which the evidence let only two ship” | VERIFIED | `scripts/report_figures.py:472-489`; `docs/ptcg/writeup/draft-context.md:26,61` | S1–S5 중 최종 빌드 포함은 S1·S5다. |
| §1 | “Final entry: a matched **pair of the same build**.” | VERIFIED | `submissions/history.tsv:57-58`; `docs/ptcg/writeup/draft-context.md:17` | 55525772와 55525773은 동일 H-036 패키지다. |
| §1 | “When the ladder stopped (31 Aug)” | VERIFIED | `research_loop/ladder/55525772.json`, episode 104462377; `research_loop/ladder/55525773.json`, episode 104460167 | 마지막 종료 시각은 각각 2026-08-31 23:58:33 UTC와 23:54:08 UTC다. |
| §1 | “742.8 (54.0%)” | VERIFIED | `research_loop/ladder/55525772.json`, episodes 96183680–104462377 | 최종 rating 742.8836, 최근 1,000경기 540승이다. |
| §1 | “700.2 (53.0%)” | VERIFIED | `research_loop/ladder/55525773.json`, episodes 96197083–104460167 | 최종 rating 700.2005, 최근 1,000경기 530승이다. |
| §1 | “with 1,000-game means of 725.0 and 719.2” | VERIFIED | 동일 두 ladder JSON; 계산 규약 `scripts/report_figures.py:710-730` | `updatedScore` 평균은 724.9852와 719.1863이다. |
| §1 | “Final placement **1,611 / 6,807** (top 24%).” | VERIFIED | `submissions/rank_history.tsv:6` | 1,611/6,807 = 23.67%, 올림 표현으로 top 24%가 맞다. |
| §2 | “We picked the deck by mining daily replay exports for deck signatures and top-pool win rates, not from tier lists.” | VERIFIED | `docs/ptcg/journal/2026-08-10.md:41-48`; `docs/ptcg/research/top-agent-observation.md:27-46` | 최종 구리스트 유지 결정은 replay signature·승률·정책 적합성 비교에 근거했다. |
| §2 | “Alakazam, a Stage 2 whose damage scales with hand size (20 per card held)” | VERIFIED | `data/raw/EN Card Data.csv:1309-1310` | Stage 2이며 손패 한 장당 damage counter 2개, 즉 20 damage다. |
| §2 | “a 4-4-4 Abra–Kadabra–Alakazam line with 3 Rare Candy” | VERIFIED | `candidates/h036_tempo_boss/deck.csv:14-28`; 카드 매핑 `fork_policy.py:65-76` | 741·742·743 각 4장, 1079 세 장이다. |
| §2 | “The support line is a Dunsparce–Dudunsparce draw engine” | VERIFIED | `candidates/h036_tempo_boss/deck.csv:7-13`; `data/raw/EN Card Data.csv:129-132,586-587` | Dunsparce 3장, Dudunsparce 4장이며 Dudunsparce 능력은 3장 드로다. |
| §2 | “4 Telepath Psychic Energy bring the attacker online off one attachment” | VERIFIED | `candidates/h036_tempo_boss/deck.csv:3-6`; `data/raw/EN Card Data.csv:41,1310` | 에너지 4장과 Alakazam의 `{P}` 1에너지 공격 비용이 일치한다. |
| §2 | “3 Boss's Orders” | VERIFIED | `candidates/h036_tempo_boss/deck.csv:44-46`; `data/raw/EN Card Data.csv:1988` | ID 1182가 정확히 3장이다. |
| §2 | “Every remaining slot serves that axis: draw supporters, recovery, energy denial to buy setup turns” | VERIFIED | `candidates/h036_tempo_boss/deck.csv:29-60`; `data/raw/EN Card Data.csv:1858,1878,1920,1957,1990,2014,2050-2058,2080` | Hammer, recovery, search/draw 및 방어 Stadium 구성과 부합한다. |
| §2 | “Rare Candy sits at 16,000 because skipping Kadabra is the deck's tempo.” | VERIFIED | `candidates/h036_tempo_boss/fork_policy.py:22,45,462-463`; `data/raw/EN Card Data.csv:1854` | 우선순위 16,000이며 카드 효과가 Stage 1을 건너뛴다. |
| §2 | “the first- and third-most-played archetypes in the top pool were the two *worst*-performing” | VERIFIED | `docs/ptcg/research/top-agent-observation.md:27-41` | Grimmsnarl 1위/41.2%, Alakazam 3위/43.8%로 명시된 아키타입 중 최저 두 승률이다. |
| §2 | “Ours was one of them (13% share, 44% win rate).” | VERIFIED | `docs/ptcg/research/top-agent-observation.md:33` | 원값 13.2%, 43.8%를 반올림했다. |
| §2 | “23,313 games (Discussion 737107)” | VERIFIED | `docs/ptcg/research/2026-08-31-solution-scan.md:66-68` | Discussion 번호와 표본 수가 일치한다. |
| §2 | “11.4% of the field, but only 6.9% of the top decile.” | VERIFIED | `docs/ptcg/research/2026-08-31-solution-scan.md:68-71` | 정확히 기록된 수치다. 해당 Discussion의 상위 에피소드 표본 한계가 적용된다. |
| §2 | “the policy is tuned to this deck's card IDs, so a swap would have voided every gate result we owned with no budget left to re-earn them” | VERIFIED | `docs/ptcg/research/top-agent-observation.md:41-45`; `docs/ptcg/journal/2026-08-10.md:43-45` | 카드별 가중치와 실제 덱 교체 실패 게이트가 기록돼 있다. |
| §2 | “Discussion 737125 gained ~200 points, 652 → 854” | VERIFIED | `docs/ptcg/research/2026-08-31-solution-scan.md:25,32-33,46` | 원값 652→853.8로, 854와 약 +200이 맞다. |
| §2 | “HP breakpoints via +20 energy and +30 stadium” | VERIFIED | `docs/ptcg/research/2026-08-31-solution-scan.md:32-33` | Discussion 요약에 동일한 두 조정이 기록돼 있다. |
| §3 | “we attempted five surgeries. Two shipped: **S1** … and **S5**” | VERIFIED | `scripts/report_figures.py:472-489` | 다섯 수술과 최종 포함 두 수술이 명시돼 있다. |
| §3 | “S1, a light lethal graft … takes the turn only when we hold ≤3 prizes; otherwise the fork plays instantly” | VERIFIED | `candidates/h036_tempo_boss/main.py:42-69,100-149`; `docs/ptcg/journal/2026-08-10.md:23-37` | 정확히는 창 밖에서 포크로 즉시 위임한다. 포크 내부 탐색까지 즉시라는 뜻은 아니다. |
| §3 | “mirror 50.0%, n=60; meta 85.0%, n=40; counter-archetype proxy 100%, n=40” | VERIFIED | `research_loop/results.tsv:78-79`; run records `20260814-H036-01`, `20260814-H036-02` | 30/60, 34/40, 40/40이다. |
| §3 | “S2's mirror was a 29–31 tie” | VERIFIED | `research_loop/results.tsv:70`; `docs/ptcg/journal/2026-08-12.md:36` | 29승 31패, 48.3%, CI 36.2–60.7%다. |
| §3 | “S2 … S3 … S4 … passed every local no-regression gate and never shipped” | VERIFIED | `research_loop/results.tsv:70-77`; `docs/ptcg/journal/2026-08-12.md:36`; `submissions/rating_history.tsv:792-800` | no-regression 판정은 기록돼 있으며 최종 H-036에는 미포함이다. 다만 세 계열 모두 실제 ladder 제출은 되었으므로 “never shipped”는 “never made the final build” 의미로만 정확하다. |
| §3 | “their submission families never cleared the incumbent's ladder band” | VERIFIED | `submissions/rating_history.tsv:792-800,806-809` | S2–S4 최고치가 H-024b 가족 상단 844.7을 넘지 못했다. |
| §3 | “S5 adds one guarded branch.” | VERIFIED | `docs/ptcg/journal/2026-08-14.md:13-17`; `scripts/report_figures.py:401-402` | H-024b 대비 `boss_kill_now` 조건부 승격 한 건으로 기록됐다. |
| §3 | “only when the attacker is evolved and energized, the target is reachable and killable” | VERIFIED | `candidates/h036_tempo_boss/fork_policy.py:480-489` | Alakazam·Psychic energy·attack option·target 조건을 모두 검사한다. |
| §3 | “(hand_size - 1) * 20 >= target.hp” | VERIFIED | `candidates/h036_tempo_boss/fork_policy.py:485`; `docs/ptcg/journal/2026-08-14.md:15` | 코드와 문서가 정확히 일치한다. |
| §3 | “priority jump from 2,262 to 6,000, stepping over the 4,249 draw supporter” | VERIFIED | `candidates/h036_tempo_boss/fork_policy.py:27,45,480-489` | `boss_kill=2262`, `boss_kill_now=6000`, `lana=4249`다. |
| §3 | “65 decisions changed; all 65 were the intended branch; zero collateral changes.” | VERIFIED | `docs/ptcg/journal/2026-08-14.md:17,26` | 정확한 회귀 결과다. |
| §4 | “The engine documents no seed replication, so paired A/B is unavailable.” | VERIFIED | `docs/ptcg/03-validation.md:3-6` | 동일 초기상태를 재현하는 공식 seed/export/import 경로가 없다. |
| §4 | “Build A, n = 7: 711.0 – 844.7 — a **134-point spread from identical code**” | VERIFIED | `submissions/rating_history.tsv:791,793,801,806-809` | H-024b 7개, 정확한 spread 133.7이다. |
| §4 | “Final build, n = 9: spread 81.” | VERIFIED | `submissions/rating_history.tsv:782-790`; final pair JSONs | H-036 범위 674.0–754.9, spread 80.9다. |
| §4 | “A 60-point ‘improvement’ in one submission is inside the noise.” | VERIFIED | 동일 H-024b/H-036 분포 레코드 | 관측된 동일 코드 산포 80.9와 133.7 모두 60보다 크다. |
| §4 | “This standard rejected S2–S4.” | VERIFIED | `docs/ptcg/research/2026-08-31-solution-scan.md:37-45`; `submissions/rating_history.tsv:792-800` | 분포 기반 기각 규칙과 세 계열의 최종 제외가 기록돼 있다. |
| §4 | “Discussion 737125 (8/23) … seven times: mean 765, sd 51, range 168.” | VERIFIED | `docs/ptcg/research/2026-08-31-solution-scan.md:25-30` | 원값 n=7, mean 765.0, sd 51.4, range 168.2다. |
| §4 | “Discussion 737435 … Bradley-Terry over all public episodes, 500 Monte-Carlo replays” | VERIFIED | `docs/ptcg/research/2026-08-31-solution-scan.md:53-59` | BT 적합과 500회 rating-process simulation이 기록돼 있다. |
| §4 | “wide rank intervals even in the gold zone” | VERIFIED | `docs/ptcg/research/2026-08-31-solution-scan.md:57-59` | 예시 5–95% 순위 범위 7–19가 기록돼 있다. |
| §4 | “future simulations will re-rate with Bradley–Terry … variance in a writeup is welcome (Discussion 738791)” | VERIFIED | `docs/ptcg/research/2026-09-08-solution-scan.md:13-16` | Kaggle staff 발언 요약과 Discussion 번호가 일치한다. |
| §4 | “Three mechanisms, each measured” | VERIFIED | `docs/ptcg/research/2026-08-31-solution-scan.md:39-45` | sticky placement, scheduling priority, drift control 세 가지가 열거돼 있다. |
| §4 | “opened 4–1, spiked to 998 by game 6, and decayed to 750 by game 33” | VERIFIED | `research_loop/ladder/55515319.json`, games 1–33 | game 6 rating 998.0515, game 33 rating 750.1026이다. |
| §4 | “a fresh submission played 32 games while an older one played 1” | VERIFIED | `docs/ptcg/journal/2026-08-15.md:12-15` | 동일 4시간 창의 관측값이다. |
| §4 | “resubmitted three days later scored 825.4 against a pre-period mean of 782 (n = 4)” | VERIFIED | `submissions/rating_history.tsv:793,806-809`; `submissions/history.tsv:47` | 초기 네 값 평균 782.05, 3일 뒤 동일 패키지 825.4다. |
| §4 | “watched 1,000 post-deadline games each” | VERIFIED | `research_loop/ladder/55525772.json`; `research_loop/ladder/55525773.json` | 각각 score-bearing episode가 정확히 1,000개다. |
| §4 | “Their 1,000-game means differ by **5.8**” | VERIFIED | 동일 두 JSON; `scripts/report_figures.py:724,733-739` | 재계산값 5.7988769다. |
| §4 | “same-build spread of 134 at ~50 games” | VERIFIED | `submissions/rating_history.tsv:791,793,801,806-809`; `docs/ptcg/research/2026-08-31-solution-scan.md:43` | H-024b의 133.7점 산포와 당시 약 40–50경기 표본을 가리킨다. |
| §4 | “at matched game counts the two sat 19.8 points apart on average, up to 75.6” | VERIFIED | pair JSONs; `scripts/report_figures.py:733-739` | 같은 game index끼리 절댓값 차이를 계산하면 mean 19.7797, max 75.6004다. 실제 동시각 비교는 아니다. |
| §4 | “their 100-game rolling means crossed repeatedly” | VERIFIED | pair JSONs; `scripts/report_figures.py:719-723` | 100-game window 재계산에서 부호 교차가 10회 발생한다. |
| §4 | “the ladder's last read had them 43 apart” | VERIFIED | pair JSON final episodes 104462377 and 104460167 | 최종 차이는 42.6831로, 반올림하면 43이다. |
| §4 | “zero of five available submissions on the final day” | VERIFIED | `docs/ptcg/journal/2026-08-16.md:14-18,21-25` | 탄환 사용 0/5가 기록돼 있다. |
| §4 | “We held, and logged the hold as a decision.” | VERIFIED | `docs/ptcg/journal/2026-08-16.md:14-25` | HOLD 원칙과 실행 결과가 모두 기록돼 있다. |
| §5 | “archetype composition of the top pool at 15 time points” | VERIFIED | `scratch/decks_2026-08-04.json`–`scratch/decks_2026-08-21.json`; `docs/ptcg/writeup/draft-context.md:53` | 날짜가 붙은 덤프가 정확히 15개다. |
| §5 | “exports hold only each day's highest-rated episodes … top of the ladder, not the field” | VERIFIED | `docs/ptcg/research/2026-08-31-solution-scan.md:68,79-82` | 외부 감사와 내부 문서 모두 동일한 표집 한계를 명시한다. |
| §5 | “we classify by evolution-line set” | VERIFIED | `scripts/archetype_shares.py:10-25` | 각 아키타입을 진화 라인 ID 집합 포함 여부로 판정한다. |
| §5 | “automatic labels … name eight of the top twenty decks after a one-of tech card (Discussion 737107)” | VERIFIED | `docs/ptcg/research/2026-08-31-solution-scan.md:66-78` | Fezandipiti ex 1-of가 20대 덱 중 8개를 덮어쓴 사례가 기록돼 있다. |
| §5 | “0.407 → 0.431 (peak) → 0.309 → 0.261” | VERIFIED | `scratch/decks_2026-08-04.json`, `08-06`, `08-14`, `08-15`; `scripts/report_figures.py:289-303` | 재계산값 0.407463, 0.431205, 0.309174, 0.261097이다. |
| §5 | “Two days before the deadline we wrote down a prediction” | VERIFIED | `docs/ptcg/research/top-agent-observation.md:25,77-96`; deadline `docs/ptcg/07-strategy-track.md:18` | 8/14 기록, 8/16 UTC 마감으로 달력 날짜 기준 이틀 전이다. |
| §5 | “6.3% → 27.5% by the deadline and → 32.9% five days after” | VERIFIED | `scratch/decks_2026-08-04.json`, `08-15`, `08-21`; `docs/ptcg/writeup/draft-context.md:59,62` | 재계산값 6.319%, 27.517%, 32.890%다. |
| §5 | “30.9% → 9.5% → 0.7%” | VERIFIED | 동일 8/04·8/15·8/21 덤프 | 재계산값 30.939%, 9.544%, 0.702%다. |
| §5 | “arriving at its external equilibrium of ~0” | VERIFIED | `scripts/report_figures.py:257-266`; `docs/ptcg/research/top-agent-observation.md:81` | Grimmsnarl은 외부 상위 15위 밖이어서 비교 규약상 0으로 둔다. |
| §5 | “TV distance reached a new low of 0.254.” | VERIFIED | `scratch/decks_2026-08-21.json`; `scripts/report_figures.py:289-303` | 재계산값 0.254215다. 신뢰 가능한 비-throttle 후속 시점 중 최저다. |
| §5 | “expected win rate fell from 45–48% to **40.3%**” | VERIFIED | `docs/ptcg/research/top-agent-observation.md:44,95,117-120` | 메타 점유율 재가중 결과가 해당 범위와 최종값으로 기록돼 있다. |
| §5 | “24.9% (n=197) and 29.2% (n=24)” | VERIFIED | `docs/ptcg/research/top-agent-observation.md:54-67` | Dragapult와 Slowking이 최저 두 매치업이며 수치와 표본이 정확하다. |
| §5 | “a denominator error inflated one share” | VERIFIED | `docs/ptcg/research/top-agent-observation.md:99-108`; `docs/ptcg/journal/2026-08-16.md:13` | episode 수 대신 deck-game 수를 써야 하는 오류와 수정이 기록돼 있다. |
| §6 | “Every evaluation runs both seats with repeated games and a fixed minimum sample.” | VERIFIED | `docs/ptcg/03-validation.md:7-18`; H-036 run records | 공식 평가 프로토콜과 H-036 좌석 균형 레코드가 일치한다. |
| §6 | “Generic opponents saturated at 85–90% in week one” | VERIFIED | `docs/ptcg/journal/2026-08-07.md:37` | 정확한 포화 범위가 기록돼 있다. |
| §6 | “a distilled-opponent gate that held our search lineage near **52.5%**” | VERIFIED | `research_loop/results.tsv:26`; `docs/ptcg/journal/2026-08-07.md:37` | H-016은 21/40 = 52.5%다. |
| §6 | “By the final lineage it too had saturated (85%); only the incumbent mirror stayed informative at 50%.” | VERIFIED | `research_loop/results.tsv:78-79` | 최종 meta0d 85%, mirror 50%다. |
| §6 | “mirror 43.3% vs 56.7% (n=30 each)” | VERIFIED | run record `20260814-H036-01` | 좌석별 13/30과 17/30이다. |
| §6 | “saturated gates 95% vs 90% (n=40 each)” | VERIFIED | run record `20260814-H036-02` | meta0d+proxy 합산 좌석별 38/40과 36/40이다. |
| §6 | “Two locked instances … 54.0% and 53.0% over their last 1,000 games each (95% CI ±3.1 points).” | VERIFIED | pair JSONs, final episodes 104462377 and 104460167 | Wald half-width는 각각 약 3.09pp와 3.10pp다. |
| §7 | “Our entire first week was a self-built machine-learning stack, and it lost to a public rule-based agent by a wide margin.” | VERIFIED | `docs/ptcg/writeup/draft-context.md:24-26`; `docs/ptcg/09-submission-log.md:16-22` | 첫 주 최고 search 결과 667.0 대 fork 818.8이다. |
| §7 | “Replay-distilled policies … ladder 327–571.” | VERIFIED | `docs/ptcg/09-submission-log.md:16-17,39-47`; `submissions/rating_history.tsv:778-781` | 전체 증류 계열 범위 326.9–571.4다. |
| §7 | “Determinized turn search with a learned value function: ladder 511–667.” | VERIFIED | `docs/ptcg/09-submission-log.md:18-21,49-56` | 관련 계열 범위 511.6–667.0이다. |
| §7 | “The value function reached AUC .736–.742” | VERIFIED | `docs/ptcg/04-hypotheses.md:18,23`; `docs/ptcg/journal/2026-08-07.md:19` | 두 held-out AUC가 정확히 기록돼 있다. |
| §7 | “the public rule-based fork scored **818.8** on its first submission” | VERIFIED | `docs/ptcg/09-submission-log.md:57`; `docs/ptcg/journal/2026-08-09.md:38-42` | 첫 H-022 제출 점수다. |
| §7 | “Three guards (S2–S4) that passed every local gate and never translated to the ladder.” | VERIFIED | `research_loop/results.tsv:70-77`; `submissions/rating_history.tsv:792-800` | “passed”는 no-regression 기준을 뜻한다. 세 계열 모두 제출됐지만 최종 빌드에는 들어가지 않았다. |
| §7 | “Three scaling experiments (3× nodes, wider branching, 8-second budget) all landed inside confidence intervals” | VERIFIED | `docs/ptcg/journal/2026-08-07.md:10-13,46,51`; `docs/ptcg/writeup/draft-context.md:69` | 노드·K·시간 예산 확장이 유의 개선을 만들지 못했다. |
| §7 | “one tuned variant was rejected as overfit.” | VERIFIED | `research_loop/results.tsv:34-35`; `docs/ptcg/04-hypotheses.md:29` | H-017f가 target gate 80%지만 mirror 37.5%로 기각됐다. |
| §7 | “Discussion 738158 … ~12M-parameter entity transformer … self-play PPO … custom C++ vectorized engine at ~30 games/s and reached 1132.” | VERIFIED | `docs/ptcg/research/2026-08-31-solution-scan.md:10-23` | Discussion 번호, 모델 규모, PPO, C++, 처리량, 점수가 모두 일치한다. |
| §7 | “We ran only the official Python engine.” | VERIFIED | `docs/ptcg/research/2026-08-31-solution-scan.md:20-23`; `docs/ptcg/03-validation.md` | 내부 연구 경로가 공식 Python/CABT 엔진으로 기록돼 있다. |
| §7 | “torch's absence at inference is a deployment constraint, not evidence against RL.” | VERIFIED | `docs/ptcg/research/2026-08-31-solution-scan.md:49-51` | 저장소 연구 노트에 동일한 구분이 명시돼 있다. |
| §8 | “a 130-point illusion” | VERIFIED | `submissions/rating_history.tsv:791,793,801,806-809` | 동일 빌드 최대 산포 133.7을 130으로 근사한 표현이다. |
| §8 | “reject three of our own changes, hold on the final day, and predict the field” | VERIFIED | `docs/ptcg/research/2026-08-31-solution-scan.md:39-45`; `docs/ptcg/journal/2026-08-16.md:14-25`; `docs/ptcg/research/top-agent-observation.md:96,117-120` | 세 결과 모두 원장에 남아 있다. |
| §8 | “the full experiment ledger (78 experiments)” | VERIFIED | `research_loop/results.tsv:1-79` | 헤더 1줄과 실험 레코드 78개다. |
| §8 | “one regeneration command per figure” | VERIFIED | `scripts/report_figures.py:774-823`; `docs/ptcg/writeup/submission-2026-09-11/gallery-captions.md:5-11` | A–E에 대응하는 `cascade`, `dist`, `meta`, `matrix`, `convergence` 명령이 있다. |
| §8 | “Kaggle discussions 737125, 737435, 737107 and 738158” | VERIFIED | `docs/ptcg/research/2026-08-31-solution-scan.md:10,25,53,66` | 네 Discussion 식별자와 인용 대상이 일치한다. |

전체 판정: 최종 페어의 742.8/700.2, 54.0%/53.0%, 평균 725.0/719.2, 차이 5.8, 격차 19.8/75.6, 최종 43점 차이, 순위 1,611/6,807은 모두 재계산과 일치한다. 심사자 관점의 상위 3개 위험은 ① 실제 탐색 에이전트를 “deterministic/no tree search”로 설명한 구조적 모순, ② 코드에 초반·턴 번호 분기가 있는데 “no opening-specific/hard-coded turn numbers”라고 한 강건성 주장, ③ MIT 공개가 완료됐다는 추적 가능한 증거가 없고 `LICENSE`가 아직 untracked인 점이다.

Codex session ID: 01a08bb5-f23e-7201-a7f2-280703e258be
Resume in Codex: codex resume 01a08bb5-f23e-7201-a7f2-280703e258be
