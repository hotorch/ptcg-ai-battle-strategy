# CLAUDE.md

Kaggle [PTCG AI Battle Challenge Simulation](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle) 연구 작업공간. 기준 규칙은 `AGENTS.md`, 대회 라우터는 `docs/ptcg/README.md`다.

## 명령어

```bash
uv sync
uv run python scripts/smoke_test.py
uv run pytest -q
uv run ruff check scripts/ tests/ main.py

uv run python scripts/evaluate.py --candidate . --bundle smoke
uv run python scripts/evaluate.py --candidate candidates/<h###_slug> --bundle quick
uv run python scripts/evaluate.py --candidate candidates/<h###_slug> --bundle full \
  --opponents random,first,. --experiment-id YYYYMMDD-H###-nn \
  --hypothesis-id H-### --append-results

uv run python scripts/kaggle_ops.py auth-check
uv run python scripts/kaggle_ops.py status
uv run python scripts/kaggle_ops.py sync-context
uv run python scripts/curate_context.py
uv run python scripts/package_submission.py --source .
```

## 구조

- `main.py + deck.csv`: 현재 best. 초기 기준선은 공식 Mega Lucario sample deck을 사용하는 random legal-action agent다.
- `candidates/h###_slug/`: 후보별 독립 제출 루트.
- `research_loop/results.tsv`: 비교 원장. `runs/` 상세 JSON은 재생성 가능하므로 gitignore.
- `context/kaggle/`: 공식 페이지·Discussion·Notebook 스냅샷과 큐레이션 결과.
- `data/raw/`: Competition Data. 커밋 금지, 대회 종료 후 삭제.

## 중요한 차이

Kaggriculture 레포의 운영 루프는 재사용하지만 평가기는 재사용하지 않는다. CABT 엔진은 공식 RNG seed/상태 복제 방법이 문서화되지 않았으므로 같은 seed의 결정론적 A/B가 아니다. 양 좌석 반복 경기와 충분한 표본으로 판단한다.

제출은 단일 `.py`가 아니라 `.tar.gz`다. 최상위 `main.py`, `deck.csv`가 필수이며 `cg`를 import하면 `scripts/package_submission.py`가 SDK를 함께 묶는다. 실제 제출은 사용자 승인과 `--confirm SUBMIT_PTCG_AI_BATTLE`이 모두 필요하다.

일일 전체 루프는 `/daily-run`을 사용한다.

