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
