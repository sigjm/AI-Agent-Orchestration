# 작업 — 검수 기록을 산출물로 남기기

## 만들 파일 (이 하나만)
`docs/evaluation/deliverables-review-2026-09-16.md`

## 배경
2026-09-16 에 전체 산출물 검수를 했고, 판정 결과가 `.orchestration/reports/audit-2026-09-16/00-final.md` 에 있다. 그런데 `.orchestration/` 은 `.gitignore` 대상이라 저장소에 남지 않는다. 검수 결과는 산출물로 남아야 한다.

## 할 것

### 1. 본문
`.orchestration/reports/audit-2026-09-16/00-final.md` 의 내용을 위 경로로 옮겨 적는다. **내용을 바꾸지 말 것.** 판정·등급·행 번호·기각 사유를 그대로 유지한다. 다음만 손본다.
- 워커 보고서 원본 4개(`codex.md`, `agy.md`, `agy2.md`, `agy-2.md`)는 `.orchestration/` 에 로컬로만 남는다는 사실을 머리말에 한 줄 적을 것. 저장소에는 이 판정 문서만 남는다.
- 워커 별칭(codex/agy/agy2)은 그대로 써도 된다. 이미 `docs/operations/orchestration.md` 에 나오는 이름이다.

### 2. 문서 성격 표시
이 문서는 **시점 기록**이다. 머리말에 그렇게 적고, 이후 상태가 바뀌어도 이 문서를 고치지 않는다는 점을 한 줄로 남길 것.

### 3. "조치 결과" 절 추가 (문서 맨 끝)
검수 후 실제로 무엇이 고쳐졌는지 커밋과 함께 적는다. 아래가 사실이며, 각 커밋을 `git show --stat <해시>` 로 직접 확인하고 적을 것.

- `cdf33c4` — 치명 C-1~C-4, 불일치 I-1~I-6, 사소 T-1·T-2. 문서 11개 + `.env.example`
- `e0d98b6` — 사소 T-6. `Dockerfile`, `sglang/Dockerfile` 의 web COPY 축소
- `ecebfd1` — 사소 T-3(pytest pythonpath), T-4(`scripts/build_review_page.py` 1,871줄 삭제)
- 검수 중 추가로 잡은 것: 수정 과정에서 `docs/api/be-fe-ai-integration-spec.md:104` 에 diff 아티팩트(`+ ` 불릿)가 들어간 것을 발견해 되돌렸다. `cdf33c4` 에 포함돼 있다.
- **시점 기록 4건은 고치지 않았다**(차수 로그의 권고 문장, round-11 의 12건/13건, round-10 과 full60-runs 의 게이트 버전 차이, sglang-serving-research.md:148 의 산수 오류). 그대로 남긴 이유도 한 줄로.
- 검수 시점 이후 기준 `python -m pytest -q` 와 `uv run pytest -q` 모두 **358 passed**.

### 4. 색인 연결
`docs/deliverables-audit.md` 에 이 검수 문서로 가는 링크를 한 줄 추가할 것. **다른 내용은 건드리지 말 것.**

## 하지 말 것
- `docs/deliverables/experiments/`, `docs/evaluation/` 의 기존 문서, `docs/README.md` 는 건드리지 말 것. `docs/README.md` 는 다른 워커가 동시에 고치는 중이다.
- 없는 사실을 만들지 말 것. 사람 평가 점수는 존재하지 않고, 서버 GPU 실행도 아직 없다.

## 검증
`.venv/bin/python -m pytest -q` → **358 passed**

## 보고
`## 결과` 에 만든 파일과 "조치 결과" 절에 적은 커밋 확인 방법을 적고, 마지막 줄에 `완료: 신규 1개 파일, 테스트 358 passed` 출력.
