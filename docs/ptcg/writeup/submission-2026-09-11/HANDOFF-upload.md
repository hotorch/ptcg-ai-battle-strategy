> 2026-09-13 실행 기록: 수정본 Update Submission 후 Submitted! 확인. 이미지 제목은 255자 제한이므로 짧은 설명을 쓰고 gallery-captions.md 전문을 첨부했다. 아래는 실행 전 절차 기록이다.

# 핸드오프 — 수정본 업로드 (2026-09-13 재검토 반영)

기존 초안을 그대로 올리지 않는다. 이 폴더의 **수정된 본문과 그림·캡션**을 사용한다.
마감 기록: **2026-09-13 23:59 UTC (= 9/14 08:59 KST)**. 업로드 시작 시 Kaggle UI 마감도 확인한다.
현재 요청은 수정본 준비까지였으므로 Kaggle/GitHub 업로드와 공개 게시를 실행하지 않았다.

## 0. 대상과 파일

- 계정: `aisamhottman`.
- **기존 Writeup을 Edit**: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/writeups/new-writeup-1786172403257
- 제목 **The Ladder as the Object of Study** 유지. 기존 subtitle·Track 확인/유지.
- 9/10 SUBMITTED 기록이 있다. 새 Writeup을 만들지 않는다.
- 파일 기준 폴더: `docs/ptcg/writeup/submission-2026-09-11/`.
- 본문 `body.md`: 로컬 공백 구분 **1878 words**, 8개 섹션. 최종 폼 카운터 ≤2,000 재확인.
- 덱은 **이 폴더의 deck.csv**. 루트 deck.csv는 다른 덱이다. 최종 에이전트는 `candidates/h036_tempo_boss/`.
- 빈 New Writeup draft 2개는 이번 작업에서 건드리지 않는다.
- 공개 저장소: https://github.com/hotorch/ptcg-ai-battle-strategy (9/13 PUBLIC 확인).
- 구 저장소 `hotorch/Kaggle-The-Pok-mon-Company`는 비공개 유지. 과거 Competition Data가 있으므로 공개하지 않는다.

## 1. 본문 교체

Edit → Project Description 전체를 `body.md`로 교체한다. Preview에서 8개 섹션·코드 예시·링크 렌더링을 확인한다.

수정 확인용: §5에 **0.426 / 0.370 / 0.393**, `and Other`, `not our final agent`가 있어야 한다.
이전 수치 0.407→0.261→0.254와 40.3% 기대승률은 사용하지 않는다.

## 2. Media Gallery

기존 이미지가 있으면 이전 것을 제거/교체하여 중복 없이 **5장**, 순서 **A → B → E → C → D**로 만든다.
아래 각 문단 전문이 캡션이다. 그림 파일은 `gallery/` 안에 있다.

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

## 3. 덱 첨부

Attachments에 아래 두 파일을 추가한다:

1. `deck.csv`: H036 최종 제출과 동일한 60장 카드 ID.
2. `deck-reference__v01__named-counts.csv`: 같은 60장, 카드명·수량·역할 21행의 열람용 표.

카드명 표는 Kaggle 첨부용이다. GitHub에 추가하지 않는다. `.gitignore`에 등록되어 있다.
호스트 738657은 덱 CSV 첨부와 단어 수 제외를 허용했다. 735679는 Media Gallery의 단어 수 제외를 확인했다.

## 4. Submit 및 검증

- Preview: 제목, 8개 섹션, 140HP 예시, 그림 5장과 캡션, 덱 2개, 링크 확인.
- **Submit 또는 Update까지 누른다. Save만 하면 안 된다.**
- 목록에서 **SUBMITTED 배지**를 확인하고 스크린샷을 남긴다.
- 다시 열어 수정된 §5와 그림 B(8.3 별표 없음), C(TV including Other), E(matched game counts)를 확인한다.
- 자동화 결과에 제출 상태, 폼 단어 수, 첨부 개수, 스크린샷 경로를 남긴다.

## 5. 공개 분석 코드 동기화

수정된 `scripts/report_figures.py`와 `tests/test_report_figures.py`는 현재 로컬에만 있다.
업로드 작업을 승인받아 실행하는 세션에서 공개 저장소의 분석 코드도 이 수정본으로 동기화해야 한다.
현재 origin은 공개 저장소지만 push 전 다시 확인한다. 새 커밋을 만들고 amend/force-push는 하지 않는다.

동기화 대상은 이번 수정의 코드·본문·캡션·그림·문서와 `.gitignore`다. **무차별 git add . 대신 diff를 검토하여 지정한다.**
카드 메타데이터 CSV, raw/replay 데이터, context 캐시, 실험 run JSON은 추가하지 않는다.
`tests/test_report_figures.py` 통과와 공개 코드의 Other 항 포함을 확인한다.
Writeup 마감이 임박하면 우선 1–4를 완료해 제출 상태를 확보한다.

## 6. Rule 3.6.b 공유 글 — 공개 게시 승인 후

규칙은 코드 공개 시 해당 대회 포럼 또는 노트북에서도 공유하도록 한다.
이 단계의 공개 게시 승인이 아직 없으면 아래 완성된 초안에 대해 사용자 승인을 받은 뒤 게시한다.
이미 동일한 공유 글이 있으면 중복 생성하지 않는다.
위치: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/discussion

**제목**: `[MIT] Solution and evaluation code: The Ladder as the Object of Study`

**본문**:

```text
Sharing our solution and evaluation code under MIT:
https://github.com/hotorch/ptcg-ai-battle-strategy

The final agent is in candidates/h036_tempo_boss/ (the repository-root deck is a different research baseline). It builds on Rozen's public V10 policy, with our selective lethal-search wrapper and a guarded Boss's Orders priority.

The repository includes the ledger of 78 experiments, both-seat evaluation scripts, and figure-generation code. Seven submissions of one identical build spanned 133.7 rating points. We treated that as a reason to require more evidence from individual submission improvements, not as a significance threshold.

Of five tested changes, two remained in the final build. The others were tested on the ladder and excluded. Our final pair finished at 742.8 and 700.2; the S5 match tests did not establish an overall win-rate gain.

The final review also corrected the metagame chart: total-variation distance now includes Other. The data support a directional Dragapult forecast, but not continued convergence to an external equilibrium.

Replay-derived inputs and the named-card attachment are omitted from the public repository. The README describes omitted inputs and regeneration steps using participants' own competition data. Pokémon Elements are not licensed as our own work.

Policy base: https://www.kaggle.com/code/romanrozen/strong-start-baseline-agent-v10-lb-950
```

## 완료 체크리스트

- [ ] 기존 Writeup 본문 교체, 폼 단어 수 ≤2,000
- [ ] 그림 5장 A→B→E→C→D, 새 캡션 5개
- [ ] H036 deck.csv + 이름·수량 표 첨부
- [ ] Submit/Update → SUBMITTED 재확인 + 스크린샷
- [ ] 공개 분석 코드 수정본 동기화 확인
- [ ] 승인 후 포럼 공유 글 게시, 게시 URL 기록
