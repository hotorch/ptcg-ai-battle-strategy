# 외부 맥락과 초기 큐레이션

## 자동 수집

```bash
uv run python scripts/kaggle_ops.py sync-context
uv run python scripts/curate_context.py
```

선별 점수는 투표·댓글·대회 관련 키워드의 작은 휴리스틱이다. 점수는 진실성이나 코드 품질이 아니라 읽을 순서를 정한다. 원문 URL·작성자·시각·라이선스를 확인한 뒤 가설로 옮긴다.

## 2026-08-05 초기 확인

- 공식 CABT 환경 이름은 `cabt`; observation은 `logs`, `current`, `select`로 구성된다.
- engine source는 공개되었고 대회 목적의 수정/파생 사용이 허용되지만 Competition Data 사용 제한이 적용된다.
- daily top episode dataset은 참가자 평균 rating이 높은 episode 쪽으로 편향된다.
- 공식 sample은 `main.py`, `deck.csv`, `cg/`를 아카이브 최상위에 둔다.
- public local-battle notebook은 반복 경기·양 좌석·중간 checkpoint를 사용한다.
- 공개 상위 baseline은 deck-specific heuristic과 meta patch가 중심이다. 지금 단계에서는 전략 코드를 복사하지 않고 환경 계약만 가져온다.
- replay visualizer의 selected action이 한 step 밀린다는 engine-source 기반 보고가 있다.
- Python 수준 seed가 native engine 초기 상태를 재현하지 못한다는 공개 감사 결과가 있어 paired deterministic A/B는 보류한다.

## 우선 확인할 공식 Discussion

- Game Engine Source Code (`717141`)
- Differences Between Official Rules and Simulator (`708586`)
- Daily Top Episodes Datasets (`709160`)
- Reminder about Simulation Competition Format (`714189`)
- How to Get Started (`708492`)

## 초기 Notebook 표본

- `guregu321/basics-build-a-local-battle-environment`
- `godhand/en-submission-sanity-checker-0`
- `ryona0123/beginner-guide-from-deck-list-to-first-valid-sub`
- `makthanithin/pokemon-tcg-ai-battle-1084-5-baseline`

