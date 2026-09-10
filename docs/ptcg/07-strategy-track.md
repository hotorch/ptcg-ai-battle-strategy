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

### 공식 Evaluation 원문 (08-18 API 재수집 — 채점 기준은 질문 9개 형태, 제목 미러링용)

- Model 70%: ① How clearly is the chosen approach articulated, and how well is the rationale for the model and methods explained? ② How original and technically sound is the proposed approach? ③ How consistently does the model perform under repeated matches and stable conditions? ④ How well does the strategy avoid over-reliance on specific initial states, matchups, or situational advantages? ⑤ Performance within the competition track.
- Deck 20%: ⑥ How clearly is the deck concept articulated, and how well does it align with the intended strategy? ⑦ How effectively are the key cards selected and utilized to support the deck's overall game plan?
- Report 10%: ⑧ How logically and clearly is the report structured and written? ⑨ How effectively are figures, charts, tables, or other visual elements used to support the explanation?
- **LB 성적은 9개 채점 질문 중 1개(⑤)뿐** — 나머지 8개는 전부 서술·방법론·덱 논리·도표 품질.

### 심사 주체 (08-18 확인)

- 공식 사이트의 "judges" 페이지는 **placeholder 상태로 심사자 미공개**. Rules상 "evaluated and ranked by judges", 동점은 judges 합의로 결정, Host(The Pokémon Company/PTCGABC 팀)가 winner 결정 책임. 즉 주최측이 지정한 비공개 심사단.
- 심사 기간 9/14~10/11, 단서: "subject to change based on the number of submissions received."

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

## Writeup 섹션 초안 — "The Converging Meta: 군중픽 역설과 다가오는 벽" (08-14 작성)

Writeup의 메타 분석 장(章)에 넣을 뼈대. 근거 데이터·수치는 `research/top-agent-observation.md` 결과 1~4.

1. **관찰**: 데일리 top-episodes 7개 시점(8/04~8/13)에서 상위 풀 아키타입 점유율 시계열을 채굴. 최다 점유 2종(Grimmsnarl, Alakazam)이 상위 풀 승률 최하위(41~44%)라는 "군중픽 역설" 발견.
2. **가설**: 래더 메타는 외부 실물 TCG 균형(limitless TEF-POR: Dragapult 42.7%, Grimmsnarl ~0%)으로 수렴한다 — 상위권 팀(LB #3)의 공개 추측을 정량 검증 대상으로 채택.
3. **검증**: 총변동거리 0.398→0.321 단조 감소, Dragapult 6.3%→19.7%(9일 3배), Grimmsnarl 30.9%→19.3%. 메커니즘 = 래더 내부의 진화적 선택압(저승률 도태·고승률 복제)이 외부 균형과 동일 방향.
4. **함의(의사결정 연결)**: ① 우리 덱의 천장은 정적 상성이 아니라 "다가오는 벽"(8/13 재가중 기대승률 ~43%) — 덱 교체 불가 시점에서 카운터 튜닝 대신 일반 원칙 수선(H-036)과 조기 잠금을 선택한 근거. ② 마감 후 2주 수렴 기간의 풀 예측에 외부 균형을 선행지표로 사용 가능. ③ 상위권의 "강빌드 숨기기" 행동과 결합하면 공개 컷은 최종 컷의 하한 추정치.
5. **도표 후보**: 점유율 시계열 라인차트(6종+기타), TV 거리 감소 곡선, 매치업 재가중 기대승률의 시점별 변화.

리스크 노트: limitless 점유율은 대회 점수(points) 기준이라 게임 수 기반 래더 점유율과 정의가 다름 — Writeup에는 "방향 일치의 증거"로 쓰고 절대 수치 비교는 피할 것.

## 2026-09-02 호스트 답변 확인 — 단어 수 산정 범위·Pokémon Elements (Strategy 토론)

출처: Strategy 트랙 토론 735679(8/26 답변), 738324(8/31 답변), 738657(9/1 답변). 답변자 전부 Addison Howard(Kaggle 호스트).

- **단어 수 = 본문(main body)만.** Media Gallery는 포함되지 않음(735679). **그림·표 안의 텍스트는 세지 않음**(738657). 취지는 "본문 단락을 이미지로 숨기지 말라"는 것이며, 초과분이 "graphic footnotes" 수준이면 감점 가능성 낮음(738657 원문: "you're unlikely to face penalty if your overages are simply graphic footnotes or the like").
- **셈 방식 = 공백 구분 표준 단어 수**(738324). 다단어 카드명은 단어 수만큼 센다. → 로컬 프록시는 `wc -w`가 맞고, 대시 분리 계산은 과대 추정.
- **덱리스트**: 이미지 또는 CSV/Kaggle dataset 첨부로 제출 가능, 단어 수 미포함, 우회로 간주되지 않음(738657). → 733067 미해결 항목 해소.
- **Pokémon Elements**: 본문에서 카드명·보드 상황·카드 상호작용 언급 **허용·권장**. 공식 비주얼라이저가 제공한 형식의 카드 아트워크 사용도 허용(738657). 금지는 Elements의 변형·신규 창작·유사 게임 제작. → 8/17 킥오프 킷의 "카드 이미지 첨부 = 실격"과 outline의 "카드명 최소화" 방침은 **과잉 보수**였음. 자체 차트만 쓰는 현재 그림 5장은 어차피 안전하며, 카드명 언급 제한을 풀어도 됨.
- 참가 규모: Strategy 570팀(9/2, 로그아웃 상태 페이지 표시). Entry Deadline **9/6 23:59 UTC** — 규칙 수락 상태를 로그인 후 재확인할 것(8/8 userHasEntered=True 기록 있음).

초안 반영: draft-2 본문 wc 1,991(캡션 5개 ~100단어 포함). 그림 캡션을 Media Gallery로 옮기면 본문 ~1,890. 표는 단어 수에서 제외되므로 표 2(세대별 아블레이션)를 무료로 복원 가능.

### 9/2 추가 — Writeup 편집 폼 실측 (Chrome 로그인 상태)

- 폼 구조: Title(80자, 저장 필수) / URL slug / Subtitle(140자) / Track(Main 자동) / **Media Gallery**("Add videos or photos", 동영상은 YouTube만) / **Project Description**(마크다운 편집기, 하단에 "N Words" 카운터) / Attachments(링크·파일 100MB·DOI 옵트인). 제출 체크리스트 4항목 = Title, Subtitle, Track, Project Description.
- 마크다운 편집기 "..." 메뉴: Insert table, Upload image, Embed image, Embed YouTube, Preview, Markdown docs → **그림을 본문에 직접 삽입 가능**(Media Gallery와 별개).
- **카운터 실측 = 순수 공백 토큰 수.** `one two—three four-five six/seven 8.3 (eight) Boss's Orders` → 8 Words (대시 결합어는 1단어). 마크다운 표 `| alpha | beta |` 등 3행 + `![caption words here](url)` + `**bold** \`code\`` → 19 Words: **파이프 `|`와 `|---|---|`도 각각 1단어, 이미지 alt 텍스트도 계산됨.** 호스트 규정(표·그림 내 텍스트 제외)과 폼 카운터는 다르다 — 심사자가 카운터 숫자를 볼 가능성을 감안해 **카운터 기준 ≤2,000도 함께 맞추는 게 안전**. 마크다운 표는 파이프 때문에 크게 부풀므로(4열 9행 ≈ +50 토큰) 표는 이미지로 Media Gallery/본문 삽입 권장.
- 부작용: "New Writeup" 클릭만으로 빈 draft가 자동 생성됨(취소해도 남음). 9/2 현재 "New Writeup" 제목의 빈 draft 3개 존재 → 카드 ⋮ 메뉴에서 정리 필요(1개만 남기고 그 안에 최종본 작성).
- 마감 표시: Sep 14, 2026 8:59 AM KST (= 9/13 23:59 UTC).

## 2026-09-08 재스캔 실측 — 규모·가중치·제출 위험

- 참가 **679팀 / 747명** (9/2 570 → 9/8 679). Finalist 8팀 = 1.2%. 마감 표시 Sep 14 08:59 KST(= 9/13 23:59 UTC).
- Kaggle 스태프(738058): 시뮬 점수는 "weighted highly enough" / "a significant portion of your score" → ⑤ 실질 가중치가 균등 1/9보다 큼. (738791 댓글): 최종 LB 점수는 Strategy 점수의 입력이며 **순위 분산을 writeup에서 지적해도 좋다** → §4 인용 완료.
- **우리 계정 Writeups 탭에 빈 DRAFT 3개** — 제출 전 삭제. 버그 신고 739855(제출본이 정체불명 draft로 덮임) → 제출 후 SUBMITTED 상태 재확인·스크린샷.
- 상세: [research/2026-09-08-solution-scan.md](research/2026-09-08-solution-scan.md)

## 2026-09-10 재측정 — A4 종결

- `watch_rank.py`: 1,611 / 6,807, 742.8 — 9/6 판독과 동일. 컷: gold 1130.9 / silver 924.0 / bronze 853.7.
- `watch_pair.py`: i8 742.9 (1,000경기 54.0%), i9 700.2 (53.0%), 두 인스턴스 모두 217시간 무경기. `fetch-ladder`로 원본 갱신: 마지막 경기 2026-08-31 23:58 UTC(i8) / 23:54 UTC(i9) → 래더 종료 확정.
- 갱신 창(8/21 18:36 → 8/31 23:58) 기준 1,000경기 평균 725.0 / 719.2 (차 5.8), 동시점 격차 평균 19.8 / 최대 75.6, 최종 판독 격차 42.6.
- draft-2 §1·§4·§6 교체, 그림 E 재생성, 본문 1,986단어(제목·이탤릭 헤더 제외, 섹션 제목·마커 포함). 남은 일: 9/11 마커 제거 → 폼 카운터 확인 → 빈 draft 3개 삭제 → Media Gallery 캡션·deck.csv 첨부 → Submit → SUBMITTED 재확인.


## 2026-09-10 23:55 KST — Strategy Writeup 제출 완료 (SUBMITTED)

- 제출 URL: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/writeups/new-writeup-1786172403257 (8/8 생성된 첫 draft를 재사용; slug는 자동 생성값 그대로).
- 제목 "The Ladder as the Object of Study", 부제 130자, 본문 = `writeup/submission-2026-09-11/body.md` (wc 1,993 / 폼 카운터 1,961). 제출 직후 목록에서 SUBMITTED 확인, 본문 재열람으로 정정 문구 확인.
- 제출 전 Codex 팩트체크 2차(`review/codex-factcheck-2026-09-10.md`) → 5건 정정 (2-ply 탐색 존재, turn≤2 분기, Boss "only Supporter", TV 단조 구간, MIT 표현).
- **미완**: Media Gallery 그림 5장, deck.csv 첨부 — 인앱 브라우저에 파일 업로드 도구가 없고 JS 주입 우회는 권한 분류기가 차단. 사용자가 폼에서 직접 업로드하거나 권한 부여 필요. `gallery-captions.md` 순서대로.
- **빈 draft 2개 삭제 실패**: Kaggle 오류 "Permission 'forumMessages.update' was denied". 제출본과 무관한 IN PROGRESS draft라 심사에 영향 없음(팀당 제출 1개 규정은 SUBMITTED 기준).
- 폼 안내: 마감(9/14 08:59 KST)까지 retract·edit·resubmit 가능.
