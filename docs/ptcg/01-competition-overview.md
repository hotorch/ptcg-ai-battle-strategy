# 대회 개요

확인일: 2026-08-05.

- 목표: Pokémon TCG의 hidden information·확률·장기 계획 아래 legal option을 선택하는 agent 개발.
- 시작: 2026-06-16 11:00 UTC.
- 참가/팀 병합 마감: 2026-08-09 23:59 UTC.
- 최종 제출 마감: 2026-08-16 23:59 UTC.
- 마감 뒤 약 2주 동안 게임을 계속 실행해 최종 leaderboard를 수렴시킨다.
- 하루 5회 제출, 최신 2개 제출만 활성, 최대 팀원 5명.
- 점수는 승패 기반 Gaussian skill rating이며 점수 차이는 update 크기에 영향을 주지 않는다.
- Simulation 부문 자체 상금은 없고, 별도 Strategy Hackathon 결과와 결합해 상금 심사를 한다.

## 제출 계약

- `.tar.gz`, 최대 197.7 MiB.
- 아카이브 최상위에 `main.py`, `deck.csv`.
- agent 파일은 `/kaggle_simulations/agent/` 아래 배치된다.
- 초기 observation에서 60장 deck ID 목록을 반환하고, 이후에는 legal option index 목록을 반환한다.
- self-play validation 실패 시 제출은 Error 처리된다.

## 공식 출처

- [Competition overview](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/overview/description)
- [Competition data](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/data)
- [Competition rules](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/rules)
- [CABT API documentation](https://matsuoinstitute.github.io/cabt/)
- [Kaggle cabt environment](https://github.com/Kaggle/kaggle-environments/tree/master/kaggle_environments/envs/cabt)

