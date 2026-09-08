# 2026-09-08 재스캔 (계획상 9/6분) — 초안 2 → 초안 3 반영 지시서

스냅샷: `context/kaggle/snapshots/20260908T032338Z` (제목만; 본문은 브라우저 수동 열람). 8/31 이후 신규 토픽 12건.

## 규모·규정 (Strategy 페이지 실측 9/8)

- **Strategy 679팀 / 747명 참가** (9/2 570 → 9/8 679). Finalist 8팀 = **1.2%**.
- Writeups 탭 목록은 "Team 1…~680"이 전부 SUBMITTED·비공개("Viewable at Hackathon close") 표시 — 참가 팀 수와 일치하므로 실제 제출 수가 아니라 팀 슬롯일 가능성. 실제 제출 비율은 마감 후에만 확인 가능.
- 마감 표시: **Sep 14, 2026 08:59 KST** (= 9/13 23:59 UTC, 기존 기록과 동일).
- **우리 계정에 빈 "New Writeup" DRAFT 3개 존재** (8/31~9/2 폼 실측 부작용). 팀당 writeup 1개 규정이므로 **제출 전 빈 draft 정리 필요**. 관련 버그 신고(739855, 9/7): 제출 완료된 writeup이 "ssssssadasfsd" 제목의 draft 2개로 덮여 사라졌다는 보고 — **제출 후 반드시 Writeups 탭에서 SUBMITTED 상태를 재확인**하고 스크린샷 보관.
- 팀 구성 공지(738924/738925): Strategy 팀 구성은 Simulation과 동일해야 함. 솔로라 해당 없음.

## Kaggle 스태프 발언 — 채점 가중치 (인용 가치)

- **Addison Howard (738058, 9/4)**: 시뮬 미참가 팀은 "your simulation score is weighted highly enough that it would effectively be a public contribution." 10일 전 댓글: "a significant portion of your score is based on the performance of your agent." → **⑤ 항목의 실질 가중치가 9문항 균등보다 크다**는 공식 시사. 우리 top 24%는 약점이며, 이를 상쇄할 유일한 축은 나머지 8문항의 밀도.
- **Addison Howard (738791 댓글, 9/3)**: "Future simulations will use Bradley-Terry at the end… For this competition, should you submit to the Strategy competition, your final leaderboard score is an input to the final score, and **you are welcome to note any perceived randomness/variance in the final ranking as a part of your writeup**." → §4 서사(빌드=분포)를 공식이 초대한 셈. **초안에 한 문장 인용 완료(9/8)**.
- 리더보드 정리(부정행위 팀 실격) 공지 — 8/31 이후 순위 변동(1,649→1,611)의 일부는 퍼지 효과. private LB 확정 시점은 미공지("When will the private leaderboards be finalized?" 미답).

## 신규 공개 솔루션

- **739241 15위 (ntumlnoob, 9/4, 37v)**: 7.5M 파라미터 recurrent actor–critic, 분산 population self-play, BC 없음, 런타임 탐색 없음, ~5.5B 결정·RTX 4090 ~5 GPU-days. Slowking/Dragapult 스페셜리스트. **"상세 리포트는 Strategy writeup에서"** 예고 → 상위권 writeup은 기술 밀도가 매우 높을 것. 평가 절: 동일 덱·좌석 교대 paired schedule로 정책 개선을 덱/좌석 운과 분리 — 우리 §6과 같은 철학이나 규모가 다름.
- 739956 492위 BC→RL, 739022 191위 IL(덱 312), 738633 369위 Ogerpon consensus replay learning, 739219 589위 bronze — 중하위권도 학습 기반 서사가 다수. 룰베이스+실험방법론 서사는 차별화되나, "학습 시스템 없음"이 ②에서 불리하게 읽힐 위험은 여전.
- 739417 공식: Round 2 카드 리스트 공개·Playground 예정 (writeup 무관).

## 초안 3 반영 체크리스트

| # | 항목 | 상태 |
|---|---|---|
| 1 | §4 Kaggle 스태프 BT·variance 발언 인용 | ✅ 9/8 |
| 2 | 빈 draft 3개 삭제 후 제출 | 사용자 작업 (9/11) |
| 3 | 제출 후 SUBMITTED 상태 재확인 + 스크린샷 | 9/11 |
| 4 | 최종 레이팅·순위 재측정 (A4) | 9/10 |
