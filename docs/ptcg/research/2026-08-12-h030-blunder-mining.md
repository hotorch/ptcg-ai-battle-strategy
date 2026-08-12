# H-030 블런더 마이닝 — h024b 래더 패배 분석 (2026-08-12)

목표: 현재 best(H-024b light, 포크 룰 정책 + 리썰 창 탐색)의 래더 패배에서 반복되는 결정적 실수를 찾아, 하드 가드레일 규칙 후보를 도출한다. **본 문서는 증거 수집·분석 단계로, 후보 코드는 아직 수정하지 않았다.**

## 데이터셋

- 수집 경로: daily zip이 아니라 **제출별 직접 수집** — `ListEpisodes`(공개 엔드포인트, `report_figures.py fetch-ladder`)로 h024b 5개 인스턴스(55396840, 55398409, 55408461, 55408468, 55442768)의 episode 목록을 받고, replay 원문은 `kaggleusercontent.com/episodes/<id>.json`에서 내려받았다. 좌석 식별은 submissionId로 정확하다(덱 매칭 불필요).
- 저장: `data/raw/episodes/h024b_ladder/` (227 경기 전체, ~800MB, 커밋 금지 대상).
- 규모: **227경기 = 130승 97패 (57.3%)**, 2026-08-10 ~ 08-12 래더.
  - 주의: ListEpisodes의 reward 필드는 6경기에서 미기록(무승부처럼 보임) — replay 원문 rewards로 정정했다. 그중 1경기(91672495)는 **상대의 INVALID 액션 몰수승**. 우리 쪽 시간 초과·INVALID·ERROR는 **0건** (min remainingOverageTime > 500s).
- replay 해석 메모 (재사용 가치): step t의 `action`은 step t-1 observation의 select에 대한 응답. `observation.logs`는 "직전 결정 이후" 이벤트 꼬리이며 대기 중 동일 리스트가 반복된다 → 연속 동일 리스트 dedup 후 병합하면 게임 로그가 복원된다. RESULT(type 23) 로그는 replay에 안 남으므로 종료 원인은 양 좌석 최신 관측(프라이즈·덱·벤치)에서 추론해야 한다.

## 패배 종료 원인 분포 (97패)

| 원인 | 건수 | 비고 |
|---|---|---|
| prize-out (상대 6프라이즈) | 47 (48%) | 절반 이상이 Dudunsparce 미러·Grimmsnarl |
| **bench-out (액티브 KO 시 벤치 0/스프레드 전멸)** | 36 (37%) | 17건이 6턴 이내 돈크. Froslass/Munkidori 스프레드 포함 |
| **deck-out (내 덱 0 → 드로 불가)** | 14 (14%) | 상당수가 접전(5-4, 5-5, 4-4)에서 자멸 |

상대 아키타입별 (227경기): **Dudunsparce(사실상 우리와 같은 Alakazam 리스트의 미러) 53경기 19승 34패(36%)**, Grimmsnarl ex 41경기 49%, Mega Lucario 37경기 84%, Dragapult 18경기 56%, Archaludon 16경기 69%, Kangaskhan 14경기 79%. **레이팅 정체의 최대 단일 요인은 미러(래더 최다 아키타입) 열세다.** 미러 상대 리스트는 우리와 달리 basic 9–10장(+Fezandipiti ex, Shaymin), Enhanced Hammer 4장을 쓴다.

## 블런더 패턴 랭킹 (빈도 × 결정성)

### P1. 저덱 자가드로 deck-out — "이기고 있는데 스스로 덱을 태운다" (14패 중 최소 5건 즉시 결정적)

접전에서 3장 드로 특성·Poké Pad·Hilda를 덱이 바닥나는 순간까지 사용한다. ABILITY-ACTIVATE(select type 9, context 43)에 대해 정책이 **무조건 YES**.

**[H-030 구현 중 정정·보강 (같은 날)]** contextCard 검증 결과 저덱 ACTIVATE의 주범은 Dudunsparce가 아니라 **Kadabra/Alakazam의 진화 시 "Psychic Draw"** (진화할 때마다 YES/NO 프롬프트, 3장 드로)였다. 덱의 3장 드로 특성은 4종 전부(Kadabra 742, Alakazam 743, Dudunsparce 66, Fezandipiti ex 140). 저덱(≤6) ACTIVATE 26건 전수 조사:
- 래더에서 **NO를 답한 10건은 전승** — 전부 리썰 커밋 라인 재생 경로가 답한 것(포크 휴리스틱은 무조건 YES라 NO를 낼 수 없음).
- 포크가 YES를 답한 16건은 8승 8패. 밴 존(deck−prize−1<3)으로 좁히면 **3승 7패**이고, 그 3승도 16~23스텝 뒤의 느린 승리라 드로 의존이 아니다.
- 가드 설계 교훈: `safe_draws`의 can_win_this_turn 탈출구(999)를 ACTIVATE 가드에 쓰면 안 된다 — 잔여 프라이즈 1에서 포크의 킬 추정이 낙관 오판으로 밴을 무력화한다(91680994가 정확히 이 경로로 자멸). 진짜 리썰용 드로는 커밋 라인 재생이 별도로 처리한다.

증거 사례:
- **ep 91680994** (vs Dudunsparce 미러, **5-4 리드 중 패배**): 턴15 덱 3장에서 특성 YES → 덱 0 → 다음 내 턴 시작 드로 불가 즉사. 특성만 거절했으면 공격 턴 1회 추가 = 마지막 1프라이즈 경쟁 유지.
- **ep 91578363** (vs Dudunsparce, 5-5 패배): 턴14 덱 6에서 YES, 턴16 덱 3에서 YES, 덱 1에서 또 YES → deck-out. 상대는 7장 남김.
- **ep 91675332** (vs Dudunsparce, 3-5): 상대 덱 **1장** 남은 상태에서 우리가 먼저 deck-out — 한 턴만 버텼으면 상대가 먼저 죽는 상황.
- **ep 91572969** (vs Chandelure/Comfey 강제드로 밀 덱, **4-0 리드 중 패배**): 상대 Comfey 공격이 우리에게 강제 드로를 시키는 밀 전략. 우리 선택적 드로가 가속 페달을 같이 밟아줌.
- 그 외 스톨 덱(Crustle 3, Spidops 2, Honchkrow 1) 상대 장기전 deck-out 다수 — 패배 경기의 attach-skip/idle 지표는 정상이므로 원인은 순수하게 드로 과다.

**가드레일 스케치 (구현 대상 1순위)**:
```
# lethal_search/fork_policy의 ACTIVATE(YES/NO, context=43) 처리에서
if select.context == ACTIVATE and 특성이 드로류(두두운스파스):
    if my.deckCount <= 6: return NO        # 하드 밴
if select.context == MAIN and option이 Poké Pad/Hilda류 드로:
    if my.deckCount <= 4: 해당 옵션 점수 -inf  # 드로 금지
# 예외: 커밋된 리썰 라인 재생 중이면 허용
```
결정성: 5경기는 거의 확실히 뒤집혔고(리드 중 자멸), 나머지 접전 4-5건도 턴 수 연장으로 승산 상승. **97패 중 5–8패 회수 기대 = 래더 승률 +2~3%p.**

### P2. bench-out 돈크 — 외로운 Abra (36패, 그중 17건 6턴 이내)

시작 핸드에 basic 1장(대부분 50HP Abra)만 있고 후속 basic/Poffin을 못 뽑은 채 상대 첫 공격에 액티브 KO → 벤치 0 즉사. Froslass/Munkidori 스프레드(3건)는 벤치까지 전멸시킴.

증거 사례:
- **ep 91585809 / 91693256** (vs Archaludon, 턴2 패배): 핸드 [Night Stretcher, Dudunsparce×3, Alakazam×2, Hilda] — 진화체만 가득, 합법 플레이 없음(Hilda는 핸드 7장이라 불가), END 강제 → 돈크.
- **ep 91657902** (vs Mega Starmie/Froslass, 턴3): Abra 2마리 전개했으나 스프레드로 동시 KO.
- **ep 91668741** (vs Mega Lucario, 턴3): 동일 구조.

중요한 **음성 소견**: 최종 결정 감사 결과 "벤치 가능한데 안 놓은" 경우는 37경기 중 0건, "미사용 Poffin" 0건, "미사용 딕" 1건 — **정책은 벤치를 성실히 놓고 있다. 이 패턴은 정책 블런더가 아니라 구조(덱의 basic 7장 vs 미러의 9–10장) + 드로 분산이다.** 하드 가드레일로 고칠 수 있는 폭이 작다.

가드레일 스케치 (보험용, 발화 빈도 낮음):
```
if my.bench == 0 and MAIN options에 (basic 플레이 or Poffin) 존재:
    해당 옵션을 다른 모든 옵션(특히 Xerosic 등 핸드 파괴)보다 먼저 강제
```
근본 대응은 덱 수정(basic +2, 예: Dunsparce70 +1·Fezandipiti)이지만 새 덱 레버는 H-028에서 3진 아웃으로 닫혔다. 재개하려면 "리스트 미세수정(±3장)"으로 별도 가설 등록 필요.

### P3. 미러(Dudunsparce/Alakazam) 열세 — 19승 34패 (총 레이팅 손실 최대)

패배 내역: prize-out 21, bench-out 8, deck-out 5. 미러에서 결정 요인:
1. **deck-out 자멸(P1과 동일 기계)** — 미러는 양쪽 다 덱을 태우므로 드로 절제가 곧 승리 조건.
2. 상대 리스트가 Enhanced Hammer 4장(우리 3) + Xerosic 3 + Nighttime Mine으로 우리 Telepath 에너지를 집요하게 제거 — 에너지 6장 체제에서 복구가 밀림.
3. basic 수 차이로 돈크 손실 교환에서 불리.

정책 레벨 가드레일은 P1 적용이 곧 미러 개선. 추가로 "미러 감지 시(상대 討 Abra/Kadabra 관측) 에너지 어태치 우선순위를 basic 에너지부터"는 소프트 후보(Hammer는 특수 에너지만 제거).

### P4. missed lethal — 접전 패배에서 놓친 승리 라인 (엔진 탐색 재검증)

접전 패배 15경기(내 4프라이즈 이상)의 마지막 ~3턴 MAIN 결정 전부를 오프라인에서 h024b 자체 탐색기(`_search_once`, 결정 당 3s×3회)로 재탐색했다.

**결과: 승리 라인 발견 0건 (탐색 결정 수십 개, 결정당 9s = 래더 예산 2.6s의 3.5배).** 접전 패배들은 "리썰을 놓친" 게임이 아니라 상대가 먼저 마지막 KO에 도달한, 이미 진 포지션이었다. 이는 H-029a(창 완화)가 래더에서 개선을 못 만든 것과 정합적이다 — **리썰 기계는 현재 낭비 없이 작동 중이며, 추가 회수 여지는 탐색이 아니라 P1(deck-out)·P3(미러) 쪽에 있다.** (한계: 우리 자체 탐색기로 재검증했으므로 "우리 탐색기의 지평 밖 승리"는 배제 못 함.)

### P5. 선공/후공 선택 — 하드코딩 "항상 후공"의 근거 약함 (전 경기 공통)

IS_FIRST(YES/NO, context 41) 선택에서 정책은 **코인을 이기면 100% 후공**을 고른다. 실측:
- 우리가 코인을 이겨 후공 선택: 107경기 55승 52패 = **51.4%**
- 상대가 코인을 이겨 우리가 선공 강제: 31경기 21승 10패 = **67.7%**
- 상대가 코인을 이겨 우리가 후공: 83경기 50승 33패 = 60.2%

n=31이라 약한 신호(단측 p≈0.10)지만, 뒤집는 비용이 1줄이고 로컬 A/B(quick 게이트)로 즉시 검증 가능하다. 가드레일이라기보다 **무료 실험 후보**.

## 가드레일 우선순위 제안 (H-030 step 2)

| 순위 | 규칙 | 예상 회수 | 구현 위치 | 리스크 |
|---|---|---|---|---|
| 1 | 저덱 드로 밴(특성 NO @ 덱≤6, 드로 서포터/아이템 금지 @ 덱≤4, 리썰 재생 중 예외) | 5–8패/97 | fork_policy ACTIVATE·MAIN 스코어러 | 낮음 — 발화 조건이 좁고 명확 |
| 2 | 벤치0 → 벤치 옵션 최우선 강제 | 0–1패 | fork_policy MAIN | 없음(보험) |
| 3 | 선공 선택 A/B (IS_FIRST=YES) | 불명(+수%p 가능) | fork_policy IS_FIRST | 로컬 게이트로 판정 |
| — | 리썰 창 조정은 **불필요** (P4에서 missed lethal 0건 확인) | 0 | — | — |

검증 프로토콜: 규칙 추가 후 (a) 인프로세스 카운터로 발화 빈도 확인, (b) held-out 일치율 재확인(`distill_replays.py`), (c) vs h024b 60경기 quick→full 게이트, (d) 특히 **deck-out 시나리오 재현 스파링**(Crustle/Spidops 스톨 봇 상대 장기전에서 deck-out율 측정).

## 한계

- 상대 아키타입 표본이 좌석·시간대 편향일 수 있다(5개 인스턴스, 2일).
- "결정성" 판정은 사후 추론이며, 특히 P1의 회수 기대치는 재현 스파링으로 확인해야 한다.
- 미러 열세의 리스트 요인(basic 수·Hammer 4)은 정책 가드레일 범위 밖 — 덱 레버 재개는 별도 가설로.
