# 핸드오프 — Writeup 미디어 업로드 + 포럼 링크 게시

**작성 2026-09-13 03:4x UTC. 마감 2026-09-13 23:59 UTC (= 9/14 08:59 KST).**

브라우저 자동화가 필요한 작업만 남았다. Claude Code 세션에서는 Chrome 확장이 연결되지 않아
파일 업로드 도구에 접근할 수 없었다. 이 문서만 읽고 독립적으로 수행할 수 있게 작성했다.

---

## 0. 전제 — 이미 끝난 것 (다시 하지 말 것)

- Writeup 본문은 **2026-09-10 23:55 KST에 이미 SUBMITTED 상태**다. 새로 만들지 말고 **기존 것을 Edit**한다.
  - URL: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/writeups/new-writeup-1786172403257
  - 제목: `The Ladder as the Object of Study` (변경 금지)
- 계정: Kaggle 사용자 `aisamhottman`.
- 저장소는 공개 완료: https://github.com/hotorch/ptcg-ai-battle-strategy (MIT).
- 구 저장소 `hotorch/Kaggle-The-Pok-mon-Company`는 **비공개 유지**. 절대 공개하지 말 것
  (force-push 이전 커밋에 대회 데이터 파생 파일이 남아 있음).

## 1. 본문 교체

`docs/ptcg/writeup/submission-2026-09-11/body.md`가 최종본이다. **1,999 words (wc -w)**,
Kaggle 폼 카운터 기준 예상 ~1,967.

9/10 제출본 대비 달라진 점 — 반드시 반영해야 한다:

1. **Discussion 737125가 삭제됨**(`[Deleted Topic]`). 이를 인용하던 2개 문장을 자체 기록 출처로
   재귀속했고 참고문헌 목록에서 뺐다. 수치는 그대로다.
2. Discussion 737107은 원저자가 8/24에 덱 라벨을 수정 → `(Discussion 737107, since corrected)`.
3. §8에 저장소 URL을 넣었다: `github.com/hotorch/ptcg-ai-battle-strategy`.
4. 위 증가분 상쇄로 3개 문장을 압축했다.

**절차**: Edit → Project Description 전체 선택(⌘A) 후 `body.md` 전문으로 교체 →
하단 "N Words" 카운터가 **2,000 이하**인지 확인.

## 2. Media Gallery — 그림 5장

파일은 `docs/ptcg/writeup/submission-2026-09-11/gallery/`에 있다. 총 940KB.
**업로드 순서 = 본문 첫 언급 순서. 아래 순서를 지킬 것 (A → B → E → C → D).**

| # | 파일 | 캡션 (그대로 입력) |
|---|---|---|
| 1 | `A_cascade_surgeries.png` | Figure A — the priority cascade with the five surgery sites: two shipped (S1, S5), three passed locally and did not translate (S2–S4). |
| 2 | `B_build_distribution.png` | Figure B — one point per submission, grouped by build. |
| 3 | `E_convergence.png` | Figure E — left: the placement spike and decay; right: the final pair's 1,000-game trajectories. |
| 4 | `C_meta_convergence.png` | Figure C — top-pool archetype shares at 15 dates vs the external equilibrium; throttled-matchmaking window shaded; lower panel, TV distance. |
| 5 | `D_seat_matrix.png` | Figure D — final-build win rate per gate and seat, with sample sizes; two of three gates sit at the ceiling. |

주의:
- 캡션·그림 내 텍스트는 **단어 수에 포함되지 않는다** (호스트 답변 735679, 738657).
- 5장 모두 자체 제작 차트다. 카드 아트워크·보드 스크린샷이 없으므로 Pokémon Elements 위반 소지 없음.
  (호스트 9/12 답변 736603: 보드 상태를 그릴 거면 자체 제작 말고 공식 비주얼라이저를 쓰라 — 우리는 해당 없음.)

## 3. 첨부 — deck.csv

Attachments → Upload Files → `docs/ptcg/writeup/submission-2026-09-11/deck.csv` (246바이트, 60장).

호스트가 명시 허용한 방식이다 (738657, 9/1 Addison Howard):
> "attaching as a csv file/Kaggle dataset to your Writeup is sufficient and wouldn't count against your
> word limit. That would not be considered circumnavigating the limit."

## 4. 제출 및 검증 — 여기서 실수가 나온다

1. Preview로 섹션 제목 8개, 굵게/기울임, 그림 5장 순서를 확인.
2. **Submit(또는 Update) 버튼까지 누른다.** 저장만 된 draft는 심사에서 제외된다.
3. 목록으로 돌아가 **SUBMITTED 배지를 눈으로 재확인**하고 스크린샷을 남긴다.
   - 알려진 버그 739855: 제출본이 정체불명 draft로 덮이는 사례가 보고됨.
4. 본문을 다시 열어 §8의 저장소 URL과 737125 관련 문장이 반영됐는지 확인.

참고: 계정 Writeups 탭에 빈 `New Writeup` draft 2개가 남아 있다. 9/10에 삭제를 시도했으나
Kaggle이 `Permission 'forumMessages.update' was denied` 오류를 냈다. **제출본과 무관하므로
심사에 영향 없다** (팀당 1개 규정은 SUBMITTED 기준). 시간이 남으면 정리하되 실패해도 무시할 것.

## 5. 포럼에 저장소 링크 게시 — 규정 준수용 (중요)

대회 Rule 3.6.b:
> "If you do choose to share Competition Code or other such code, **you are required to share it on
> Kaggle.com on the discussion forum or notebooks associated specifically with the Competition for the
> benefit of all competitors.**"

GitHub에만 공개하면 문자 그대로는 비준수다. Simulation 트랙 디스커션에 새 글로 링크를 남겨야 한다.
선례: Discussion 735444 (rin ichikawa, 8/16)가 레포를 포럼에 공유했고 유지되고 있다.

게시 위치: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/discussion → New Topic

**제목**: `[MIT] Solution repo: treating the ladder as a distribution (1,611th, 742.8)`

**본문 초안**:

```
Sharing our repository under MIT, per the code-sharing rule.

  https://github.com/hotorch/ptcg-ai-battle-strategy

Our final agent is a fork of Rozen's public V10 rule-based agent with two shipped changes; the
repository is mostly the measurement apparatus around it:

- research_loop/results.tsv — the full ledger of 78 experiments
- scripts/evaluate.py — both-seat repeated-match evaluation
- scripts/mine_episodes.py — deck-signature and win-rate aggregation from daily episode exports
- scripts/report_figures.py — one regeneration command per figure

The thing we found most useful: the same build resubmitted seven times spanned 134 rating points,
so we treated every build as a distribution rather than a point, and used that as a rejection rule
on our own changes. Three of five changes we wrote never shipped because of it.

Note on contents: artifacts derived from replay exports (mined decklists, game traces) are omitted
from the repository under the Competition Data terms; README lists them and the command that
regenerates each from your own data.

Happy to answer questions about the measurement setup.
```

게시 전 사용자 승인을 받을 것. 공개 게시이므로 임의로 올리지 말 것.

## 6. 완료 체크리스트

- [ ] 본문을 `body.md` 최신본으로 교체, 폼 카운터 ≤ 2,000 확인
- [ ] 그림 5장 업로드 (A → B → E → C → D), 캡션 5개 입력
- [ ] `deck.csv` 첨부
- [ ] Submit → SUBMITTED 재확인 + 스크린샷
- [ ] (사용자 승인 후) Simulation 디스커션에 저장소 링크 게시
