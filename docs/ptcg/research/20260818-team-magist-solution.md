# Pokemon TCG AI - Team Magist Solution (본문 전문)

- URL: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/writeups/team-magist-solution
- 저자: jazivxt, WOOSUNG YOON · 게시 2026-08-17 · Solution Writeup · 114th place
- 수집: 2026-08-18, 브라우저 렌더링 (Kaggle CLI `topics show`는 원글 본문을 반환하지 않아 수동 수집. 735593.json에는 메타데이터+댓글만 있음)

---

## Part 1. General Strategy

### A. Pattern Database

Waltheri's Go Pattern Search(https://ps.waltheri.net/)에서 영감. 프로 기보에서 유사 국면을 검색해 후속 수·결과 통계를 얻는 접근을 PTCG로 이식.

**Pokemon Pattern DB**: 실제 매치 리플레이에서 현재 상황과 유사한 게임 상태를 검색, 양 플레이어의 다음 액션과 기대 결과를 과거 통계로 추정.

- Primary Key: 양측 Active Pokémon
- Secondary Keys: Damage Counters(5단위 양자화), Bench 구성, Energy 부착량

결론: 유사 과거 국면 기반의 단순·고속 상대 모델링. 국지 전술 패턴은 리플레이에서 직접 포착하고, 전체 국면 평가는 Value Network로 보완.

### B. Transformer Policy / Value Architecture (T96)

```
Game State (Cards, Pokémon, HP, Energy, Bench, Hand, ...)
  → Game Information Encoding
  → Transformer (2 layers, 4 attention heads)
  → Shared Game-State Representation
      ├─ Action Head: 합법 액션 스코어
      ├─ Pass Head: 패스 여부
      └─ Value Head: 국면 평가·승률
```

- 초기 2층에서 시작, 층을 점진 추가하며 층별 learning rate로 안정화.
- **Supervised Learning 데이터 3원**: ① Leaderboard Public Play(제출 에이전트 경기) ② Heuristic Agents(규칙 기반) ③ League Play(학습 모델·체크포인트·휴리스틱 간 리그전)

### C. Heuristic Tactical Variants

- Self-play는 국지 메타에 서로 수렴하는 문제 → 전술 다양성 확보 필요.
- 신경망 정책이 기본, 휴리스틱은 선택적 보강: Energy 배분, 후퇴 결정, 강제 승리 시퀀스, 카드별 특수 상황.
- 우선순위 조정(전개/진화/에너지/후퇴/공격 선호 변경) + 표적 가이드로 전술 변형 에이전트를 만들어 리그에 투입 → 상태·전략 다양성 확대.

### D. Deck Selection (GA 탐색)

- 덱 표현: 카드별 매수 유전자 `[Card A: 4] [Card B: 2] ... [Card N: 1]`, 제약(4매 제한, ACE SPEC 1장, 60장) 적용.
- Crossover/Mutation → CPU 병렬 매치 평가 → 선택.
- **결과: 특이 변형 덱이 나왔지만 일관되게 더 강하지 않았음. 반복 실험에서 상위 리더보드 덱 구조가 더 안정적** → 최종 제출은 상위 공개 덱을 거의 그대로 쓰고 잔여 최적화는 플레이 정책에 집중.
  - ※ 우리의 build-as-distribution 결론(상위 메타 덱 분포 추종)과 독립적으로 교차검증됨.

### E. Monte Carlo Sampling

- 히든 정보·랜덤 이벤트가 걸린 액션(예: Judge)에서 사용.
- 후보 액션마다 가능한 결과를 다중 샘플 → 신경망 정책으로 이어서 플레이 → Value Head 평가 → 평균 기대값으로 액션 비교.
- 예: Judge 사용 시 셔플·드로우 결과 핸드를 여러 개 샘플해 "Judge를 안 쓴 가치"와 비교.

### 링크

- Codex Sol Eclipse Alakazam (노트북, 118 upvotes)
- A Visit to a Pokémon Card Shop Mini Tournament: discussion/714505
- Pokémon Deck List: discussion/721010
- A Better Hand - Alakazam Rising Tide v21 (노트북, 55 upvotes)

### 인용

jazivxt, WOOSUNG YOON. Pokemon TCG AI - Team Magist Solution. https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/writeups/team-magist-solution. 2026. Kaggle
