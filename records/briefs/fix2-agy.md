# 수정 — 서빙되지 않는 web 파일이 운영 이미지에 번들됨 (사소 T-6)

## 담당 파일
- `Dockerfile`
- `sglang/Dockerfile`

(다른 워커가 `pyproject.toml` 과 `scripts/` 를 동시에 고치는 중이니 절대 건드리지 마세요.)

## 문제
두 Dockerfile 이 `COPY web ./web` 으로 `web/` 디렉터리 전체를 이미지에 넣는다(`Dockerfile:34`, `sglang/Dockerfile:86`).

그러나 **런타임이 실제로 읽는 것은 두 개뿐**이다.
- `src/detail_page_ai/html_renderer.py:499` → `web/detail_page.html`
- `src/detail_page_ai/html_renderer.py:500` → `web/detail_page.css`

나머지 6개(`ai_input.html/css/js`, `ai_draft_preview.html/css/js`)는 **FastAPI 가 서빙하지 않는다.** `src/` 에 `StaticFiles` 마운트가 없고, 이 파일들을 여는 것은 저장소에서 실행하는 Playwright 테스트뿐이다(`scripts/browser/test_input_page.mjs:5`, `scripts/browser/test_draft_preview.mjs:94`, `scripts/browser/test_draft_preview_remote.mjs:81`).

## 고칠 것
두 Dockerfile 의 `COPY web ./web` 을 **런타임이 쓰는 두 파일만 복사**하도록 좁힐 것.

주의사항:
- 복사 후 경로가 그대로 `/app/web/detail_page.html`, `/app/web/detail_page.css` 여야 한다. `html_renderer.py:20` 의 `DEFAULT_WEB_DIR = PROJECT_ROOT / "web"` 기준이며 `PROJECT_ROOT` 는 `/app` 이다. **경로가 바뀌면 렌더링이 깨진다.**
- `COPY` 로 여러 파일을 한 번에 넣을 때 목적지 디렉터리 표기를 정확히 할 것(끝의 `/` 누락 주의).
- `DETAIL_PAGE_TEMPLATE_PATH` 환경변수로 외부 템플릿을 지정하는 경로는 그대로 동작해야 한다. 그 기능을 제거하지 말 것.
- `web/` 파일 자체는 삭제하지 말 것. 저장소에는 그대로 둔다. 바꾸는 것은 **이미지에 무엇이 들어가는가**뿐이다.
- 왜 두 개만 복사하는지 한 줄 주석을 남길 것.

## 검증
1. `.venv/bin/python -m pytest -q` → **358 passed**
2. 두 Dockerfile 에 대해 `docker build` 는 하지 말 것(빌드 환경이 없고 시간이 오래 걸린다). 대신 `COPY` 줄이 문법적으로 올바른지, 목적지 경로가 `/app/web/` 아래로 정확히 떨어지는지 눈으로 확인하고 근거를 적을 것.
3. `grep -rn "web/" src/` 로 런타임이 위 두 파일 외에 `web/` 아래 다른 파일을 읽지 않는지 다시 확인하고 결과를 적을 것.

## 보고
`## 결과` 에 파일별 `행 번호 · 전 → 후` 와 위 검증 3건의 결과를 적고, 마지막 줄에 `완료: 수정 2개 파일, 테스트 358 passed` 출력.
