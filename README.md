# PTCG AI Battle Research

Kaggle의 [PTCG AI Battle Challenge Simulation](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle)용 재현 가능한 연구 작업공간입니다.

```bash
uv sync
uv run python scripts/kaggle_ops.py fetch-sdk
uv run python scripts/smoke_test.py
uv run pytest -q
```

핵심 흐름은 `외부 맥락 수집 → 가설 등록 → 후보 구현 → 반복 경기 평가 → 현재 best 승격 → 검증·패키징 → 승인 후 제출`입니다.

- `main.py`, `deck.csv`: 현재 best와 기준 덱
- `candidates/h###_slug/`: 가설별 `main.py + deck.csv`
- `scripts/evaluate.py`: 비결정적 반복 경기 평가
- `scripts/package_submission.py`: Kaggle용 `.tar.gz` 검증·생성
- `scripts/kaggle_ops.py`: 읽기 작업과 확인 문구가 필요한 제출
- `scripts/curate_context.py`: Discussion/Notebook 선별 및 원문 수집
- `docs/ptcg/`: 대회 사실, 검증 규약, 가설, 제출 절차
- `research_loop/results.tsv`: 실험 결과 원장

대회 데이터는 Competition Use Only이므로 `data/raw/`에만 두며 커밋하지 않습니다.

## Omitted artifacts / 제외된 산출물

이 저장소는 대회 규칙 2.4.b.1(Competition Data 재배포 금지)과 3.6.b(Pokémon Elements 공개 금지)를
지키기 위해, 리플레이에서 파생한 다음 산출물을 **커밋 히스토리에서 제거**했습니다.

| 경로 | 내용 | 재생성 |
|---|---|---|
| `candidates/*/meta_decks.json` | 상위 풀 리플레이에서 채굴한 타 참가자 덱 구성 + 경기 수 | `scripts/mine_episodes.py deck-stats` |
| `research_loop/deck_*.json` | 개별 참가자 덱 스냅샷 | `scripts/mine_episodes.py extract` |
| `docs/ptcg/writeup/trace_game.json` | 단일 경기 트레이스 | `scripts/evaluate.py` |

제출본(`main.py` + `deck.csv`)은 이 파일들을 참조하지 않으므로 그대로 실행됩니다. 탐색 계열 후보의
`_load_meta_decks()`는 파일 부재 시 빈 리스트를 반환하므로 동작하되 상대 덱 사전(prior)만 비활성화됩니다.
본인의 Competition Data로 위 명령을 실행하면 복원됩니다.
