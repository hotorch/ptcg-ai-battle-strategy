# 검증 프로토콜

## 핵심 제약

CABT native engine에는 공식적으로 노출된 RNG seed, 상태 export/import, 동일 초기 상태 replay 방법이 없다. Python random seed만 고정해도 shuffle·setup이 같아진다고 가정하지 않는다.

따라서 후보 비교는 다음 순서를 따른다.

1. `smoke`: self-play 1경기로 계약·crash 확인.
2. `quick`: 상대마다 양 좌석 10경기씩 실행해 방향 확인.
3. `full`: 상대마다 양 좌석 50경기 이상 실행.
4. 후보와 현재 best를 같은 공개 상대 묶음에서 별도로 평가하고, 필요하면 반복 실행한다.
5. 전체 win rate뿐 아니라 좌석별 결과, draw, error, 표본 수, 95% Wilson interval을 본다.
6. 한 matchup 개선이 다른 matchup 붕괴를 가리지 않는지 확인한다.

```bash
uv run python scripts/evaluate.py --candidate candidates/h001_example --bundle quick
uv run python scripts/evaluate.py --candidate candidates/h001_example --bundle full \
  --opponents random,first,. --experiment-id 20260805-H001-01 \
  --hypothesis-id H-001 --append-results
```

공개 replay에서 state/action pair를 만들 때는 visualizer action off-by-one 보고를 확인한다. 원본 action이 다음 step에 저장되는지 한 episode를 수동 검증하기 전에는 학습 데이터로 쓰지 않는다.

