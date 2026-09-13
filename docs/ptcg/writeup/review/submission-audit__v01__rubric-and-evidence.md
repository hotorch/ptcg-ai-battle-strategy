---
date: 2026-09-13
type: review
scope: submission-2026-09-11 body, gallery A–E, deck, handoff
status: local-corrections-verified
---

# 제출 직전 재심사

현재 자료 그대로 업로드하는 것은 권하지 않는다. 연구 기록은 강점이지만, 핵심 지표 계산과 모집단 귀속에 오류가 있어 기술적 타당성 점수를 잃을 수 있다. 이번 검토는 원문·그림을 수정하거나 Kaggle에 게시하지 않았다.

## 공식 배점과 전략

2026-09-13 Kaggle CLI로 Strategy 공식 페이지를 다시 읽었다. 웹 검색 도구는 페이지 본문을 반환하지 않아 공식 CLI의 pages 응답으로 확인했다.

- [Evaluation](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/overview/evaluation): 모델 70%, 덱 20%, 보고서 10%. 세부 질문별 가중치는 공개되지 않았다. 모델 질문 5개를 각각 14점이라고 계산하면 안 된다.
- [Description](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/overview/description): 중하위 래더 참가자도 깊은 분석·독창성·명료한 보고서로 높은 평가를 받을 수 있다고 명시한다. 다만 이것은 성능 점수가 무의미하다는 뜻이 아니다.

| 영역 | 현재 강점 | 남은 약점 | 우선 대응 |
|---|---|---|---|
| 모델 70% | 78개 실험, 회귀 검증, 두 좌석, 실패 공개 | TV 계산 오류, 타 에이전트 성적을 우리 것으로 서술, 개선 효과·강건성 과장 | 아래 P0/P1 수정 |
| 덱 20% | 손패→공격력이라는 명료한 전략 | 수량 선택 근거 부족, 덱 설명보다 래더 해명이 김 | 핵심 카드 수량·역할과 실제 한 턴 예시 강화 |
| 보고서 10% | 일관된 이야기, 자체 제작 도표 | B/E 수치·레이블 충돌, A 실행 흐름 부정확 | 원본 스크립트에서 도표 재생성 |

현재 순위나 수상 확률을 숫자로 예측할 근거는 없다. 마감 전 가장 효과적인 작업은 새로운 실험보다 기존 주장의 정확성을 높이고 게임 전략과의 연결을 명확히 하는 것이다.

## P0 — 업로드 전에 반드시 고칠 것

### 1. Figure C는 현재 총변동거리(TV)가 아니다

`scripts/report_figures.py:257`의 외부 기준은 여섯 아키타입 합계 52.9%다. `cmd_meta`는 여섯 항목에 대해서만 `0.5 * sum(abs(p-q))`를 계산한다. 기타 범주가 없고 재정규화도 없으므로 완전한 확률분포 간 TV가 아니다.

같은 입력을 사용하고 양쪽에 Other를 포함하여 직접 재계산했다:

| 날짜 | 기존 6항 부분합 | Other 포함 TV |
|---|---:|---:|
| 8/04 | 0.407463 | 0.426224 |
| 8/06 | 0.431205 | 0.478436 |
| 8/14 | 0.309174 | 0.404710 |
| 8/15 | 0.261097 | 0.370365 |
| 8/21 | 0.254215 | 0.393312 |

따라서 마감 후까지 거리가 계속 좁혀졌다는 결론은 유지되지 않는다. Other 포함 TV는 8/15보다 8/21에 커졌다. 이는 외부 기준의 미관측 아키타입을 0으로 놓는 기존 가정을 유지한 계산이며, 그 가정 자체도 불확실하다.

권장: Other를 포함해 계산·Figure C·본문을 함께 수정하고, 관측된 Dragapult 증가/Grimmsnarl 감소와 전체 분포 수렴을 분리한다. 전체 수렴 증명 대신 방향 예측의 확인으로 범위를 줄인다. 인게임 평형이 입증된 것이 아니므로 external equilibrium은 external reference distribution으로 바꾼다. Limitless TEF–POR, 8/14 수집, 상위 15위 밖 0 처리라는 비교 규약을 캡션에 명시한다.

### 2. §5의 패배 매치업은 최종 에이전트 성적이 아니다

`docs/ptcg/research/top-agent-observation.md` 결과 3은 **상위 풀 Alakazam 여러 파일럿의 1,129경기** 분석이다. Dragapult 24.9%(197경기), Slowking 29.2%(24경기)를 `Our two worst matchups`라고 쓰면 우리 H036의 직접 측정으로 오해된다.

권장 문구:

> In the exported top-pool Alakazam sample, win rates were 24.9% against Dragapult (n=197) and 29.2% against Slowking (n=24); these are archetype-level observations, not tests of our final agent.

40.3% 역시 우리 최종 모델의 실전 승률 예측으로 제시하면 안 된다. 원기록은 8/15 관측 점유율 재가중이므로 `forecast field`에도 시간상 문제가 있다. 사용한 승률·가중치의 모집단을 밝히고 시나리오 추정으로 한정하거나, 계산 근거가 불명확하면 삭제한다. 실제 최종 페어 53–54%는 다른 상대 풀이라 직접 비교되지 않는다는 설명이 필요하다. §6의 `Both losing matchups`도 함께 수정한다.

### 3. Figure B와 E가 본문과 충돌한다

- B: 별표 범례는 `after 1,000 games each (gap 8.3)`라고 되어 있다. 현재 본문의 최종 레이팅 차이는 42.7, 1,000경기 평균 차이는 5.8이다. `_final_pair()`가 `pair_convergence.tsv` 마지막 스냅샷을 읽어 오래된 자료가 남는 구조다. 최신 ladder JSON의 최종 레이팅을 쓰거나 별표를 없애고 E에서만 수렴을 다루는 편이 명료하다.
- E: `same-moment gap`은 실제 동일 시각 비교가 아니다. 코드는 경기 순번을 맞춘다. `gap at matched game counts`로 수정한다.
- B: 제목은 전체가 동일 코드 반복 제출처럼 읽히지만 그룹은 해시가 아니라 description의 실험 접두어로 묶인다. H010 등은 변형이 섞일 수 있다. 동일 패키지가 확인된 H024B/H036만 동일 코드라고 한정하고, 나머지는 실험 계열로 표시한다.

### 4. Figure A의 S1 설명이 코드보다 강하다

그림은 `only after 2-of-2 fresh re-verification`이라고 쓰지만 `_lethal_probe()`는 최초 두 결정화에서 같은 행동에 표가 두 개 모이면 추가 fresh verification 없이 채택한다. 추가 검증은 `count < 2`일 때만 한다. `two supporting determinizations, with extra verification when needed`처럼 실제 로직을 설명해야 한다. 이것도 숨겨진 정보 전체에 대한 승리 보장은 아니다.

그림의 Rozen 분기에는 본문에 추가된 2-ply 탐색이 빠져 있다. 탐색 결과가 우선순위 선택을 덮어쓸 수 있다는 점과 리썰 실패 시 포크로 돌아가는 경로를 보여준다.

## P1 — 기술적 설득력과 덱 점수 강화

1. **비개선과 개선 입증을 대칭적으로 표현한다.** S5 미러 30/60과 회귀 65/21,975는 승률 향상을 입증하지 않는다. 회귀 검증은 기록된 관측에서 변경 범위를 확인한다. `improved by five` 대신 `tested five changes; retained two`를 쓰고, S5는 국소 동작 수정이며 전체 승률 상승은 확인되지 않았다고 구분한다. S2–S4도 제출은 했으므로 `never shipped`보다 `excluded from the final build`가 정확하다.
2. **강건성 단정을 낮춘다.** `No initial-state dependence`는 좌석별 테이블이 없다는 사실로 증명되지 않는다. `Seat checks and limitations`로 바꾸고 초기 손패 유형별 검증은 없었다고 밝힌다. 43.3% 대 56.7%, 각 30경기는 동등성 입증이 아니다. 95% CI ±3.1은 독립 베르누이 가정의 근사치이며 상대 구성 변화·시계열 의존을 반영하지 않는다.
3. **통계적 표현을 바로잡는다.** `decomposed the variance`는 정식 분산분해가 아니다. `documented three sources of rating variation`으로 바꾼다. `rating inflation rejected`는 `no clear evidence of inflation in this small sample`, `expected value zero`는 `no demonstrated lasting benefit` 정도가 증거에 맞다. 서로 다른 빌드의 단기 범위 134와 두 장기 평균 차이 5.8은 같은 통계량이 아니다.
4. **예측 시점을 드러낸다.** 8/14 예측 이전인 8/04의 6.3%부터 전부 예측 성과처럼 연결하지 않는다. 8/14에 기록한 방향 예측과 그 이후 실현을 따로 보여준다. 타 참가자의 수렴 관찰에서 출발했다는 기록도 있으므로 독창성은 자체 계량·의사결정 적용에 둔다.
5. **외부 사례를 줄이고 덱에 단어를 배정한다.** 삭제된 글의 +200점 사례와 재제출 통계는 독자가 검증하기 어렵고 우리 수치와 중복된다. 이 부분을 줄여 실제 덱의 수량·역할을 설명한다. 특히 Dunsparce는 2장+1장의 두 카드 ID 합계 3장, Dudunsparce 4장, 기본 Psychic 2장+Telepath 4장임을 알기 쉽게 표시한다. 수량이 최적이라고 주장할 근거는 없으므로 채택 이유와 미검증 한계를 분리한다.
6. **S5에 작은 수치 예시를 넣는다.** 예: 손패 8장·140 HP 벤치 타깃이면 Boss 사용 후 7×20=140, 손패 7장이면 사용 후 6×20=120이라 승격하지 않는다. 도달 가능성·에너지 등 다른 가드도 충족한 가정임을 명시한다. 새 실험 없이 카드 선택·정책 정합성을 보여줄 수 있다.
7. **첨부 덱을 사람이 읽을 수 있게 한다.** 현재 deck.csv는 60줄의 카드 ID다. 제출 파일로는 맞지만 덱 점수 심사에는 불편하다. 카드명·수량·역할을 정리한 간결한 덱 표를 추가 자료로 준비하는 것이 유용하다. 원래의 deck.csv는 유지한다.

## 규정·핸드오프 확인

- [Rule 3.6.b](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/rules)는 자발적으로 코드를 공개할 경우 해당 대회 포럼 **또는 노트북**을 통해 공유하도록 명시한다. 포럼 공유를 마무리하는 방향은 타당하다. 반드시 새 토픽만 가능한 것은 아니며, GitHub 링크만으로 조항을 완전히 충족하는지에 대한 별도 호스트 확인까지 얻은 것은 아니다. 이번 요청은 검토이므로 공개 게시하지 않았다.
- [호스트 738657 답변](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/discussion/738657): 덱 CSV 첨부 허용, 그림·표 내부 텍스트 제외 확인. 그림을 추가 본문을 숨기는 용도로 쓰지 말라는 취지도 있다.
- [호스트 735679 답변](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/discussion/735679): Media Gallery는 2,000단어에 포함되지 않는다.
- [호스트 736603 답변](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/discussion/736603): 9/12에 보드 상태는 공식 visualizer 사용 권고. 현재 다섯 차트에서 새 카드 아트나 보드 재현은 보이지 않았다. 이를 Pokémon Elements가 전혀 없다는 뜻으로 확대하면 안 된다.
- 본문은 로컬 `wc -w` 1,999. 최종 폼 카운터는 편집 후 별도로 확인해야 한다.
- §8 `which opens at the hackathon's close`는 핸드오프의 이미 공개 완료 상태와 모순된다. 공개 상태 확인 후 시제 수정 및 클릭 가능한 링크로 바꾼다.
- 패키지 README에는 새 Writeup 생성·draft 삭제라는 오래된 절차가 남아 있다. 기존 제출 편집을 지시하는 HANDOFF와 통일해야 한다.
- Save만으로는 안 되고 Submit/Update 후 SUBMITTED 확인이 필요하다. 이번 검토에서 로그인된 UI의 현 제출 상태·Track·팀 동일성은 직접 확인하지 않았다.
- `kaggle_ops.py status`에서 최종 두 제출 COMPLETE, 742.8/700.2를 재확인했다. 이것은 Strategy Writeup의 SUBMITTED 확인을 대신하지 않는다.

## 권장 실행 순서

1. TV 계산·모집단 귀속·통계적 과장부터 수정한다.
2. 그림 A/B/C/E의 소스와 출력·캡션을 함께 정합화한다.
3. 외부 사례를 압축한 공간에 덱 수량·S5 숫자 예시를 넣는다.
4. 본문과 그림 교차 검증 및 단어 수 확인 후 기존 제출을 업데이트한다.
5. Submit 상태를 확인하고, 사용자 승인 후 코드 공유 글을 게시한다.


## 2026-09-13 수정 완료 기록

후속 사용자 지시에 따라 위 검토를 반영했다. 앞부분은 수정 전 진단 기록이다.

- body.md 1,878단어, 8개 섹션. 덱·S5 수치 예시 보강, 모집단 귀속 정정, 40.3% 추정 제거, 개선·강건성 단정 완화.
- report_figures.py의 TV는 Other를 포함한다. 누락 재발을 잡는 tests/test_report_figures.py 추가 및 통과.
- A/B/C/E 재생성 및 육안 확인, D 재생성으로 기존 좌석 결과 확인. gallery 복사본 5개와 생성 원본의 바이트 일치 확인.
- 첨부 deck.csv를 H036 후보 덱과 대조. 이름·수량 CSV 21행, 합계 60장과 ID별 수량 일치. 메타데이터 첨부는 Git에서 제외.
- 캡션 전문과 HANDOFF 내 캡션 일치, README 절차 정리. 원본 코드·본문 변경 내역은 로컬에 있으며 원격 push 미실행.
- TV 0.426/0.370/0.393과 최종 두 궤적 각 1,000경기, 평균 725.0/719.2, 마지막 격차 42.7 재계산 통과.
- Python compile, TV 체크, 테스트 파일 Ruff, git diff --check 통과.
- Kaggle 폼 단어 수·SUBMITTED 상태·업로드 결과는 업로드 세션에서 확인해야 한다. 현재 세션은 업로드/공개 게시를 하지 않았다.
