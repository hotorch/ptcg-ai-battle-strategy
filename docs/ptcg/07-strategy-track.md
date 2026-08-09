# Strategy Track (상금 부문)

확인일: 2026-08-05. 재검증: 2026-08-08 (공식 페이지 전체 재수집, 아래 "08-08 재검증" 절 참고). 출처: Kaggle API `competitions pages pokemon-tcg-ai-battle-challenge-strategy` (공식 Rules/Overview).

## 핵심 사실

- 상금은 전부 이 부문에 있다: **$240,000 — Finalist 8팀 × $30,000** (304팀 참여 중, top ~2.6%).
- Finalist는 도쿄 오프라인 토너먼트에 초대될 수 있다(규칙상 "may also be invited", 세부 TBD).
- Simulation 참가가 필수 조건. 솔로 참가이므로 팀 동일성 조건은 자동 충족.
- 우승 시 제출물·코드 **MIT 오픈소스 공개** 의무.
- 심사 기간 2026-09-14 ~ 10-11, 결과 발표 TBD.

## 마감

| 이벤트 | 날짜 (UTC) |
|---|---|
| Simulation 팀 병합 마감 | 2026-08-09 23:59 |
| Simulation 최종 제출 | 2026-08-16 23:59 |
| Strategy 참가/병합 마감 | 2026-09-06 23:59 |
| **Strategy Writeup 제출** | **2026-09-13 23:59** |

## 제출물

- **Kaggle Writeup 1개 (팀당 1개만), 2,000단어 이하** (초과 시 감점 가능).
- [Projects 탭](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/projects) → "New Writeup" → 저장 후 우측 상단 **Submit**. 저장만 된 draft는 심사 제외.
- Media Gallery 선택이지만 Report Score가 도표 활용을 평가하므로 첨부 권장.
- **포켓몬 카드 이미지 등 Pokémon Elements 라이선스 위반 이미지 첨부 시 실격.** 카드 스캔 이미지 넣지 말 것. 자체 제작 차트/다이어그램만 사용.

## 채점 기준

| 항목 | 가중치 | 세부 |
|---|---|---|
| Model Score | **70%** | 접근법 설명의 명료성·근거 / **독창성과 기술적 타당성** / 반복 경기 안정성 / 특정 초기상태·매치업 과의존 없는 강건성 / 리더보드 성적 |
| Deck Score | 20% | 덱 컨셉 명확성, 전략 정합성, 키 카드 선택·활용 |
| Report Score | 10% | 논리 구조, 도표·차트·표 활용 |

공식 Overview 명시: 리더보드 상위권은 유리하지만 보장 아님. **중하위권도 깊은 분석·독창성·구조화된 보고서로 높은 총점 가능.**

## 전략적 함의

- 리더보드 6,306팀 중 8등보다 Writeup 304팀 중 8등이 훨씬 현실적. 8/16 이후 4주는 전부 보고서 품질에 투자.
- H-006R(리플레이 증류)은 "1위 복제"로 읽히면 originality에서 치명적. 보고서에서는 증류를 **메타 분석 방법론**(리플레이 마이닝 → 정책 증류 → held-out 일치율 검증)으로 프레이밍하고, 그 위의 자체 개선(tempo fix 등)과 가설-검증 루프(H-001~H-006, results.tsv 원장)를 메인 서사로 세운다.
- Model 70%의 절반이 "강건성" 언어다. 좌석 교대 승률, 상대 풀 다변화, 반복 표본 분산 등 강건성 증거 그림을 8/16 전에 실험과 함께 축적할 것.

## 08-08 재검증 (공식 페이지·디스커션 전량 재수집)

- 채점표·2,000단어 제한·마감·상금 구조 전부 8/5 확인분과 동일. 참가 323팀으로 증가. **우리 엔트리 확인됨(userHasEntered=True).**
- **"Model Score"의 model은 ML을 의미하지 않는다** — 주최측 공식 답변(topic 724094): rule-based/search/heuristic/ML 모두 인정. "strong, robust, well-designed, clearly explained"가 기준. 우리 탐색+증류 하이브리드 서사에 유리.
- **Second Round(도쿄) 진출 팀은 Strategy Competition 결과로 선발** — 주최측 공식 답변(simulation topic 732331). 시뮬레이션 최종 LB는 8/16 마감 후 약 2주 추가 경기로 확정되며 Strategy 결과와 무관.
- Second Round는 BO3, 추가 카드 도입 예정(Expanded 아님, 오리지널 카드 아님), 1라운드와 다른 덱·에이전트 사용 가능.
- Writeup에 첨부한 private Kaggle 리소스는 마감 후 자동 공개된다. 첨부물 설계 시 유의.
- Writeup 제출 시 Track 선택 필수(UI). 저장만 된 draft는 심사 제외 — **반드시 Submit 버튼까지.**
- 미해결 공개 질문(0답변, 추적 필요): 덱리스트가 2,000단어에 포함되는지(733067), Pokémon Elements 허용 범위 — 카드명 텍스트 언급 가능 여부(733690), 채점·상금 세부(733194).
- Winner 의무: 제출물+소스코드 MIT 공개, 솔루션 생성 과정 상세 기술 제출. AMLT(자동 ML 도구) 사용 허용.
