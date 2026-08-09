# Strategy Writeup 골격 v1 (2026-08-08 — 벤치마크 3종 반영)

목표: 2,000단어 이하. 원칙: **루브릭 체크리스트 채점에 맞춰 줄 단위로 채점하기 쉽게** 쓴다.
근거: `../08-writeup-benchmarks.md` (시뮬레이션 우승작 6편 + 심사형 우승작 6편 + 현 대회 지형).

## 작성 원칙 (벤치마크 도출)

- 섹션 제목에 루브릭 언어 미러링, **제목이 곧 발견**("Data refresh alone bought +88 rating" 식).
- 훅+TL;DR 100단어 이내. 배경 설명 금지. 시간순 일지 금지 — 주장 단위 조직.
- 모든 주장 옆에 수치(표본수·CI 병기). 그림은 캡션에 takeaway 내장.
- 서두에 재현성 선언 1문장(코드·원장·그림 재현 경로).
- 시그니처 혁신에 이름: **"distilled-opponent gate"**, **"reply-horizon search"**.
- 강건성은 한 문장 수치로(ttvand 패턴): 세대별 게이트 통과·양좌석·아키타입 성적 압축.
- 정직 섹션 필수(What didn't work) — 메커니즘 설명 포함.

## 섹션 골격 (단어 예산 2,000 / 그림 5)

1. **Approach at a Glance** (~150w)
   - 테제 1문장: replay-mined priors + determinized turn search + learned value, every change gated by falsifiable local experiments.
   - 헤드라인 수치 표 3행(최종 레이팅, 건틀릿 양좌석 승률, held-out 일치율). 재현성 선언 1문장.
2. **Deck Rationale: Deck Selection as a Data Problem** (~250w + 그림: 덱 승률 분포)
   - 일일 episode 마이닝 → 덱 시그니처·승률 집계 → Majkel Lucario 63.4% 전체 1위 확인 후 채택.
   - "덱은 옳고 파일럿이 문제" 반전(meta0 46.4% 평범). 키 카드 4~6개 역할 소표 + 에이전트 정책과의 정합.
   - [Deck 20% 전용 — 벤치마크 대회들엔 없던 항목, 묻히면 안 됨]
3. **How the Agent Decides** (~400w + 우선순위 캐스케이드 의사코드)
   - 계층: 증류 프라이어 → 결정화 턴 탐색(하위 선택 포함) → 응수 테이블 상대 모델 → 학습 가치함수 리프.
   - 발견-제목 소절: "The same data has different value at different injection points" (H-015: MAIN 블렌드 무효 → 탐색 리프 +7.5pp).
4. **Worked Example: One Turn, Annotated** (~250w + 3패널 그림: 보드상태+행동분포+승률곡선)
   - Toad Brigade 패턴. 리썰/체인 결정 순간 1개 주석.
5. **Consistency Under Repeated Play** (~250w + 그림: 건틀릿 매트릭스 or 래더 궤적)
   - 양좌석 반복·표본 규율(비결정론 엔진 → paired A/B 불가 판단 포함), 세대별 래더 수렴치 아블레이션 표.
   - 평가 방법론 서사: 제네릭 봇 85~90% 포화 → **distilled-opponent gate**(52.5% 비포화) 발명.
6. **Robustness and Weak Matchups** (~250w + 그림: 좌석×아키타입 소형 다중)
   - two-regime 패턴: 좌석 × 아키타입(meta2 40-0, grimmsnarl 39-1, meta0d, 미러).
   - 최악 매치업(meta0) 공개 + 진단(승자 대비 핸드 체인 절반 실행) + 패치 서사. H-017f 기각 = 과적합 회피 실례.
7. **What Didn't Work** (~200w)
   - 스케일링 무효 3건(노드 3배·K=6·예산 8s — 전부 CI 내), 관측 로지스틱의 드로우 인과 실패(`my_deck_consumed` 음수 교란), RL 미채택 근거(공개 지형 인용: 공개 RL 시도 전부 룰베이스 이하).
8. **Conclusion + Code** (~100w)

## 열린 결정

- c-number식 내장 아블레이션(최종 2슬롯 = best + 제거판): 순위 손해 트레이드오프 있음. 차선 = 과거 세대 래더 수렴치가 자연 아블레이션 → 아블레이션 표로 대체 가능. 8/14 슬롯 결정 때 확정.
- 카드명 텍스트 언급 범위: 규정 질문(733690) 미답변 — 최소화 방침 유지.
- 덱리스트는 첨부로(단어 수 방어, 733067 미답변).

## 그림 자산 계획 (5개)

| 그림 | 섹션 | 상태 |
|---|---|---|
| 덱 승률 분포(마이닝) | §2 | 신규 — mine_episodes deck-stats |
| 우선순위 캐스케이드 의사코드 | §3 | 신규 — 텍스트 블록 |
| 3패널 게임 순간 | §4 | 신규 — replay + 가치함수 곡선 |
| 래더 궤적/아블레이션 | §5 | fig_ladder_trajectory 갱신됨 + ablation_table.md |
| 좌석×아키타입 소형 다중 | §6 | fig_seat_split + fig_by_opponent 통합 리디자인 |
