# 세대별 아블레이션 표 (Writeup §3/§5 자산, 2026-08-08 기준)

| Generation | Key change | Local gate | Ladder converged |
|---|---|---|---|
| H-000 random baseline | legal-action random | 10% vs random/first | ~370 |
| H-006R distilled policy | replay-mined selection table | 77% vs 5-pool | 491–521 |
| H-010 Lopunny redistill | 2-day data refresh | 64% vs 5-pool | 485–571 |
| H-011 turn search | determinized search + distilled prior | 67% vs 5-pool | 543 |
| H-012 search on Lucario | search + mirror-adaptive fallback | 79% vs 5-pool | 587–609 |
| H-014 learned value | + value function (AUC .736) | 84% vs 5-pool | 512 |
| H-016 3-day retrain | data refresh only | 62% sparring vs H-014 | 601 |
| H-017b subselect search | search all subselections, 3-horizon leaf | 67.5% vs meta0d gate | 667 |
| H-017d reply model | opponent reply table in leaves | 75% vs meta0d gate | 634 |

주: "Local gate" 열은 세대마다 기준 풀이 다르므로 열 내부 비교만 유효(각주로 명시할 것).
로컬-래더 괴리 사례(H-014 84%→512, H-017d 75%→634 vs H-017b 67.5%→667)는
"로컬 평가의 한계와 비포화 게이트 설계" 서사의 핵심 증거로 §2에서 사용.
