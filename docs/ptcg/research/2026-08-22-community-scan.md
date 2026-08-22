# 2026-08-22 커뮤니티·수렴 통합 판독 (마감 후 D+6)

수렴 루틴 데이터와 디스커션 신규 글(마감 후 솔루션·운영 스레드)을 함께 판독한 기록.
출처는 전부 공개 디스커션이며, 인용 시 스레드 ID를 병기한다.

## 1. 수렴 루틴 판독 (pair_convergence.tsv 8/17~22)

- i8 730.0(314g, 승률 52.2%) / i9 699.5(322g, 50.9%). 격차 30.5 — 8/21에는 i9가 +15.5로 우세했다가 하루 만에 역전. **동일 코드 두 인스턴스가 300+경기 후에도 ±30 밴드에서 요동** = 인스턴스 분포 방법론의 최종 검증 데이터가 쌓이는 중.
- 게임 레이트 급가속(67→132→219→314g): 원인 확인됨 — 공식 스로틀 버그. 8/18~19에 12~20/day로 정체(5위 Azat, 6위 Dipam, 33위 CroDoc 증언, topic 735822·735312), **8/20 Kaggle 스태프 수정("Should be significantly faster now")** 후 ~95/day로 공언치(96/day) 도달.
- 함의: 8/30 확정까지 ~700경기/인스턴스 추가 → 밴드는 더 좁아질 것. 현 추세로 최종 헤드라인은 **순위가 아니라 방법론**이 맞다(둘 다 700~745 밴드, 브론즈 컷 840 미달).

## 2. 공식 사실 (topic 735312, Addison 공지 + 댓글)

- 마감 후 2주 연장 에피소드: 48/day에서 96/day로 점진 증량 계획 공언 (실제로는 스로틀 후 8/20 회복).
- **anti-cheat 퍼지 "early next week"(= 이번 주)** — 팀이 LB에서 사라질 수 있음. → **우리 rank가 수동적으로 오를 수 있다. 루틴에 rank 추적 추가 가치 있음** (pair_convergence.tsv에는 rating만 있음).
- 솔루션 공개는 공식 권장 사항. 단 Writeup 점수는 자기 제출의 LB 성과에 묶임(표절 무의미 명시).

## 3. 상위권 솔루션·증언 스캔 — Writeup에 쓸 것

### 3.1 Team Magist 솔루션 (topic 735593, 219위) — **우리 포크의 원 계보**

- 저자 = **jazivxt + WOOSUNG YOON**. 우리가 fork한 Rozen V10의 상류인 "Codex Sol Eclipse Alakazam" 공개 노트북(119 upvotes)의 팀. 공식 Kaggle Writeup 형식으로 이미 게시(구조 참고용 실물: 섹션 구성, ASCII 다이어그램, Project Links, Citation).
- 내용: Waltheri식 패턴 DB(리플레이 유사 국면 검색) + 2층 Transformer policy/value(T96) + MC 샘플링(Judge 등 은닉 정보 액션 평가) + **GA 덱 탐색 → "상위 LB 공개 덱이 더 안정적" 결론**.
- 인용 가치: ① 크레딧 정확화(포크 계보를 명시적으로 그들의 writeup URL로 연결) ② **GA 덱 탐색 무효 결론 = 우리 신덱 레버 3진 아웃과 독립 재현** (219위 팀도 동일 결론).

### 3.2 탐색·RL 부정적 증언 (topic 736121 댓글, 8/19~20)

- **Dipam Chakraborty(6위)**: "MCTS doesn't work because of the unknowns about opponent's deck… after long enough training, MCTS was a wash against the direct policy head."
- **Kh0a(33위)**: "My MCTS with value head stuck at 700 elo."
- RMensinck(1198위): PPO로 900 못 넘김.
- 인용 가치: **우리 1주차 탐색+가치함수 천장(667)의 독립 corroboration이 6위·33위에게서 나옴.** §7 정직 섹션의 "우리만의 실패가 아니라 구조적 난점"으로 격상 가능.

### 3.3 BC(행동 복제)는 대규모 신경망으로는 통했다 — 정직한 대비

- Anil Ozturk(527위, topic 736121): 마지막 1주 BC(4.65M 결정, 6층 Transformer)+PPO+MCTS로 상위 브론즈~하위 실버 도달 주장. TommyCyd 팀(100위, topic 735503): 룰→BC 혼합. Belati(167위): "BC로 실버 직행".
- 함의: 우리 **선택률 표 증류(최고 571)의 실패 원인은 '리플레이 학습' 자체가 아니라 표(capacity) + 데이터 규모**. §5 정직한 실패 서술을 이렇게 정밀화하면 방어력이 오른다 (채점 질문 "기술적 타당성" 대비).

### 3.4 레이팅 측정 비판 스레드 (topic 732105, 8/02~) — 래더 과학 절의 프레임

- c-number(12위): TrueSkill LB의 역사적 수렴 실패(체스 대회 사례) → 최종 순위에 주간 평균+Bradley-Terry 요청. 공식 답: "mid-competition 변경은 too disruptive" → 기각.
- KaizaburoChubachi(21위): per-match 업데이트의 **경로 의존성(path-dependence)** 정식 비판 + BT 일괄 적합 제안.
- e-toppo(14위, topic 736361): 10% 랜덤 매치 = 고레이팅에게 "win +0, lose −15 복권". KawattaTaido(3위)도 분산 영향 인정.
- 인용 가치: **우리 '57제출/17빌드 반복 표집' 방법론 = 상위권이 공개 제기한 측정 문제에 대한 참가자 측 해답**이라는 프레임. 그림 B(인스턴스 분포)의 서론이 이 스레드 인용으로 완성된다.

### 3.5 그림 C의 훅 인용 출처 확정 (topic 735123, 8/14, LiamK 당시 3위→현 15위)

> "cool to watch the leaderboard decks look more and more like the limitless meta distribution over time (e.g. more and more dragapult). Can't decide if that's just us copying the external meta or if we're just moving towards an inevitable equilibrium."

- top-agent-observation.md 결과 4의 "3위권 팀 발언"의 공개 원문이 이것. **그림 C가 이 공개 질문에 대한 데이터 답변**(선택압 메커니즘: 저승률 군중픽 도태)이라는 구도로 §5 서두를 열 수 있다.

## 4. 데이터 기회: 마감 후 데일리 계속 발행 중

- `kaggle/pokemon-tcg-ai-battle-episodes-2026-08-18`, `-2026-08-20` 존재 확인(8/22). 연장 기간에도 데일리 발행 지속.
- → **그림 C를 8/16~8/21+로 연장 가능**: "마감 후 풀은 더 Dragapult-heavy할 것"(결과 4 예측 3)을 관측으로 전환. 예측→실현 화살표가 실측 연장선으로 대체되는, 그림 C의 최종 강화.

## 5. 남은 기간 액션 제안 (우선순위순)

1. **그림 C 연장** — 8/16~ 데일리 zip 수급 → `mine_episodes deck-stats` → `report_figures.py meta` 재실행 (파이프라인 그대로, 다운로드만 추가).
2. **rank 추적 추가** — anti-cheat 퍼지로 순위 변동 가능. 일일 루틴에 LB rank 기록 1줄 추가.
3. **draft-context 반영** — §2 서사에 3.1~3.5 인용 포인트 링크(이 문서 참조로 갈음 가능), §5 정직 섹션에 3.2·3.3 대비 구도.
4. (선택) topic 735649(내부 툴링), 736494(journey) 추가 스캔 — 우선순위 낮음.
