# PTCG AI Battle 연구 저장소

[English](README.md) | 한국어

[Kaggle Pokémon Trading Card Game AI Battle Challenge](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle)를 위한 재현 가능한 연구 작업공간입니다. 변동성이 큰 래더에서 규칙 기반 에이전트가 어떻게 움직이는지 측정하고, 특정 의사결정 실패를 작고 검증 가능한 수정으로 바꾸는 과정을 기록합니다.

## 대회 개요

이 대회는 Kaggle CABT 시뮬레이션 환경에서 Pokémon Trading Card Game을 플레이하는 AI 에이전트를 만드는 대회입니다. 반복 경기 결과로 rating 기반 순위가 정해집니다. 결과에는 정책 품질과 덱 구성뿐 아니라 상대 풀, 매칭, 경기 수, 엔진의 확률성도 영향을 주므로 제출 한 건의 rating을 곧바로 실력의 정확한 추정치로 해석할 수 없습니다.

이 저장소는 두 가지 연결된 결과물을 다룹니다.

- **Simulation 연구:** [PTCG AI Battle Challenge Simulation](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle)의 후보 에이전트, 60장 덱, 양쪽 좌석 평가, 제출 패키징.
- **Strategy writeup:** [PTCG AI Battle Challenge Strategy](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy)에 제출한 분석 글과 [Kaggle 포럼 코드 공개 글](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/discussion/741120).

최종 writeup에는 동일한 최종 빌드로 제출한 두 인스턴스의 rating **742.8**과 **700.2**, 기록된 래더 종료 시점의 순위 **1,611 / 6,807 (상위 24%)**가 포함되어 있습니다. 다섯 가지 변경을 시험했고 두 가지를 최종 빌드에 남겼습니다. 가장 강한 근거는 동작 검증입니다. 168개 에피소드의 21,975개 의사결정을 비교했을 때, 남긴 수정은 의도한 변경 65건과 관측된 부수 변경 0건을 보였습니다. 다만 로컬 매치 실험만으로 일반적인 승률 향상을 입증하지는 못했으므로 그 한계를 writeup에 명시했습니다.

## 저장소 구조

| 경로 | 용도 |
|---|---|
| `candidates/h036_tempo_boss/` | Strategy writeup에 사용한 최종 H036 에이전트와 덱 |
| `main.py`, `deck.csv` | 현재 루트 연구 기준선. 최종 H036 재현에는 위 candidate 경로 사용 |
| `scripts/evaluate.py` | 양쪽 좌석에서 실행하는 비결정적 CABT 평가 |
| `scripts/package_submission.py` | Kaggle 제출 아카이브 검증·생성 |
| `scripts/kaggle_ops.py` | 맥락 동기화, 상태 확인, 승인 문구가 필요한 제출 작업 |
| `scripts/curate_context.py` | 관련 Kaggle Discussion·Notebook 선별 및 수집 |
| `research_loop/results.tsv` | 실험 결과 원장 |
| `docs/ptcg/` | 대회 사실, 검증 프로토콜, 가설, 제출 기록 |

## 빠른 시작

```bash
uv sync
uv run python scripts/kaggle_ops.py fetch-sdk
uv run python scripts/smoke_test.py
uv run pytest -q
```

후보를 양쪽 좌석에서 짧게 평가합니다.

```bash
uv run python scripts/evaluate.py \
  --candidate candidates/h036_tempo_boss \
  --bundle smoke \
  --workers 2
```

제출 전에 후보를 검증하고 아카이브를 만듭니다.

```bash
uv run python scripts/package_submission.py \
  --source candidates/h036_tempo_boss \
  --output submission.tar.gz
```

로컬 CABT 엔진은 확률적입니다. 반복 실행, 좌석 균형, 표본 수, 불확실성을 결과의 일부로 다뤄야 하며 한 경기나 한 번의 rating으로 인과관계를 주장하지 않습니다.

## 데이터와 제외된 산출물

Competition Data는 대회 참가 목적으로만 사용하며 이 저장소에 재배포하지 않습니다. 리플레이에서 파생한 타 참가자 덱 스냅샷, 원본 트레이스, named-card 메타데이터는 저장소와 Git 기록에서 제외했습니다. 최종 에이전트는 이 파일들 없이 실행됩니다. 허용되는 경우 참가자 자신의 로컬 Competition Data로 분석 파일을 재생성할 수 있으며, 명령은 `docs/ptcg/`에 기록했습니다.

Pokémon 카드명·이미지와 기타 Pokémon Elements는 각 권리자에게 귀속됩니다. 이 저장소의 원본 코드와 문서는 [MIT License](LICENSE)로 공개합니다. 정책 기반은 출처를 밝힌 [Rozen의 V10 notebook](https://www.kaggle.com/code/romanrozen/strong-start-baseline-agent-v10-lb-950)입니다.

## 링크

- [제출된 Strategy writeup](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/writeups/new-writeup-1786172403257)
- [솔루션·평가 코드 공개 Discussion](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/discussion/741120)
- [대회 페이지](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle)
