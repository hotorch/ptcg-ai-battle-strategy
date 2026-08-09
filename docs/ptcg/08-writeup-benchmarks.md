# Writeup 벤치마크 (2026-08-08 리서치)

시뮬레이션 대회 우승 writeup 6편 전문 분석 + 심사형 writeup 대회 분석(추가 예정) + 현 대회 참가자 공개 방법론(추가 예정).

## A. 시뮬레이션 대회 우승작 6편 — 구조 분석

| 작성자 | 대회/순위 | 길이 | 그림 | 구조 특징 |
|---|---|---|---|---|
| [Toad Brigade](https://www.kaggle.com/competitions/lux-ai-2021/writeups/toad-brigade-toad-brigade-s-approach-deep-reinforc) | Lux AI 2021 1위 | ~2,900w | 3개(3패널 리플레이 합성) | 피벗 서사 선두, 계층적(개요→세부), 해석 그림 |
| [ry_andy_](https://www.kaggle.com/competitions/lux-ai-season-2/writeups/ry-andy-1st-place-solution) | Lux AI S2 1위 | ~2,000w | 1 스크린샷 + 코드 2 | 단일 전략 테제, 시그니처 기법 명명("ice conflicts"), 약점 매치업 공개 |
| [ttvand](https://www.kaggle.com/c/halite/discussion/183543) | Halite IV 1위 | ~3,800w | 0 | "22개 제출 중 16개가 1위였을 것" — 강건성을 한 문장 수치로 |
| [Harm Buisman](https://www.kaggle.com/competitions/kore-2022/discussion/340035) | Kore 2022 1위 | ~1,400w | 0 | 버전 원장(V118/127/146), 상속 프레임워크 + 자기 혁신 2개 구조 |
| [Goosebumps](https://www.kaggle.com/competitions/hungry-geese/writeups/goosebumps-goosebumps-solution-2nd-place) | Hungry Geese 2위 | ~3,300w | 수식 2 | 리플레이 필터링·held-out·리그레션 테스트 — **우리 증류 트랙의 직계 사촌** |
| [c-number](https://www.kaggle.com/competitions/llm-20-questions/writeups/c-number-1st-place-solution) | LLM 20 Questions 1위 | ~1,600w | 3 | 결과표를 방법보다 먼저, **제출 2개를 내장 아블레이션으로 사용** |

## B. 반복 패턴 8개 (전 편 공통)

1. **피라미드 구조**: 테제 한 문장 + 핵심 베팅을 첫 두 문단에, 세부는 하강, 잔여는 코드 링크로.
2. **시그니처 혁신에 이름 붙이기** — originality 점수는 "이름 붙은 아이디어 1개"가 나른다. 우리 후보: "distilled-opponent gate"(meta0d 비포화 게이트), "reply-horizon search".
3. **강건성은 형용사가 아니라 수치 한 문장**: "22개 중 16개가 우승권" 식. 우리 버전: "9세대 전 제출의 래더 궤적 + 세대마다 게이트 통과 이력".
4. **실패·피벗 서사 + 메커니즘 설명**: 실패의 '왜'를 설명해야 성공이 믿긴다. 우리 재료: 스케일링 무효 3건, 관측 로지스틱의 인과 한계, H-017f 트레이드오프 기각.
5. **약점 매치업 명시적 공개**: meta0 0-5 고전과 그 진단(핸드 체인 절반 실행)을 숨기지 말고 서사의 축으로.
6. **평가 방법론 자체가 콘텐츠**: 내부 건틀릿, 리플레이 리그레션 테스트, 표본 규율. 우리 gauntlet.py·비포화 게이트 발명이 여기 직결.
7. **그림은 장식이 아니라 해석**: 보드상태+가치곡선 합성, 소형 실례 표, 도구 스크린샷. **아키텍처 다이어그램은 아무도 안 씀** — outline v0의 "파이프라인 다이어그램"은 재고.
8. **모든 문단에 수치**: 초/턴, 노드 수, 반복 횟수, 비용 대비 효과.

## C. 즉시 차용할 3개 전술

1. **c-number의 내장 아블레이션**: 최종 2슬롯을 "best + 핵심 메커니즘 제거판"으로 구성하면 레이팅 격차 자체가 핵심 아이디어의 측정값이 된다. → 8/14 슬롯 결정과 연동해 검토 (단, 순위 손해 트레이드오프 있음 — 차선: 과거 세대 제출들의 래더 수렴치가 이미 자연 아블레이션).
2. **Toad Brigade의 3패널 게임 순간**: 보드상태 + 에이전트 행동 분포 + 승률 곡선 1경기 합성 그림. 우리 replay 데이터로 제작 가능.
3. **ttvand의 한 문장 강건성 스탯**: 좌석 교대·아키타입별 성적을 한 문장 수치로 압축해 서두에.

## D. 권장 스켈레톤 (에이전트 종합안, outline.md v1에 병합)

1. Approach at a glance (~150w): 테제 + 최종 성적 + 헤드라인 수치 표 3행.
2. The deck and its key cards (~250w + 그림 1): **Deck Score 20%는 벤치마크 대회들에 없던 항목 — 묻히지 않게 독립 섹션 필수.**
3. How the agent decides (~400w + 의사코드): 증류 프라이어 → 결정화 탐색 → 응수 모델 계층. 시그니처 기법 명명.
4. What the agent learned / worked example (~250w + 3패널 그림).
5. Consistency under repeated play (~250w + 그림): 건틀릿 매트릭스, 양좌석 승률+표본수.
6. Robustness and weak matchups (~250w + 그림): 아키타입별 성적, 최악 매치업 명명과 진단·패치 일화.
7. What didn't work (~200w): 3개 불릿, 각각 메커니즘.
8. Evaluation methodology (~150w): 비결정론 엔진 → 양좌석 반복, 비포화 게이트, 버전 원장.
9. Conclusion + code (~100w).

합계 ~2,000w, 그림 5개.

## F. 심사형(judge-scored) 대회 우승작 6편 — 채점 대응 기술

읽은 실물: Meta Kaggle Hackathon 우승([Kaggle Chronicles](https://www.kaggle.com/competitions/meta-kaggle-hackathon/writeups/kaggle-chronicles-15-years-of-competitions-communi), ~6,400w/그림 25), Gemini Long Context 우승 2편([FrameCut](https://www.kaggle.com/code/kyle1373/framecut-a-natural-language-video-editor), [KeepTrack](https://www.kaggle.com/code/mrdbourke/keeptrack-use-gemini-to-keep-track-of-anything)), 2023 Kaggle AI Report 우승 3편([Towards Green AI](https://www.kaggle.com/code/iamleonie/towards-green-ai), [How to Win a Kaggle Competition](https://www.kaggle.com/code/thedrcat/how-to-win-a-kaggle-competition) ~2,400w — **2,000단어 캡의 최근접 유사물**, [Tabular Pipeline](https://www.kaggle.com/code/rhysie/learnings-from-the-typical-tabular-pipeline)).

**핵심 구조적 사실: 심사형 Kaggle 루브릭은 항목별 체크리스트 채점이다.** 우승작들은 채점자가 줄 단위로 점수 매기기 쉽게 쓰여 있다.

1. **루브릭 언어를 섹션 제목에 미러링** — Monigatti는 심사 질문을 문자 그대로 소제목으로 사용. 우리도 "Robustness", "Deck Rationale", "Originality" 등 채점 언어를 제목에.
2. **작은 배점도 명시적으로 사냥**: KeepTrack은 5점짜리 항목(컨텍스트 캐싱)에 측정 차트 섹션을 배정. → Deck 20%는 데이터 기반 독립 섹션, Report 10%는 의도적 그림 설계.
3. **두 정권(two-regime) 강건성 패턴**: 같은 행동을 두 조건에서 벤치마크(FrameCut의 short/long). → 우리: 좌석 × 아키타입 소형 다중 그림 1개.
4. **깊이는 레이어링**: writeup은 척추, 재현 노트북/부록은 아래층. 서두에 "모든 그림은 X에서 재현 가능" 한 문장 = 재현성 점수 획득.
5. **제목이 곧 발견**(Kłeczek): "Search on crystallization turns beats a value net" 식 헤딩 — 2,000단어 압축의 최고 장치.
6. **훅+TL;DR 100단어 이내**: 배경 설명으로 시작 금지. 문제·접근·독창성을 첫 문단에.
7. **모든 주장 옆에 수치/그림 1개** — Meta Kaggle 루브릭 40점이 "주장을 뒷받침하는 증거".
8. **정직 섹션("Tried and failed")** = 전문가 심사자에게 강건성 증거로 읽힘.

Don'ts: 시간순 실험 일지 금지(주장 단위로 조직), 심사자가 아는 배경 설명 금지, 캡션 없는 그림 금지, 재현성 링크를 끝에 묻지 말 것.

## E. 현 대회 공개 지형 (08-08 스캔)

### 고득점 공개 방법론 — 확인된 것

- **Masami(=tomatomato 추정, note.com + Kaggle)**: 피크 1341/세계 2위(6월 말), Starmie/Froslass **순수 룰베이스**. 3모드 구조(일반/매치업별/**리썰 모드** — 이번 턴 승리 라인을 전방 탐색으로 검증 후 재생). 핵심 혁신: **프라이즈 카드 추론 트래커**(덱리스트−가시 카드=잔여가 프라이즈 수와 일치할 때만 확정, 아니면 unknown) — 탐색이 불가능한 라인을 찾는 것을 방지. "틀린 프라이즈 추론은 추론 없음보다 나쁘다". [노트북](https://www.kaggle.com/code/masamikobayashi/prize-card-tracking-1300-starmie), [note 포스트](https://note.com/glad_puma5862/n/nd72fdc4821cd)
- **sue124**: 2일차 5위 Alakazam 룰 플레이북 전면 공개. [노트북](https://www.kaggle.com/code/ryotasueyoshi/rule-based-not-psychic-alakazam-best-5th)
- **Roman Rozen "Baseline Agent V10 | LB 950+"**: **공개 포크 가능한 ~950 Alakazam** (가중치 파라미터화 + memetic 튜닝). [노트북](https://www.kaggle.com/code/romanrozen/strong-start-baseline-agent-v10-lb-950) — 래더의 Alakazam 동질화 원인이자, **우리 634가 공개 베이스라인보다 낮다는 뼈아픈 사실.**
- **Takibi Lab**: 로컬 검증 통과가 프로덕션 회귀를 부른 사례("새 로직의 트리거 조건이 로컬 상대 풀에서 발생 안 함") → 제출 전 head-to-head 검증 채택. 우리 로컬-래더 괴리 문제의 외부 corroboration. [note](https://note.com/takibisan/n/n2fa2106cadb5)
- **RL/MCTS는 공개 사례 전부 저조**: TomBombadyl repo(RL+MCTS v5 580μ < 룰 880μ), 공식 샘플 파생들. "룰+표적 탐색+메타 적응"이 공개 증거상 승리 공식.
- **상위 10팀(Majkel1337 등)은 방법 비공개** — 마감 전 함구 중. 복사할 것도, 비교당할 자료도 없음.

### 유용한 메타 분석 (인용 후보)

- [busyaprime "What actually wins on the ladder"](https://www.kaggle.com/code/busyaprime/what-actually-wins-on-the-ladder): 아키타입 점유율·Wilson CI 매치업 그리드·**필드 가중 기대 승률**. 우리 mine_episodes 분석과 상호 검증 가능.
- [MYSO 점수대별 덱 메타](https://www.kaggle.com/code/myso1987/ptcg-ai-battle-leaderboard-deck-meta-by-score-band) (8/7 갱신).

### 전략적 함의

1. **에이전트 개선 레버 2개 수입 가능**: (a) 리썰 모드 — 승리 라인 전방 탐색 검증은 우리 탐색 구조에 자연 결합, (b) 프라이즈 추론 — 결정화 샘플링의 은닉 정보 모델 개선. 공개 기법이므로 인용하고 개량하면 originality 손상 없음.
2. 공개 950 베이스라인의 존재는 "리더보드 성적" 항목에서 우리 위치를 더 아프게 만든다 — 남은 기간 래더 레버는 이 두 수입 기법에 집중하는 것이 방어 논리(공개 지식 흡수+개량)도 서사도 좋다.
3. Writeup에서 "공개 증거상 RL 저조, 룰+탐색 우세" 지형을 인용하면 우리 하이브리드(증류 프라이어+탐색+학습 가치)의 위치 설정이 선명해진다.
