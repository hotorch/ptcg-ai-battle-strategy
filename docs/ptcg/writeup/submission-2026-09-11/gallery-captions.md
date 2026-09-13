# Media Gallery — 확정 순서와 캡션 (2026-09-13 재검토 반영)

순서: **A → B → E → C → D**. 각 문단 전체를 해당 caption 필드에 입력한다.

## 1. A_cascade_surgeries.png

Figure A — The final decision pipeline and five tested changes. S1 and S5 are retained; S2–S4 were tested locally and on the ladder, then excluded from the final build. The fork's heuristic priorities are conditional and may be overridden by its 2-ply search; the diagram includes fork-supported alternatives that are absent from the final deck. S1 uses sampled hidden states, not guaranteed information. Source: candidates/h036_tempo_boss/main.py and fork_policy.py; policy base: Rozen's V10 (https://www.kaggle.com/code/romanrozen/strong-start-baseline-agent-v10-lb-950).

## 2. B_build_distribution.png

Figure B — One point per submission, grouped by experiment-family label; orange bars mark family means. Blue highlights identify the repeated identical-build comparisons H024B (n=7, range 133.7) and H036 (n=9, range 80.9). Other families can contain variants. Each value is the last rating recorded for that submission, at differing dates and game counts; ranges are descriptive, not confidence intervals. Source: submissions/rating_history.tsv. The final pair's longer trajectories are shown separately in Figure E.

## 3. E_convergence.png

Figure E — Left: one placement spike, submission 55515319. Right: the final H036 pair, submissions 55525772 and 55525773, through their last 1,000 recorded games ending 31 August. Thin lines show per-game ratings; thick lines show trailing means over up to 100 games. Mean ratings are 725.0 and 719.2 (difference 5.8); terminal ratings differ by 42.7. The 19.8 average and 75.6 maximum gaps align game counts, not timestamps. Source: Kaggle episode histories; these are two observed trajectories, not a controlled convergence experiment.

## 4. C_meta_convergence.png

Figure C — Shares of exported top-pool deck-games at 15 dates, not shares of the whole ladder. The lower panel uses TV = one half the sum of absolute share differences across six named archetypes plus Other. The external reference is the Limitless TEF–POR snapshot recorded on 14 August; asterisks mark Grimmsnarl and Slowking, approximated as zero because they were outside the reference's top 15. These assumptions limit interpretation. TV is 0.426 on 8/04, 0.370 on 8/15 and 0.393 on 8/21: the final observation does not establish continued convergence. The shaded interval marks reported matchmaking throttling. Sources: Daily Top Episodes (https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/discussion/709160), our dated observation log, and the motivating discussion (https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/discussion/735123).

## 5. D_seat_matrix.png

Figure D — H036 win rates by local opponent and seat: incumbent H024B, a replay-distilled opponent, and a rule-based counter-archetype proxy. The labels give sample sizes. The proxy's 100% results and the distilled gate's 85% aggregate offer limited discrimination; they do not establish performance against strong ladder pilots. The incumbent comparison is 30/60 overall, with a roughly 38–62% Wilson interval. Source: recorded runs 20260814-H036-01 and 20260814-H036-02. No opening-hand stratification was performed.

## 첨부

- `deck.csv`: 실제 H036 최종 제출 덱, 카드 ID 60줄. 루트 `deck.csv`로 교체하지 않는다.
- `deck-reference__v01__named-counts.csv`: 같은 덱의 카드명·수량·역할, 심사자 열람용. 카드 메타데이터 포함 자료이므로 Kaggle 첨부용으로만 사용하고 GitHub에 올리지 않는다.

Media Gallery와 덱 첨부의 단어 수 제외는 호스트 답변 735679·738657에서 확인했다. 이 캡션은 도표의 지표·표본·출처를 설명한다.
