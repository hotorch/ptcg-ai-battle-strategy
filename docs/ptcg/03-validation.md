# 검증 프로토콜

## 핵심 제약

CABT native engine에는 공식적으로 노출된 RNG seed, 상태 export/import, 동일 초기 상태 replay 방법이 없다. Python random seed만 고정해도 shuffle·setup이 같아진다고 가정하지 않는다.

따라서 후보 비교는 다음 순서를 따른다.

1. `smoke`: self-play 1경기로 계약·crash 확인.
2. `quick`: 상대마다 양 좌석 10경기씩 실행해 방향 확인.
3. `full`: 상대마다 양 좌석 50경기 이상 실행. 표본을 더 원하면 `deep`(150) 또는 `--games-per-seat`.
4. 후보와 현재 best를 같은 공개 상대 묶음에서 별도로 평가하고, 필요하면 반복 실행한다.
5. 전체 win rate뿐 아니라 좌석별·**상대별**(`by_opponent`) 결과, draw, error, 표본 수, 95% Wilson interval을 본다. 상대 풀 합산 승률은 매치업 붕괴를 가린다.
6. 한 matchup 개선이 다른 matchup 붕괴를 가리지 않는지 확인한다.
7. `candidate_move_ms_max`로 착수당 지연을 확인한다. 로컬 spec은 `actTimeout=0`, `runTimeout=2000`초지만 제출 환경 예산은 보수적으로 본다.
8. 후보가 여럿이면 `scripts/gauntlet.py`로 라운드로빈을 돌려 상호 상성과 순위를 본다.

평가는 기본 8 worker 프로세스 병렬이다(`--workers`). 내장 `random`/`first`는 자체 고정 덱을 쓰므로(AGENTS.md 참고) 내장 상대 승률은 절대 지표가 아니라 추세 지표로만 쓴다.

```bash
uv run python scripts/evaluate.py --candidate candidates/h001_example --bundle quick
uv run python scripts/evaluate.py --candidate candidates/h001_example --bundle full \
  --opponents random,first,. --experiment-id 20260805-H001-01 \
  --hypothesis-id H-001 --append-results
```

공개 replay에서 state/action pair를 만들 때는 visualizer action off-by-one을 보정한다. 2026-08-03 episode `89613740`에서 `steps[t].observation`의 응답이 `steps[t+1].action`에 저장됨을 수동 확인했다. 다른 스키마 버전은 한 episode를 다시 확인한 뒤 학습 데이터로 쓴다.

replay 증류 후보(H-006R 계열)는 경기 승률 게이트에 더해 held-out episode 일치율(특히 MAIN)을 함께 본다. 증류 위 하드 오버라이드를 추가하면 일치율이 떨어질 수 있으므로, 오버라이드 추가 후에는 반드시 `distill_replays.py`를 다시 돌려 일치율 게이트를 재확인한다. daily episodes 원본(zip·추출본)은 `data/raw/episodes/`에만 두고 커밋하지 않으며 대회 종료 후 삭제한다.
