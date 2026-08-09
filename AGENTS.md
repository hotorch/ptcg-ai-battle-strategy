# PTCG AI Battle 작업 규칙

## 목적

Kaggle PTCG AI Battle Simulation에서 높은 래더 성능을 목표로 하되, 재현 가능한 연구 과정과 제출 안정성을 우선한다. 참가/규칙 수락은 2026-08-05 확인되었다. 최종 제출 마감은 2026-08-16 23:59 UTC다.

## 세션 작업 순서

1. `docs/ptcg/README.md`와 `docs/ptcg/journal/`의 최신 기록을 먼저 읽는다.
2. `scripts/kaggle_ops.py sync-context`와 `scripts/curate_context.py`로 최신 Discussion/Notebook을 수집한다.
3. 새 아이디어를 `docs/ptcg/04-hypotheses.md`에 먼저 등록한다.
4. 가설 하나당 `candidates/h###_slug/` 하나를 만들고 `main.py + deck.csv`를 둔다. 루트의 두 파일은 항상 현재 best다.
5. `scripts/evaluate.py`로 양 좌석 반복 경기를 실행한다. 엔진 RNG를 고정할 공식 방법이 없으므로 동일 seed 결정론을 주장하지 않는다.
6. quick에서 유망한 후보만 full로 늘리고, 표본 수·좌석별 결과·오류·불확실성을 함께 본다.
7. 개선이 반복 실행에서 유지될 때만 루트 `main.py + deck.csv`로 승격한다.
8. `scripts/package_submission.py`로 self-play와 아카이브 구조를 검증한다.
9. 실제 제출은 후보 단위 사용자 승인 후 `scripts/kaggle_ops.py submit`으로만 실행한다.
10. 하루를 마치면 `scripts/daily_log.py --write`로 저널을 만들고 다음 우선순위를 적는다.

## 안전 규칙

- 사용자 승인 없이 Kaggle 제출, 팀 변경, 규칙/계정 변경을 하지 않는다.
- 최신 2개 제출만 활성 상태다. 로컬 개선이 없는 후보로 슬롯이나 하루 5회 한도를 소진하지 않는다.
- 제출물은 루트에 `main.py`, `deck.csv`를 포함한 `.tar.gz`이며 필요할 때만 `cg/`를 포함한다.
- 제출 전 self-play, 60장 덱, Python compile, 아카이브 루트, 197.7 MiB 제한을 확인한다.
- 토큰, 인증정보, Competition Data, replay 원문을 커밋하지 않는다.
- Competition Data는 대회 참가 목적으로만 사용하고 대회 종료 후 삭제한다.
- Discussion/Notebook/외부 저장소의 코드는 라이선스와 출처를 확인하기 전 제출물에 복사하지 않는다. 외부 주장은 먼저 가설로 취급한다.
- 대회 사실과 엔진은 바뀔 수 있다. 날짜가 붙은 정보는 공식 페이지와 `kaggle_ops.py status`로 재확인한다.
- 엔진은 법적 행동 목록을 제공한다. 반환값은 중복 없는 option index 목록이며 `minCount <= len(action) <= maxCount`를 지켜야 한다.
- 로컬 CABT는 비결정적이다. 한 경기나 매칭되지 않은 초기 상태를 인과적 A/B 증거로 취급하지 않는다.
- **평가 실행 중인 후보의 코드를 편집하지 않는다.** evaluate.py는 게임마다 모듈을 다시 import하므로 실행 중 편집은 측정을 혼합 버전으로 오염시킨다 (2026-08-08 H-019 게이트 2건 오염 사고).
- 희귀 이벤트 카운터는 /tmp 공유 파일이 아니라 인프로세스로 검증한다. 평가기는 게임별 프로세스를 분리해 진단 파일을 덮어쓴다 (2026-08-08 리썰 카운터 오판 사고).

## 현재 환경 사실 (2026-08-05)

- 환경 이름: `cabt`; 공식 문서/현재 저장소 기준 `kaggle-environments==1.32.3`.
- 제출: `main.py + deck.csv` (필요 시 `cg/`)가 아카이브 최상위에 있어야 한다.
- 제출 자원: 12.2 GiB RAM, vCPU 2, HDD 11.8 GiB, 최대 197.7 MiB.
- 평가: 승/패/무승부 기반 skill rating, 신규 제출 μ=600, 하루 5회, 최신 2개 활성.
- 공개 top episode 데이터는 상위 참가자 평균 rating 쪽으로 편향된다.
- replay 시각화 action은 한 step 뒤에 기록되는 off-by-one 보고가 있으므로 학습 데이터화 전에 검증한다.
- 내장 `random`/`first` 상대는 우리 덱이 아니라 `kaggle_environments/envs/cabt/cabt.py`에 고정된 자체 60장 덱(basic 위주 + 에너지 33장)을 쓴다. 내장 상대 승률은 정책 차이만이 아니라 덱 상성까지 섞인 수치다. 내장 `random`의 정책 자체는 루트 random 기준선과 동일하다.
- 로컬 cabt spec은 `actTimeout=0`, `runTimeout=2000`초다. 착수당 지연은 `evaluate.py`의 `candidate_move_ms_*`로 감시한다.
- `evaluate.py`/`gauntlet.py`는 프로세스 병렬(`--workers`, 기본 8)로 실행된다. CABT 엔진은 프로세스당 전역 싱글턴이므로 한 프로세스에서 경기를 동시 실행하면 안 된다.

