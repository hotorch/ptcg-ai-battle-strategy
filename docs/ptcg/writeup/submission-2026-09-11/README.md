# Strategy Writeup — 업로드 준비본 (2026-09-13 수정)

**실행 절차는 [HANDOFF-upload.md](HANDOFF-upload.md) 하나를 따른다. 기존 제출을 Edit한다.**

- `body.md`: 8개 섹션의 수정 본문. TV와 모집단 귀속 정정, 덱 운용 설명 보강.
- `gallery/`: 본문 첫 등장 순서 **A → B → E → C → D**, 총 5장.
- `gallery-captions.md`: 캡션 전문과 표본·출처·비교 한계.
- `deck.csv`: 실제 최종 H036 덱, ID 60줄. **루트 덱과 다르므로 반드시 이 파일 사용.**
- `deck-reference__v01__named-counts.csv`: 같은 60장의 카드명·수량·역할. Kaggle 첨부용이며 Git에서 제외했다.

제목 유지: **The Ladder as the Object of Study**.
마감 기록: 2026-09-13 23:59 UTC (= 9/14 08:59 KST). 실제 업로드 시 UI 마감도 확인한다.

현재 상태: **2026-09-13 Kaggle 수정본 Update Submission 완료, Submitted! 확인.**
본문 UI 1,853 words, 그림 5장 A→B→E→C→D, 덱 파일 2개와 캡션 전문 첨부.
Kaggle 이미지 제목은 저장 시 255자 제한이 있어 짧은 설명을 사용하고 `gallery-captions.md`를 별도 첨부했다.

## 수정한 핵심

- TV에 Other 포함: 8/04 0.426, 8/15 0.370, 8/21 0.393. 전체 분포가 계속 수렴한다는 결론 철회.
- 24.9%·29.2%는 상위 풀의 여러 Alakazam 파일럿 성적임을 명시. 불명확한 40.3% 추정 삭제.
- A: 실제 탐색·fallback·표본 재검증 로직. B: 오래된 8.3 별표 제거, 실험 계열/동일 빌드 구분. E: 경기 순번 비교로 정정.
- 본문: 덱 수량·역할과 140HP 예시, 관측된 동작 변화와 승률 향상 입증을 구분.

## 재생성 (프로젝트 루트에서)

```bash
uv run python tests/test_report_figures.py
uv run python scripts/report_figures.py cascade
uv run python scripts/report_figures.py dist
uv run python scripts/report_figures.py meta
uv run python scripts/report_figures.py convergence
uv run python scripts/report_figures.py matrix --runs research_loop/runs/20260813T225422Z__20260814-H036-02.json research_loop/runs/20260813T225501Z__20260814-H036-01.json
```

원본 입력은 기존 로컬 Competition Data다. GitHub에는 넣지 않는다.
생성 결과는 `docs/ptcg/figures/`에 쓰인다. 재생성 후 아래 대응으로 gallery에도 복사해야 한다.

| 생성 파일 | 업로드 파일 |
|---|---|
| fig_cascade_surgeries.png | A_cascade_surgeries.png |
| fig_build_distribution.png | B_build_distribution.png |
| fig_convergence.png | E_convergence.png |
| fig_meta_convergence.png | C_meta_convergence.png |
| fig_seat_matrix.png | D_seat_matrix.png |
