# 수정 — 신규 체크아웃/CI 에서 테스트 11개가 돌게 한다

## 문제
`generated/` 는 `.gitignore` 대상(`.gitignore:8`)이라 신규 클론에 존재하지 않는다. 그런데 테스트 11개가 그 아래 산출물을 읽는다. 결과: **저장소를 새로 클론하면 2 failed, 9 errors.** (원 저장소·이관본 양쪽에서 동일하게 재현됨)

- `tests/test_cutout_truth.py` — 9건. `generated/evaluation/full60-20260910-204433` 를 읽는다
- `tests/test_images2_sample.py` — 1건. `generated/samples/images-2` 를 읽는다
- `tests/test_project_layout.py` — 1건. `generated/` 아래 특정 경로가 **존재한다**고 단언한다

## 방침
**필요한 최소 산출물만 추적 경로(`tests/fixtures/`)로 옮기고 테스트가 그것을 읽게 한다.** 테스트를 건너뛰게 만들지 말 것. `pytest.mark.skipif` 로 회피하는 것은 이 작업의 실패다.

## 담당 파일
- `tests/test_cutout_truth.py`, `tests/test_images2_sample.py`, `tests/test_project_layout.py`
- 새로 만들 `tests/fixtures/` 하위
- 필요 시 `scripts/audit_cutout_truth.py` (경로 해석만. 판정 로직은 건드리지 말 것)

## 1) `test_cutout_truth.py` (9건)
`scripts/audit_cutout_truth.py` 가 케이스마다 읽는 것은 다음뿐이다.
- `<case>/result_summary.json` (약 10KB × 60)
- `<case>/photos/01-hero.*` (합계 약 15MB)
- 파일럿 루트의 `run_index.json`
- 원본 이미지 — `run_index.json` 의 `image_path` 가 가리키며, **`data/evaluation/cma_real_v1/images/` 는 이미 git 에 있다.** 확인하고 그대로 쓸 것

`detail_page.png`(1.8MB×60), `react_document.json`, `sections/` 는 **읽지 않는다. 복사하지 말 것.**

→ `tests/fixtures/full60/` 에 위 파일만 복사하고 `PILOT_DIR` 을 그리로 돌린다. 예상 추가 용량 **약 16MB**.

## 2) `test_images2_sample.py` (1건)
`generated/samples/images-2` 에서 **테스트가 실제로 읽는 파일만** 골라 `tests/fixtures/images-2/` 로 복사하고 `SAMPLE_DIR` 을 돌린다. 무엇을 읽는지 테스트를 끝까지 읽고 판단할 것. 안 읽는 파일은 복사하지 말 것.

주의: `ai-fe-response.json` 안에 `"/generated/samples/images-2/detail_page.png"` 같은 **문자열 경로**가 들어 있고 테스트가 그 값을 단언한다. 이것은 **응답 본문의 값**이지 파일 위치가 아니므로 **JSON 내용을 고치지 말 것.** 파일을 어디서 읽을지만 바꾼다.

## 3) `test_project_layout.py` (1건)
이 테스트의 목적은 **저장소 레이아웃 규약**(산출물이 루트에 흩어지지 않고 정해진 곳에 모여 있다)을 지키는 것이다.

그런데 지금은 `generated/samples/live_najeon_box` 같은 **추적되지 않는 산출물이 존재한다**고 단언한다. 추적되지 않는 파일의 존재는 저장소의 성질이 아니라 **작업자 로컬 상태**라, 신규 체크아웃에서는 성립할 수 없다.

→ **"이 경로들이 존재한다"는 단언만 제거**하고, **"루트에 흩어져 있지 않다 / 정해진 위치 규약을 지킨다"는 보장은 반드시 유지**할 것. 무엇을 왜 뺐는지 결과 보고에 적을 것. 보장을 통째로 지우면 실패다.

## 지켜야 할 것
- **단언 값을 바꾸지 말 것.** 60건 분포(`source_composite` 9, `source` 51 등)는 실측 결과다. 픽스처가 같은 파일이므로 같은 수가 나와야 한다. 숫자가 다르게 나오면 픽스처를 잘못 고른 것이니 숫자를 고치지 말고 픽스처를 고칠 것.
- `pytest.mark.skip`·`skipif`·`xfail` 로 회피 금지.
- 판정 로직(`audit_cutout_truth.py` 의 축 A/B 계산)을 바꾸지 말 것.
- `generated/` 의 원본은 그대로 둔다. 복사이지 이동이 아니다.

## 검증 (반드시 이 방법으로)
```
git status --short          # 픽스처가 추적 대상인지 확인
.venv/bin/python -m pytest -q     # 369 passed
# 신규 클론에서도 통과하는지
rm -rf /tmp/ci-check && git clone -q . /tmp/ci-check && \
  cd /tmp/ci-check && <repo>/.venv/bin/python -m pytest -q
```
**신규 클론에서 369 passed 가 나와야 완료다.** 이 결과를 보고에 그대로 붙일 것.

## 보고
`## 결과` 에 옮긴 픽스처 목록과 용량, 테스트별 수정 내용, `test_project_layout` 에서 뺀 단언과 유지한 보장, 위 두 pytest 결과를 적고, 마지막 줄에 `완료: 신규 클론 N passed, 추가 용량 M MB` 출력.
