---
description: PTCG 일일 연구 파이프라인 — 맥락 수집부터 승인된 제출까지
---

1. `AGENTS.md`, `docs/ptcg/README.md`, 최신 저널의 “내일 우선순위”를 읽는다.
2. `uv run python scripts/kaggle_ops.py auth-check`, `status`, `track-ratings`를 실행한다.
3. `sync-context`와 `curate_context.py`로 최신 공식 Discussion/Notebook을 선별한다.
4. 외부 주장을 사실·가설·규칙 위험으로 나누고 `04-hypotheses.md`를 갱신한다.
5. 오늘 검증할 가설 1~3개를 고르고 후보 디렉터리별로 smoke → quick → full을 실행한다.
6. 비결정적 엔진의 한 번 결과가 아니라 반복 결과·양 좌석·오류·95% 구간으로 승격을 판단한다.
7. 승격 후보만 `package_submission.py`로 self-play/아카이브 검증한다.
8. 실제 Kaggle 제출은 해당 후보에 대한 사용자 승인이 있을 때만 실행한다. 승인이 없으면 패키지 경로까지만 보고한다.
9. `daily_log.py --write` 후 한 일·배운 것·내일 우선순위를 채운다.

