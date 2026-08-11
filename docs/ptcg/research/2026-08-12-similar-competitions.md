# 유사 대회·상위 솔루션 리서치 (2026-08-12)

점수 정체(H-024b ~782 밴드) 타개를 위한 외부 사례 조사. 서브에이전트 4기 병렬 리서치 결과 종합.

- 조사 축: ① 카드게임 AI 대회(Hearthstone/Tales of Tribute), ② Kaggle 시뮬 대회 상위 솔루션·엔드게임 전략, ③ 포켓몬 배틀 AI 문헌, ④ 본 대회 최신 공유 스캔.
- 종합 결론과 액션 항목은 문서 말미 "종합: 업그레이드 후보" 참조.

---

## ① 카드게임 AI 대회 (Hearthstone / Tales of Tribute / LOCM)

### 우승 접근법

- **Hearthstone AI Competition (2018–2020)**: 2020 Premade 트랙 Top 3 전원이 **Dynamic Lookahead(DL)** 계열 — 턴 내 행동 시퀀스를 시간 예산에 맞춰 동적 깊이로 탐색하고 **턴 종료 상태를 휴리스틱 평가함수로 채점**. NN 없음, CPU 저비용. "얕은 탐색 + 좋은 평가함수"가 3년 연속 우승 라인. 시간 초과 실격 팀 다수 → 시간 안전마진 중요. Dockhorn의 bigram 상대 핸드 예측 + 예측별 MCTS 앙상블도 승률 향상 입증.
- **Tales of Tribute AI Competition (2023–2024 연속 우승, Ciężkowski & Krzyżyński)**: **루트 병렬 MCTS를 결정화 시드 단 5개로 운영** — 시드마다 트리 1개, 예산 5등분, 최종 수는 트리 평균 점수로 선택. 평가함수는 **early/mid/late 3단계 가중치 분리**. 턴당 10s/256MB의 저자원 환경에서 2년 연속 우승.
- **LOCM/Strategy Card Game AI (2019–2021 최강 Coac)**: 깊이 3 미니맥스 + 알파베타 + 휴리스틱 가지치기(94% 승률). 공통 요소: **lethal 수 우선 단락, 행동 순서 정규화로 분기 축소, 얕은 깊이 + 강한 평가함수**. 2022 ByteRL(딥 RL)이 우승했으나 대규모 인프라 전제.
- **학술(ISMCTS/PIMC)**: 일반 카드게임에서 ISMCTS는 결정화 UCT와 동급(Dou Di Zhu) → **전면 ISMCTS 전환 불필요**. 결정화 수는 수십 개에서 포화하며 ToT 우승팀은 5개로 충분. PIMC는 disambiguation 높은 카드게임에 적합 — PTCG는 적합 영역.

### 이식 가능 요소 (우선순위·비용·리스크)

| # | 항목 | 구체안 | 비용 | 리스크 |
|---|------|--------|------|--------|
| 1 | **결정화 3–5개 앙상블 투표** | lethal-window 탐색을 3–5 시드 결정화로 돌리고 평균 점수/다수결 선택. lethal 확정은 "모든 결정화에서 lethal" AND 규칙으로 보수화 | 낮음 | 시드당 깊이 감소 |
| 2 | **탐색 창 확대** | prize≤3-4 조건을 단계 완화(상대 액티브 KO 가능 시, 분기 수 임계 이상 시) + 턴 종료 평가함수 A/B | 중간 | 시간 초과 — 예산 80–85% anytime 컷 + 룰 폴백 필수 |
| 3 | **단계별 평가 가중치** | 남은 프라이즈 수를 단계 변수로 early/mid/late 가중치 분리. 증류 선호표도 단계별 분리 집계 가능 | 낮음 | 경계 과적합 — full 게이트 |
| 4 | **상대 덱 추론 → 결정화 샘플러** | deck-stats 시그니처로 관측 플레이→아키타입 분류→미공개 카드를 해당 분포에서 샘플. co-occurrence 표는 오프라인 생성·동봉 | 중간 | 오분류 시 균등 샘플링 폴백 |
| 5 | **행동 공간 가지치기** | lethal 단락 최우선, 순서 무관 조합 정규화, 명백 열등수 필터 | 낮음 | 정답 수 오제거 — held-out 일치율 회귀 검증 |
| 6 | **시간 안전마진 감사** | 예산 80–85% anytime 컷 + 항상 유효한 폴백 수 | 매우 낮음 | 없음 |

**하지 말 것**: 전면 ISMCTS 전환, 딥 RL(단일 tarball·CPU 제약과 충돌).

**탐색 vs 규칙의 경계 증거**: 어그로/직선 플랜은 규칙으로 충분, 보드 분기 복잡도가 높거나 후반일수록 탐색 이득 증가. lethal 검증은 모든 우승작의 공통 요소 — 우리 lethal-window는 정석이고 확장 방향(창 넓히기)이 문헌과 일치.

### 링크

- [HS AI Comp 2020 결과 슬라이드](https://hearthstoneai.github.io/files/slides/2020-Results-Hearthstone-AI-Competition.pdf) / [공식](https://hearthstoneai.github.io/) / [arXiv 1906.04238](https://arxiv.org/abs/1906.04238)
- [Dockhorn 상대 핸드 예측](https://adockhorn.github.io/files/slides/Predicting%20Opponent%20Moves%20for%20Improving%20Hearthstone%20AI.pdf)
- [ToT AI Comp arXiv 2305.08234](https://arxiv.org/abs/2305.08234) / [대회 아카이브(에이전트 코드 공개)](https://github.com/ScriptsOfTribute/ScriptsOfTribute-CompetitionsArchive)
- [LOCM 총결산 arXiv 2305.11814](https://arxiv.org/html/2305.11814)
- [PIMC 성공 조건 (AAAI 2010)](https://webdocs.cs.ualberta.ca/~nathanst/papers/pimc.pdf) / [ISMCTS (2012)](https://eprints.whiterose.ac.uk/id/eprint/75048/1/CowlingPowleyWhitehouse2012.pdf) / [EPIMC arXiv 2408.02380](https://arxiv.org/abs/2408.02380)

---

## ② Kaggle 시뮬레이션 대회 상위 솔루션·엔드게임 전략

### 룰 vs 학습의 승부처 (대회별)

| 대회 | 우승 접근 | 판정 |
|---|---|---|
| Halite IV (2020) | 1위 Tom Van de Wiele(ex-DeepMind): **순수 룰 기반** (DL 실험 후 폐기). 협동 사냥·기지 방어·역할 할당 | 룰 압승 |
| Halite I–III | 전 시즌 수작업 휴리스틱 우승 | 룰 승 |
| Lux AI S1–S3 | S1/S2/S3 모두 대규모 딥 RL 우승 (S3 1위는 8×H100 수일 학습, 최고 룰 기반 20위). 골드권 가성비 루트는 **상위 리플레이 모방학습(IL)** | RL 승 (빠른 시뮬레이터 + 대규모 연산 전제) |
| Kore 2022 | 1위: **리더보드 상위 5개 제출 리플레이 ~2억 튜플 IL** — 모방 대상(룰 봇)을 오히려 이김 (전문가 평균화 + 대실수 제거 효과) | IL 승 |
| ConnectX | negamax/비트보드 + 사전계산 오프닝북 | 탐색+테이블 승 |
| RPS (2021) | 1위: 전략 앙상블 + 밴딧 메타 선택기 | 메타 앙상블 승 |
| Santa 2020 | 리더보드 에피소드 스크래핑 → 지도학습 | 리더보드 마이닝 승 |
| Hungry Geese | 상위권 = RL 정책망 + 얕은 lookahead + 안전규칙 하이브리드; 3위는 BC+수정 MCTS | 하이브리드 승 |

**종합 패턴**: 시뮬레이터가 빠르고 연산이 넉넉하면 RL, **엔진이 느리거나 RNG 복제 불가·CPU 제한이면 룰+표적 탐색이 이긴다** → PTCG는 후자 = 현 스택(룰+리썰 탐색+증류 테이블)이 역사적으로 올바른 차선. top-20→top-3 격차의 실체는 알고리즘 교체가 아니라 (a) 상대 상호작용 국면의 정밀도, (b) **대실수 제거**, (c) 막판 메타 적응.

### 엔드게임(레이팅/제출) 전략 사례

1. **분산 낚시는 보편 전략** — RPS 1위는 "제출 후 2판 지면 재제출" 루프를 명시적으로 사용.
2. **수렴 시간 확보용 조기 제출** — 상위 레이팅일수록 매치가 많이 잡히는 구조(우리 대회 ~8배)는 복리. 늦게 낸 인스턴스는 수렴할 게임 수 자체가 부족. 표준 조언: 마감 3~7일 전 최종본 제출 시작.
3. **마지막 주 카운터 메타 추격 금지** — Halite IV·RPS에서 막판 상대 분포 급변으로 과적합 에이전트 붕괴, 강건한 제너럴리스트 생존. (H-028 신덱 기각 이력과 일치)
4. **리더보드 마이닝이 반복 우승 공식** — Kore 1위, Santa 2020, Lux S1 골드권 공통: "래더 자체가 최고 훈련 데이터".
5. **점수 상황별 분산 조절** — 승세면 저분산(결과 잠금), 열세면 고분산(역전 시도) 라인 선호.

**우리 대회 번역** (last-2 승계, 인스턴스 분산 711–845): 재제출은 '마지막 2개' 교체 + 게임 수 0 재시작 비용 → 낚시는 **수렴 관찰 후 낮으면 재제출, 높으면 정지**의 최적 중단 문제. 재제출 데드라인은 "수렴 필요 게임 수 ÷ 일일 매치 수"에서 역산 — 진행 중인 인스턴스 분포 연구(n=5)가 정확히 이 시간 상수를 재는 작업.

### 이식 가능 요소

| 요소 | 출처 | 구체안 | 비용 | 리스크 |
|---|---|---|---|---|
| **대실수 제거 우선** | Kore·Halite | 지는 판의 결정적 블런더 상위 3개를 리플레이에서 채굴 → 가드레일 규칙화 | 중간 | 과잉 가드레일 — 케이스 회귀 테스트 |
| **점수 상황별 분산 조절** | RPS | 확실한 승세면 코인플립·양날 라인 배제, 열세면 고분산 라인 선호 (임계값 2개 추가) | 낮음 | 평가 오판 — quick 게이트 |
| **아키타입 감지→테이블 전환** | RPS·Halite IV | 상대 공개 카드 3~5장으로 시그니처 분류 → 매치업별 증류 테이블 라우팅 (H-011 교훈 직결) | 중간 | 오분류 — 기본 테이블 폴백 |
| **승자 필터 재증류** | Kore·Lux S1 | 상위 레이팅 에이전트가 이긴 판의 **승자 측 수만** 증류 + 마감 주 최신 에피소드 재증류 | 낮음 | 표본 축소 — 750+/700 판정 규칙 유지 |
| **시간 뱅킹** | Geese·ConnectX | 초반 턴 테이블 즉답(오프닝북화), 리썰 윈도우에 시간 몰아주기 | 낮음~중간 | 타임아웃 — 하드 캡+폴백 |
| **제출 중단 규칙 문서화** | RPS+last-2 규칙 | "T일 전 이후 재제출 금지, 그 전엔 하위 수렴 시 즉시 재제출" 명문화 + 24h 버퍼 | 낮음 | 큐 지연 등 운영 리스크 |

### 링크

- Halite IV 1위: https://github.com/ttvand/Halite / Kore 1위: https://www.kaggle.com/competitions/kore-2022/discussion/340035 / IL 구현: https://github.com/khanhvu207/kore2022
- RPS 1위: https://github.com/thisisbowen/RPS-Kaggle-1st-Place-Solution / Santa 2020 스크래핑: https://www.kaggle.com/code/shivammittal274/santa-scrapping-top-episodes-to-ml-modelling
- Hungry Geese 2위 writeup / 3위 해설: https://speakerdeck.com/hoxomaxwell/kaggle-hungry-geese / Lux S3 정리: https://zenn.dev/kurupical/articles/61dbeedf89a29d

(신뢰도 주석: Kaggle discussion 본문은 SPA 열람 제한으로 일부 2차 자료 기반. 핵심 패턴은 복수 대회 교차 확인됨.)

---

## ③ 포켓몬 배틀 AI 문헌

### 발견 요약

- **배틀 예측 대회(FDS 2025, Intelygenz 등)**: 스탯 기반 모델로 95%+ 정확도가 일반적. 피처 중요도의 일관된 결론 — **Speed 차이(선공권)가 압도적 1위 피처**. 턴제 게임에서 "누가 먼저 때리는가"가 승패의 대부분을 설명.
- **PokéChamp** (ICML 2025 spotlight): LLM+minimax이지만 핵심은 구조 — 얕은 2-ply minimax + **"상대 KO까지 필요한 최소 턴 수"를 admissible heuristic으로 사용** + 대규모 리플레이 기반 상대 모델링. 8B 모델이 GPT-4o 기반 PokéLLMon을 이김 → 프레임워크(탐색+휴리스틱)가 모델 크기보다 중요.
- **Foul Play** (pmariglia, 최강급 Showdown 룰/탐색 봇): expectiminimax→MCTS, **수작업 선형 평가함수**가 핵심. 공개 가중치: 생존 +75, HP비율 최대 +100, 스탯 부스트 +15~25(체감효용), 상태이상 -10~-40, 필드 ±5~40. 은닉 정보는 usage stats에서 determinization 샘플링 + 관측 데미지로 역산.
- **PokéLLMon**: "panic switching"(평가 흔들림으로 교체 반복)이 주요 패인 → 행동 일관성으로 해결.
- **DeNA × Pokémon TCG Pocket RL** (CEDEC, 실서비스 PTCG AI 유일 공개 사례): (a) 상대 은닉 정보는 마스킹, 완전정보화 시도 안 함, (b) 자해성 플레이는 별도 하드 페널티로 억제, (c) 선택지 1개 행동은 자동 실행으로 추론 비용 절감.
- **Legends of Code and Magic 5년 총결산**: 배틀 페이즈는 수작업 룰 + minimax/MCTS + 휴리스틱 프루닝이 오래 지배. 휴리스틱 가중치는 **N-Tuple Bandit 진화 알고리즘으로 오프라인 튜닝**. end-to-end RL(ByteRL)이 최종 압승했으나 대규모 인프라 전제.

### 이식 가능 요소 (우선순위순)

1. **"Speed 피처"의 PTCG 번역 = 프라이즈 레이스 템포 항**: `내가 다음 프라이즈(및 남은 전체 프라이즈)까지 걸리는 턴 수 vs 상대의 턴 수` 차분을 평가함수 최상위 항으로. 현 리썰 윈도우(1턴 리썰 검증)의 자연스러운 확장 = **2~3턴 프라이즈 레이스 차분**.
2. **Foul Play식 선형 평가함수 골격**: 프라이즈 차(최대 가중치) / 유효 HP 합(상대 평균 타점 대비) / 에너지 부착(필요 초과분 체감) / 상태이상·도구 ± / 벤치 전개도.
3. **가중치 오프라인 튜닝**: 기존 evaluate/gauntlet 파이프라인 위에서 소수 파라미터 그리드/진화 탐색 (LOCM의 N-Tuple Bandit 교훈).
4. **Determinization 개선**: 상대 미공개 카드를 균등 샘플링하지 말고 `mine_episodes.py deck-stats` 덱 시그니처 통계에서 **조건부 샘플링** (공개 카드로 아키타입 posterior 좁히기).
5. **DeNA 실무 규칙**: 자해성 행동 하드 금지 룰, 강제 행동(선택지 1개) 즉시 실행으로 시간 예산 절약.
6. **계획 히스테리시스**: 턴 간 평가 진동으로 인한 타깃 스위칭 방지 (panic switching 교훈).

### 링크

- PokéChamp: [arXiv 2503.04094](https://arxiv.org/abs/2503.04094) / [GitHub](https://github.com/sethkarten/PokeChamp)
- Foul Play: [해설](https://pmariglia.github.io/posts/foul-play/) / [평가함수 소스](https://github.com/pmariglia/foul-play/blob/6102ea13/showdown/engine/evaluate.py)
- PokéLLMon: [arXiv 2402.01118](https://arxiv.org/html/2402.01118v2) / 봇 카탈로그: [pkmn.ai/projects](https://pkmn.ai/projects/)
- DeNA TCG Pocket RL: [Inven Global 기사](https://www.invenglobal.com/articles/24133/how-reinforcement-learning-ai-tackles-the-complex-rules-of-pok%C3%A9mon-trading-card-game-pocket)
- LOCM 총결산: [arXiv 2305.11814](https://arxiv.org/abs/2305.11814) / ByteRL: [arXiv 2303.04096](https://arxiv.org/abs/2303.04096)
- VGC AI: [IEEE](https://ieeexplore.ieee.org/document/9618985/) / [VGC-Bench](https://github.com/cameronangliss/VGC-Bench) / Metamon: [arXiv 2504.04395](https://arxiv.org/html/2504.04395v1)
- FDS 2025: [Kaggle](https://www.kaggle.com/competitions/fds-pokemon-battles-prediction-2025) (winning writeup 미공개)

---

## ④ 본 대회 최신 공유 스캔 (최근 ~5일)

신규 토픽 5건 본문을 `context/kaggle/topics/`에 추가 저장(732331, 733137, 733995, 734027, 734368). 공유 마감(8/2) 이후 신규 기법 노트북 없음.

### 신규 발견

- **734368 "BC for Beginners ~700 ELO (1/5)"** (8/11): 본문보다 댓글이 메타 정보 — 153위 "BC+약간의 최적화로 top 100 가능", 1756위 "PPO로 ~900; **정책망이 이미 괜찮으면 forward search를 얹어도 좋은 결과를 못 얻었다**"(우리 H-029b 기각과 정확히 일치), "현재 메타는 사실상 BC 따라하기".
- **733995 확정 사항 정리**: 기지 사실 재확인 + 미확정 질문 목록(48경기/일 보장 여부, 수렴 판정, Strategy 평가 연결 제출). 호스트 답변 추적 가치.
- **734027 로컬 리플레이 뷰어**: `kaggle-environments`(≥1.32) 캔버스 비주얼라이저로 episode replay JSON을 오프라인 `viewer.html` 일괄 렌더 — **수십 경기 배치 검토(블런더 마이닝)용 실용 툴**.
- **keidroid 매치메이킹 분석** (로컬 풀 다운로드): **같은 아티팩트 동시 2제출이 최종 1150 vs 867 (283점 차)** — 경로 의존성 정량 증거. 1000+ 제출은 첫날 ~900대 대비 3.5배 경기 수령. 경기 집중은 제출 후 0–3h + 11–21h. → 최종 제출은 초반 러닝 확보 타이밍에, 동일 아티팩트 2슬롯 제출이 변동성 헤지.
- **GitHub 외부**: wmh/ptcg-abc (Bellibolt ex Elo 836, Alakazam 미러 대비 Mist Energy 테크, "덱 선택은 어느 지점까지만"), TomBombadyl/kaggle_pokemon (RL+MCTS 580μ 퇴행 — search 레버 약함 판정과 일치).
- **Strategy 루브릭 원문**: Model Score 70%에 "**반복 경기·안정 조건 일관성**", "**특정 초기 상태·매치업 과의존 회피**" 명시 → 강건성 증거(양 좌석·다상대·대량 표본)가 채점 항목 그 자체. Deck 20%, Report 10%, **2000단어 제한**. 마감 9/13.

### 상위권 매치업 인텔

- masamikobayashi 1300+ 에이전트 = **Starmie/Froslass**. Archaludon ex/Cinderace 룰베이스가 그 상대 74.4%(1000경기) — Froslass의 Metal 약점 저격.
- soutasakurai 1208 LibraryOut 노트북(로컬 보유): Crustle LO 컨트롤 전체 코드 + 약점 자백 — h024b의 LO 매치업 방어 점검·상대 시뮬레이터로 활용 가치.
- prvsiyan search-audited Alakazam v9/v21(로컬 보유): 공식 search API 실전 사용례, 844.4 고점 주장.
- 732105 Bradley–Terry 대안 랭킹 제안 스레드 — 채택 시 경로 의존성 감소, 실제 승률 중요도 상승. 호스트 반응 추적.

### 링크

- [734368](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/discussion/734368) / [733995](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/discussion/733995) / [733137](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/discussion/733137) / [734027](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/discussion/734027)
- [keidroid 매치메이킹 분석](https://www.kaggle.com/code/keidroid/ptcg-ai-battle-rating-and-matchmaking-analysis)
- https://github.com/wmh/ptcg-abc / https://github.com/TomBombadyl/kaggle_pokemon
- [Strategy 루브릭](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/overview)

---

## 종합: 업그레이드 후보 (우선순위)

네 갈래 조사가 수렴하는 결론: **현 스택(룰+리썰 윈도우 탐색+증류 테이블)은 이 제약 조건(느린 엔진·RNG 복제 불가·CPU 제한)에서 역사적으로 올바른 아키텍처**다. Halite IV·ConnectX·HS AI Comp·ToT 모두 같은 조건에서 같은 골격이 우승했고, 본 대회 디스커션의 "정책이 좋으면 forward search 이득 없음" 증언은 H-029b 기각을 외부에서 재현한다. 따라서 남은 이득은 아키텍처 교체가 아니라 아래 순서의 정밀화다.

### A. 에이전트 개선 (가설 후보, 기대값순)

1. **H-030 후보: 블런더 마이닝 → 가드레일** (②의 top-3 격차 실체, ③ DeNA 하드 페널티). 패배 에피소드에서 결정적 블런더 상위 3개 채굴(734027 뷰어 활용) → 하드 금지 규칙화. Kore 1위의 IL 승리 요인이 정확히 "대실수 제거"였음. 비용 중간, 기존 mine_episodes 파이프라인 재활용.
2. **H-031 후보: 승자 필터 재증류** (② Kore/Lux, "래더가 최고 훈련 데이터"). 상위 레이팅 에이전트가 **이긴 판의 승자 측 수만** 증류 + 최신 에피소드 재증류. 비용 낮음(파이프라인 보유), 750+/700 판정 규칙 유지.
3. **H-032 후보: 결정화 3–5 앙상블 리썰 검증** (① ToT 우승 방식). 현 2-of-2 determinization verify를 3–5 시드 평균/AND 투표로. 비용 낮음, 기존 탐색 루프에 시드 루프 추가.
4. **템포 항 평가함수 + 오프라인 가중치 튜닝** (③ PokéChamp/Foul Play/LOCM). "양측 다음 프라이즈까지 턴 수 차분"을 평가 최상위 항으로, gauntlet으로 튜닝. 단 H-023(튜닝) 계열 이력상 전이 리스크 있음 — 창 확대와 결합 시에만.
5. **아키타입 감지 → 테이블/전략 라우팅** (①②④). 상대 공개 카드 3~5장으로 시그니처 분류 → 매치업별 대응. Starmie/Froslass↔Archaludon 인텔이 구체 타깃. 오분류 시 기본 폴백 필수.
6. **시간 안전마진 감사** (① HS 실격 다수): 예산 80–85% anytime 컷 + 폴백 수 상시 확보 — 저비용 점검.

### B. 엔드게임 운영 (8/14–16)

- **낚시 = 최적 중단 문제 공식화**: 낮게 수렴하면 재제출, 높게 수렴하면 정지. 재제출 데드라인은 수렴 필요 게임 수 ÷ 일일 매치 수에서 역산(현 n=5 인스턴스 연구가 시간 상수 측정).
- **keidroid 증거 반영**: 최종 2슬롯은 동일 아티팩트(h024b) 이중화가 변동성 헤지. 제출 직후 0–3h에 경기 집중 → 판독 타이밍 설계.
- **막판 카운터 메타 튜닝 금지** (② Halite/RPS 교훈, H-028 기각 이력과 일치).

### C. Strategy Writeup (9/13)

- 루브릭의 "일관성·과의존 회피" 명문화 → **양 좌석·다상대·대량 표본 강건성 증거가 채점 항목 그 자체**. 기존 results.tsv 원장과 인스턴스 분포 연구가 곧 writeup 데이터.
- "탐색은 공격 창에서만 값을 낸다"(H-029b), "덱이 아니라 정책이 천장"(3진 아웃 + 81위 증언 + wmh/ptcg-abc) — 외부 증거로 보강된 서사 확보.
- 2000단어 제한, 図表 활용 가점, 카드명 언급 허용(이미지 금지).
