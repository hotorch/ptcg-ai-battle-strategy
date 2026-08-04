# 환경 구성

```bash
uv sync
uv run python scripts/kaggle_ops.py fetch-sdk
uv run python scripts/smoke_test.py
uv run pytest -q
```

Apple Silicon macOS에서는 `kaggle-environments==1.32.3`의 `libcg.dylib`로 CABT를 로컬 실행한다. Kaggle 제출 패키지는 Linux `libcg.so`를 사용한다.

## Kaggle 인증

인증정보를 저장소에 넣지 않는다. 현재 사용자 계정은 대회 참가/규칙 수락이 확인되었다.

```bash
uv run kaggle auth login
uv run python scripts/kaggle_ops.py auth-check
```

## Competition Data

환경 확인에는 전체 300+ MiB PDF/엔진 소스가 필요하지 않다. 카드 CSV만 필요할 때 내려받는다.

```bash
uv run kaggle competitions download pokemon-tcg-ai-battle \
  -f "EN Card Data.csv" -p data/raw
```

전체 엔진 소스는 simulator 동작을 감사하거나 custom engine을 만들 때만 받는다. 모든 Competition Data는 `data/raw/`에 두고 대회 종료 후 삭제한다.

## 후보 디렉터리

```text
candidates/h001_example/
├── main.py
└── deck.csv
```

후보가 `from cg...`를 사용하면 `fetch-sdk`로 받은 공식 SDK를 로컬 평가에 사용한다. 패키징 도구도 같은 최신 공식 SDK에서 Linux 제출 파일만 가져온다. custom engine 번들은 현재 지원하지 않는다.
