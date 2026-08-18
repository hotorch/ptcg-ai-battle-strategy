# My Internal Tooling + Play against my agent! (본문 전문)

- URL: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/discussion/735649
- 저자: Abhyuday (66th) · 게시 2026-08-17
- 수집: 2026-08-18, 브라우저 렌더링 (735649.json에는 메타데이터+댓글만 있음)

---

## The Master Control Panel

에이전트 시대에 가장 유용했던 것은 상위 의사결정을 위한 좋은 툴링. 대부분의 실험을 이 마스터 컨트롤 패널 + Claude Code로 모바일에서 운영. 본인은 패널의 소비자였고, 구동은 전부 Claude가 단순 API로 수행. **"Good evaluation and observability is key for any simulation competition."**

비전: 모든 실험·봇·메타 복제본에 대한 완전한 가시성을 가진 진화하는 컨트롤 패널 — "mini Kaggle". 이를 통해 임의 봇의 실제 리더보드 성능을 **±30 elo 이내로 추정** 가능.

### Local Leaderboard
모든 봇의 강함을 추적하는 단일 마스터 레코드. 아레나에서 경기가 있을 때마다 갱신.

### Arena
임의 수의 봇이 라운드로빈으로 겨루는 토너먼트. 강함·다양성 측정의 최선. **8 CPU 코어를 대회 내내 아레나에 상시 할당**, "현재 최강 봇은 누구인가"를 동적으로 매칭해 측정. 학습 에이전트도 봇의 진짜 강함 판정이 필요할 때 동적으로 토너먼트 생성. 이 대회는 가위바위보 역학이 강해서 모든 봇이 고강도 상대를 만나면서도 카운터에 강건해야 함.

### Playground
인간이 에이전트와 직접 겨룰 수 있는 플레이그라운드 (본인도 자기 봇을 못 이김). 공개 예정. cross/self attention 시각화, 수별 확률·사고·승률 추정을 체스 엔진처럼 표시.

### Submission analytics
제출 후 **30분 내 제출 elo 추정** 가능한 가장 유용한 도구. 답하는 질문:
- 어떤 덱이 나를 이기고 있나?
- 패인은? 덱아웃 / 접전 / 완패?
- 고elo 상대에 약한가, 덱 매치업이 나쁜가?
- 특정 인물에게 지는가? / 아직 상승 중인가?

사례: 최상위 메타에는 매우 강하지만 ~900 elo의 특정 덱에 지며 정체하던 봇 → 패치 후 top 30 진입.

### Meta Analysis
메타 감시로 대회 막판 **Dragapult 메타 상승을 감지·알림 → 2일의 리드타임으로 카운터 학습 → 최종 대 Dragapult 70% 승률**. 크로스-덱 승률표를 계산해 "봇의 상대적 강함" 조정에 사용.

### Conclusion
"Invest in robust and easy to use tools early on. You can't improve unless you know why you're losing. Especially in the agentic era. It took me a day to build, saved me weeks of time and headache."

## 댓글 요점
- (stnick) 로컬 토너먼트 데이터를 학습에 피드백했나? → **승률은 학습 에이전트의 커리큘럼 동적 조정에 사용, 리플레이 자체는 미사용.**
- (shanzhong8) 900 elo 봇에 지는 걸 어떻게 패치? → 대개 특정 덱에 대한 결손. **그 덱을 잘 다루는 강하고 다양한 teacher를 만들어 상대 풀에 투입** (Dragapult 사례가 최대 성공).
