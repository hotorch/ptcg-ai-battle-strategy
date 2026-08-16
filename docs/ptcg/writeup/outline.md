# Strategy Writeup 골격 v2 (2026-08-16 — 최종 서사 반영 개정)

목표: 2,000단어 이하, 그림 5. 원칙: **루브릭 체크리스트 채점에 맞춰 줄 단위로 채점하기 쉽게** 쓴다.
근거: `../08-writeup-benchmarks.md` + 최종 2주의 실제 서사. v1(8/8)은 git 이력 참조 — v1의 테제("replay-mined priors + turn search + learned value")는 1주차 스택 기준이라 **최종 에이전트(h036, fork 계열)와 불일치**하여 전면 개정.

## v2 테제 (한 문장)

> We treated the ladder itself as the object of study: every build is a **distribution** (57 submissions, 17 builds), every change is a **gated experiment** (zero-collateral replay regression), and the meta is a **dynamical system** we measured well enough to predict its final state (Dragapult 6.3%→41.2%, called in advance).

최종 에이전트 = 공개 룰베이스 베이스라인(Rozen V10, 명시적 크레딧)을 5회의 검증된 외과수술로 개선한 것. **독창성 주장의 축은 에이전트 코드가 아니라 실험 방법론** — 이것이 정직하面서 루브릭(독창성·기술적 타당성·강건성) 최적화 포지션.

## 섹션 골격 (단어 예산 2,000 / 그림 5)

1. **Approach at a Glance** (~150w)
   - 테제 1문장 + 헤드라인 수치: 57 submissions / 17 builds, 21,975-decision zero-collateral verification, meta endgame predicted-then-verified (41.2% vs limitless equilibrium 42.7%), 최종 페어 레이팅.
   - 재현성 선언 1문장(코드·원장 results.tsv·그림 재현 경로).
2. **Deck Selection as a Data Problem** (~220w + 그림 없음, 소표 1)
   - 초기: 데일리 episode 마이닝 → 시그니처·승률 집계로 Alakazam 라인 채택(당시 상위 점유·검증된 리스트). 키 카드 4~6개 역할 소표 + 정책과의 정합(Abra 스나이프, boss 라인).
   - 후기: **군중픽 역설 발견** (most-played = worst-performing: Grimmsnarl 23%/41%, Alakazam 13%/44%) + 덱-정책 결합도 때문에 교체 비용이 게이트 예산 초과 → 유지 결정의 정량 근거. "무엇을 언제 알았고 왜 그대로 갔나"를 데이터로 서술 — Deck 20%는 응원이 아니라 분석으로 딴다.
3. **How the Agent Decides — and the Five Surgeries** (~350w + 그림 A: 우선순위 캐스케이드 + 수술 부위 마킹)
   - fork 골격(우선순위 캐스케이드) 위 5개 수술: light-lethal graft(H-024b), deck-out guard(H-030), mirror-list(H-034), stall guard(H-035), **tempo boss(H-036)**.
   - Worked example 통합: tempo-boss 플립 1개 주석(드로 서포터 4249 vs boss_kill_now 6000 — 킬 수학 포함). 표준: **리플레이 회귀 21,975결정 65/65 의도 플립·부수피해 0**만 출고.
   - 발견-제목 소절 유지: "The same data has different value at different injection points" (H-015).
4. **Every Build Is a Distribution** (~300w + 그림 B: 빌드별 인스턴스 분포 스트립 플롯) — **방법론 센터피스**
   - 동일 빌드 반복 제출로 래더 레이팅 분포 표집: h024b n=7 (711~845), h036 n=9 (674~757). 단일 제출 = 분포에서 1추첨 — 래더 단일 표본 A/B는 통계적으로 무효.
   - **통제 실험**: 동일 빌드 3일 후 재제출(825.4 vs 사전 n=4 평균 782) — 밴드 안정성 검증.
   - **래더 역학 3발견**: sticky placement(4-1 스타트 → 943 스파이크 → 750 수렴, ~30경기 반감), 신규 제출 우선 스케줄링(동시간 32경기 vs 1경기), 마감 후 수렴이 배치 운을 소거 — 최종 페어 잠금 논리의 근거.
5. **The Meta Is a Dynamical System** (~300w + 그림 C: 수렴 시계열 + 예측→실현 화살표)
   - 상위 풀 점유율 시계열(8/04~15) × 외부 균형(limitless): TV 거리 단조 수렴(0.398→0.321), 메커니즘 = 래더 내 선택압(저승률 군중픽 도태).
   - **예측의 실현**: "마감 풀은 더 Dragapult-heavy" (8/14 기록) → 8/15 실측 41.2%(균형점 42.7% 도달). 노출 가중 기대승률 궤적(45-48%→43%→37.5%)으로 "다가오는 벽" 정량화 → 최종 주 의사결정(마이크로 엣지, 기적 금지)의 근거.
6. **Consistency & Robustness** (~250w + 그림 D: 좌석×아키타입 매트릭스)
   - 엔진 비결정론 → paired A/B 불가 판정 → 양좌석 반복 + 표본 규율. 제네릭 봇 포화(85-90%) → **distilled-opponent gate** 발명(비포화 52.5%).
   - 최악 매치업 공개: Dragapult 24.9%, Slowking 29.2% + 노출 수학(레이팅 상승 → 노출 증가 → 천장) — 강건성 항목을 "약점의 정직한 정량화"로 채점받기.
7. **What Didn't Work** (~200w)
   - 1주차 ML 스택 전부(증류 484-571, 학습 가치함수 511-601, 탐색 587-667)가 **공개 룰베이스 fork(818.8)에 완패** — 메커니즘 진단 포함(가치함수 AUC .74로는 수제 우선순위 대비 신호 부족, 증류는 파일럿 혼합의 평균으로 회귀).
   - 스케일링 무효 3건, H-017f 과적합 기각, RL 미채택 근거(공개 지형).
8. **Conclusion + Code** (~80w): 잠금 논리(수렴이 최종 심판), MIT 공개.

## 그림 자산 계획 (5개)

| 그림 | 섹션 | 상태 |
|---|---|---|
| A. 우선순위 캐스케이드 + 5수술 부위 | §3 | 신규 — 텍스트/다이어그램 |
| B. 빌드별 인스턴스 분포 스트립 플롯 | §4 | 신규 — rating_history.tsv에서 생성 |
| C. 메타 수렴 시계열 + 예측 실현 | §5 | 신규 — 결과 4·5 데이터 |
| D. 좌석×아키타입 매트릭스 | §6 | fig_seat_split + fig_by_opponent 통합 |
| E. 래더 궤적 + 이벤트 주석(i5 스파이크 포함) | §4 보조 or §1 훅 | fig_ladder_trajectory 갱신 |

## 열린 결정 (v1에서 승계·갱신)

- 내장 아블레이션: 과거 세대 래더 수렴치가 자연 아블레이션 → 아블레이션 표로 대체 (확정 — 최종 슬롯은 h036 페어로 잠금됨).
- 카드명 텍스트 언급 최소화 방침 유지(733690 미답변). 덱리스트는 첨부(733067 미답변).
- **마감 후 2주 수렴 데이터**(8/17~30): i8/i9 최종 수렴 궤적을 §4의 마지막 증거로 추가 — "예측한 수렴을 자기 에이전트로 재검증" 마무리. 9/1 이후 최종 수치 반영해 탈고.
- 2라운드 규정 확인(8/14 공식 답변): Writeup에 두 제출 모두 포함 가능 — i8/i9 페어 운영(분포 표집의 실전 적용)을 §4에 1문장으로.

## 일정 (9/13 마감)

- 8/17~30: 수렴 관전 + 주 2회 궤적 기록(자동화 검토). 그림 B/C/E 데이터 확정.
- 8/31~9/5: 초안 1 (2,000w) + 그림 5종 생성.
- 9/6~9/10: 벤치마크 루브릭 대조 퇴고 + 외부 시선 검토 1회.
- 9/11~13: 최종 제출 (draft 아닌 Submit 확인 — 저장만 된 draft는 심사 제외!).
