# 제출과 모니터링

## 패키징

```bash
uv run python scripts/package_submission.py --source .
tar -tzf submissions/packages/<file>.tar.gz | head
```

패키징 도구가 다음을 확인한다.

- `main.py`, `deck.csv` 존재와 compile
- 정확히 60개의 정수 card ID
- self-play 종료와 reward
- 최상위 경로 구조
- `cg` import 시 공식 SDK 포함
- 197.7 MiB 이하

## 상태와 제출

```bash
uv run python scripts/kaggle_ops.py status
uv run python scripts/kaggle_ops.py track-ratings

# 사용자가 해당 후보 제출을 승인한 뒤에만
uv run python scripts/kaggle_ops.py submit \
  --file submissions/packages/<file>.tar.gz \
  --message "YYYYMMDD-H###-nn: 설명" \
  --confirm SUBMIT_PTCG_AI_BATTLE
```

신규 제출은 μ=600에서 시작하고 rating이 수렴할 때까지 노이즈가 크다. 최신 2개만 활성화되므로 stable best와 실험 후보를 한 쌍으로 운용한다. 동일 파일 재제출은 기존 rating을 보존하지 않는다.

