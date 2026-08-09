# 가설 원장

상태: 대기 / 진행 / 유지 / 보류 / 폐기.

| ID | 상태 | 가설 | 최소 검증 | 출처 |
|---|---|---|---|---|
| H-000 | 유지 | 공식 sample deck과 legal random policy면 로컬·제출 계약을 검증할 수 있다 | self-play smoke | 공식 sample agent / CABT docs |
| H-001 | 보류 | 공개 Mega Lucario 덱에 독립적인 generic legal-action scorer를 적용하면 random policy보다 강하다 | random/first 양 좌석 quick, self-play | Kiyota Mega Lucario sample (927 votes); 래더 369.8로 수렴, H-006R로 대체 |
| H-002 | 보류 | 비-ex attacker를 포함한 anti-Crustle 구성이 Mega Lucario 단일 공격축보다 메타 안정성이 높다 | H-001 및 random/first 양 좌석 quick | Simple Baseline + Matchup Tests (244 votes); Crustle ability |
| H-003 | 보류 | Dragapult의 200 damage와 bench counter 분산을 우선하는 덱이 단순 prize-race에 유리하다 | H-001 및 random/first 양 좌석 quick | Kiyota Dragapult sample (334 votes) |
| H-004 | 보류 | 공개 best-5th Alakazam 덱은 one-prize damage-control 축으로 ex 중심 메타에 강하다 | H-001 및 random/first 양 좌석 quick | Rule-based Alakazam, claimed best 5th (89 votes) |
| H-005 | 유지 | Crustle·Great Tusk library-out 덱은 direct-damage 정책과 다른 승리 조건으로 포트폴리오 가치가 있다 | H-001 및 random/first 양 좌석 quick | LibraryOut w/ Crustle & Great Tusk, claimed max Elo 1208 (10 votes) |
| H-006 | 대기 | 현재 1위 팀명으로 기록된 공개 Lucario 덱 변경(Ultra Ball·Judge·Wally's Compassion)이 H-001의 안정성을 높인다 | 동일 정책으로 H-001 및 대표 상대 풀 양 좌석 quick | 2026-08-03 top episode `89613724` |
| H-007 | 진행 | 상위 Grimmsnarl replay에서 추출한 deck-specific 선택 규칙이 generic scorer보다 강하다 | off-by-one 보정 후 held-out action agreement, 대표 상대 풀 양 좌석 quick | 2026-08-03 top episodes 12개 표본 |
| H-008 | 대기 | 공개 상위 Crustle·Mega Kangaskhan control 구성이 H-005 Great Tusk library-out보다 현재 메타에 강하다 | H-001·H-004·H-005 및 공개 덱 상대 양 좌석 quick | 2026-08-03 top episodes `89613656`, `89613742` |
| H-009 | 보류 | 셋업 요구가 낮고 에너지가 두꺼운 덱(내장 basic 덱 유형)이 정책 수준과 무관하게 로컬 라운드로빈을 지배한다 — 에너지 밀도·일관성을 우리 덱 큐레이션 축으로 삼는다 | 내장 덱+generic scorer 후보를 gauntlet에 추가해 전 후보 대비 quick | 20260805 gauntlet: 내장 first 71%·random 61%로 전 후보 상회 |
| H-011 | 진행 | 증류 정책 3종이 래더 ~500에 수렴한 것은 정책 클래스의 천장이다 — 공식 search API(search_begin/step)로 결정화 턴 탐색(내 덱 정확 복원 + 상대 메타 시그니처 샘플링 + 증류 프라이어 move-ordering + 상대 응수 greedy 롤아웃 블렌딩)을 하면 증류를 넘는다. 단 최악 상성(Lucario)에서는 모방이 탐색보다 강해 매치업 적응형 전환을 쓴다 | full 500 게이트: 증류 64.2% 초과, 오류 0, 착수 예산 내; 래더 실측으로 최종 판정 | search API 스파이크, H011-01 full 65.2%(Lucario 5% 결함→적응형 수정) |
| H-014 | 진행 | 손튜닝 평가는 어빌리티류 지연 가치를 못 본다(Majkel ABILITY 일치 14%) — replay 20만 상태의 (상태특징 20종, 승패) 로지스틱 가치함수(held-out AUC 0.736)로 탐색 평가를 교체하면 강해진다 | 스파링 61.7%(vs 손튜닝 탐색, 60경기), ABILITY 일치 31%로 2배, 미러에서도 증류 상대 57.5% — fallback 제거. full 500 게이트 진행 중 | scripts/train_value.py, H013 스파링 |
| H-013 | 유지 | 다중 결정화 투표(K=3)+예산 3.4배 — 로컬 풀 포화(89.5% ≈ H-012 88.75%)로 강도 차이는 미검출, 가치함수의 기반으로 흡수 | 비-미러 400경기 full 완료 | H012 대비 A/B |
| H-012 | 진행 | 500~600 밴드는 샘플덱(격투) 밀집이라 Lopunny는 구조적 약점 세금을 낸다 — H-011 탐색 아키텍처를 격투 세금이 없는 최강 덱(Majkel Lucario, 08-05에도 64.3%)에 이식하면 두 축의 이점이 결합된다 | quick 81.3%(증류 Lucario 60%·탐색 Lopunny 85%), full 500 게이트 후 래더 A/B | H-011 아키텍처 + majkel 524 episodes 재증류(MAIN 45.9%) |
| H-010 | 진행 | 래더 수렴 500대(v1 521/v2 491, 700 미만)로 판정 규칙 발동 — Mega Lopunny 증류(순수형 636g 54.2%, Froslass 혼합형 572g 57.0%, 표본 합 1,208g로 Majkel의 5배)가 H-006R를 대체한다. 좌석 필터 실험 결과 승리좌석/상위파일럿 필터보다 전체 좌석이 held-out 일치율 우위(순수 40.6%, 혼합 46.2%) | held-out MAIN 45%+(혼합형 충족), H-006R·H-005·재현 메타 상대 quick→full 게이트, 오류 0 | 2026-08-04 daily zip, 래더 A/B 실측 |
| H-006R | 진행 | 1위 Majkel1337의 Lucario 덱(H-001에서 Ultra Ball·Judge·Wally's Compassion 3종 교체)에 replay 증류 정책(문맥별 option 우선순위 + terminal action 후순위 + Lucario 전용 규칙 + generic fallback)을 얹으면 H-001/H-005를 압도하고 래더에서 700+에 도달한다 | held-out MAIN 일치율 45%+, H-001·H-005 상대 양 좌석 100경기+에서 60%+, 핵심 매치업 40% 미만 없음, 오류 0 | 로컬 게이트 전부 통과(MAIN 45.0%, 합산 73%, 최저 매치업 50%, 오류 0), 20260805 제출 — 래더 수렴 대기 |
| H-016 | 진행 | 일일 재학습(3일치 가치함수 AUC 0.742 + 증류 표 + 메타 프라이어 2일 합산)만으로 가치함수 도입급 개선이 재현된다 — 데이터 갱신을 일일 루틴으로 | 스파링 vs H-014 61.7%, 래더 38경기 598.8 (H-014 510.6 대비 +88) — 래더 실증 | 08-06 daily zip |
| H-017 | 진행 | 래더 ~600 수렴의 병목은 플레이 체인 절단이다: 승자 대비 핸드 카드 사용 절반(8.8 vs 17.8/게임), 하위 선택은 증류 폴백(55.7%)이 결정, 시간 예산 실사용 5~20%. 하위 선택에도 탐색을 적용하고 overage 잔량 적응형 예산(5초/2400노드)을 쓰면 meta0 상성(0W-5L)이 뒤집힌다 | 승자 결정 반사실 프로브 PLAY 재현율 상승 + 스파링 vs H-016 ≥58% → 제출 | meta0 패배 5경기 + 92 luc-vs-meta0 episode 포렌식 |
| H-017b | 진행 | 하위선택 탐색의 역효과(1턴 지평선이 즉각 이득만 fetch)는 3지평 리프(내턴종료+응수후+내다음턴 롤아웃)로 풀린다 | meta0d 증류봇 ≥60% + 미러 무회귀 → 제출 | meta0d 67.5%(H-016 52.5%), TO_HAND 프로브 44%, 래더 29경기 703(역대 최고) — 55323710 |
| H-017c/g | 기각 | 예산 스케일링 단독(8s/4800n·6s/3000n)은 개선 없음 — 4번째 스케일링 무효 | meta0d ≥70% | 67.5%/57.5% — h017b와 동급 이하 |
| H-017d | 진행 | H-015 응수 테이블은 MAIN 정책 블렌드로는 무효였지만 탐색 리프의 `_greedy_reply` 응수 모델로는 유효 — 같은 데이터도 주입 지점이 결정한다 | meta0d ≥70% + 미러 ≥45% | meta0d 75.0%, 미러 45.0%, meta2 100%·grimmsnarl 97.5% — 제출 55326028 + 복제 55327512 |
| H-017e | 기각 | 증류 표를 `_greedy_self` 자기 롤아웃에도 쓰면 롤아웃 정확도가 오른다 | meta0d ≥70% | 65.0% — generic scorer 유지 |
| H-017f | 기각 | 응수 모델 위에서는 예산 스케일링(8s/4800n)이 유효해진다 | meta0d ≥70% + 미러 ≥45% | meta0d 80.0%(최고)였으나 미러 37.5%로 기각 — meta0 특화 vs 미러 열세 트레이드오프 |

새 아이디어는 코드보다 먼저 한 행으로 추가한다. 외부 점수는 우리 로컬 결과와 섞지 않는다.
