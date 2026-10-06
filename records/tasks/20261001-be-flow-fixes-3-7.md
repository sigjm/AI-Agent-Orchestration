# BE 흐름 재현에서 나온 상세페이지 결함 3~7 — 원인 검증 후 수정

## 배경

BE(develop `5ee438d`)가 보내는 요청 그대로 로컬 AI 서버에 흘려 봤다 (합죽선 사진 1장 + 판매자 입력 3개).
재현 자료는 전부 `<scratchpad>/be-repro/` 에 있다.

- `request-metadata.json` — BE 가 보낸 metadata (user_hints 3개)
- `product_image.webp` — BE 가 보낸 사진 (CDN 1280px **WebP**)
- `submit-log.json` — 초안 응답 전체 (`final_status_body.draft` 에 product·draft·page_plan·react_document)
- `approve-contract-metadata.json` — 승인에 쓴 draft
- `detail_page_from_be_flow.png` — 최종 상세페이지, `assets/` — 그때 만든 사진·섹션
- `ai.log`, `mlx-serve.log` — 서버 로그

**아래 진단은 관리자의 1차 추정이다. 그대로 믿지 말고 코드와 재현 자료로 원인을 직접 확인하라.** 다르면 다르다고 보고하라.

## 고칠 것 5가지

### 3. WebP 원본이 이미지 편집에서 거절된다 (가장 중요)

- 증상: `mlx-serve.log` 에 `[gen] 400: could not decode 'image' (PNG/JPEG supported)` 5회 → 사용 장면·디테일 02~05 생성이 전부 실패하고 원본 크롭으로 대체됨
- 추정 원인: 원본 바이트를 형식 변환 없이 이미지 모델 편집 요청에 넘긴다 (`source_photos.py` 의 생성 호출 → `local_detail_page_ai/runner.py` → `clients.py` 의 `MlxServeImageClient.edit` / `SglangImageClient.edit`)
- 운영 입력은 **항상 WebP** 다 (BE 가 CDN `1280w.webp` 를 내려받아 보냄). 서버(SGLang)도 같은 경로를 탄다
- 요구: 이미지 모델에 원본을 보내기 전에 PNG(또는 JPEG)로 바꾼다. **모든 편집 호출이 거치는 한 곳**에서 고쳐라 (호출부마다 따로 고치지 말 것). 원본 해시 검증(`source_sha256`)은 변환 전 원본 기준을 유지해야 한다
- 테스트: WebP 원본으로 편집을 부를 때 모델로 가는 이미지가 PNG/JPEG 인지 확인하는 단위 테스트

### 4. 색 견본이 hex 값과 다르게 칠해진다

- 증상: 「색과 문양」에서 `한지 베이지 #F5F0E6` 이 회색, `매화 분홍 #E8A0B0` 이 하늘색으로 칠해짐
- 추정 원인: `html_renderer.py:385` 가 `palette-swatch--{item_index % 4}` 순번 클래스로 고정 색(`web/detail_page.css:528-531`)을 칠하고 항목의 hex 값을 쓰지 않는다
- 요구: 항목에 유효한 hex 가 있으면 그 색으로 칠한다(값은 `react_document.py` 의 `_validate_color` 수준으로 검증 — 스타일 주입 금지). 없으면 지금처럼 순번 색. `react_document` 쪽 팔레트도 같은 값을 쓰는지 확인하라 (PNG 와 react_document 가 어긋나면 안 됨)

### 5. 「부채 관리 방법」 아래에 특징 3개가 목록으로 붙는다

- 증상: 초안의 notice 블록은 `items: []` 인데, 최종 PNG 에는 특징 3개가 불릿으로 붙음
- 추정: 빈 items 를 렌더 전 어딘가에서 특징으로 채운다. 어디서 채우는지 찾아라 (`html_renderer.py:409` 의 notice 렌더 자체는 items 만 쓴다)
- 요구: notice 에 판매자 관리 안내만 있고 items 가 비면 목록 없이 본문만 나온다

### 6. 판매자가 준 관리 방법이 warnings(확인 필요)에도 들어간다

- 증상: `submit-log.json` 의 `product.warnings` 에 care_guide 세 문장이 그대로 들어 있음
- 추정: 모델이 `uncertain_information` 에 판매자 문구를 넣고 `validation.py:364` 가 그대로 warnings 로 만든다
- 요구: 판매자 입력(user_hints)으로 이미 확인된 문장은 warnings 에서 뺀다. 프롬프트만 고치지 말고 **코드에서 결정적으로 거른다**

### 7. 품질 두 가지

- (a) 사용 장면 배경에 부채와 무관한 흰 접시가 나왔다 → `prompts.py:886` `build_usage_context_background_prompt` 등 사용 장면 배경 프롬프트를 확인하고 식기·접시 같은 무관 소품을 막는다 (`build_background_prompt` 에는 이미 금지 문구가 있다)
- (b) 「함께 보기 — 전주에서 만든 다른 전통 공예품도 함께 살펴보세요」 추천 블록이 실제 다른 상품 없이 특징만 반복했다 → 존재하지 않는 상품을 권하는 문구를 만들지 않게 한다. 방법(프롬프트·검증·블록 제외)은 원인을 보고 정하되 이유를 보고하라

## 검증 방법

- 전체 `pytest` 통과. 테스트를 약하게 만들거나 임계값을 바꾸지 말 것
- 4·5·6·7(b) 는 **이미지를 새로 만들지 말고** 재현 자료의 draft 와 `assets/` 사진으로 다시 렌더해 전후를 비교한다
- 3·7(a) 만 이미지를 새로 생성해 확인한다. 로컬 모델 서버가 필요하면 관리자에게 요청하라 (지금 꺼져 있다)
- 결과 PNG 는 재현 폴더 아래 새 폴더에 저장하고 경로를 보고하라

## 하지 말 것

- **git 상태 변경 금지** (commit/checkout/reset/stash/restore/switch/branch)
- BE 쪽 문제(승인 형식 불일치, 사진 1장만 전달)는 이번 범위가 아니다. 건드리지 말 것
- FE(`web/ai_draft_preview.js` 등) 연동 작업은 하지 말 것

## 보고 — 이 파일 하단 `## 결과`

항목별로: 확인한 실제 원인(관리자 추정과 같은지), 바꾼 파일·함수, 추가한 테스트, 전후 비교 결과(PNG 경로), 남은 한계.

## 결과

### 실행·검증 요약 — 2026-10-01

- 3·4·5·6·7(a)·7(b)를 수정했다. 관리자 추정 중 6의 경고 저장 위치와 4의 React 팔레트 상태는 실제 코드·자료와 달랐다(아래 상세).
- 전체 검증: `.venv/bin/python -m pytest -q` → **486 passed, 2 warnings in 21.63s**. 시작 시 **460 passed, 2 warnings**였으며, 새 회귀 테스트 26개를 추가했다. 경고는 기존 Starlette/httpx 및 anyio 사용 중단 안내 2건이다.
- `git --no-optional-locks diff --check` 통과. commit/checkout/reset/stash/restore/switch/branch를 실행하지 않았다. 기존 `docs/phase4/*`, `excalidraw-diagram-skill/` 변경은 건드리지 않았다. BE 승인 계약과 사진 전달 방식, FE 연동 JS는 변경하지 않았다.
- MLX Serve `http://127.0.0.1:11234`에서 실제 이미지 요청을 확인했다. 새 텍스트 분석은 수행하지 않았다. 모델 unload와 서버 종료는 하지 않았으며, 마지막 `/v1/models` 조회도 성공했다.

**결과 경로 기준**

아래 상대 경로의 기준 디렉터리(`R`)는 다음과 같다.

```text
<scratchpad>/be-repro/fixes-20261001/
```

- 전체 전후 PNG: `R/before.png` → `R/after.png`.
- 재현 자료의 승인 draft와 SQLite에 보관된 분석 결과를 합쳐 렌더했다. 기존 `assets/objects/`와 대조한 **동일 사진 8장**을 전후에 사용했으며, 4·5·6·7(b) 검증에는 모델 호출·새 이미지 생성이 없다.
- 원본 WebP SHA-256은 전후 모두 `dbef8d2f2898c6c2eb753c9ee2660113ac11074152d7c0234ba434ace4e50bd9`. 사진 8장의 SHA-256도 모두 동일하다. `before-metrics.json`, `after-metrics.json`, `render-audit.json`에 기록했다.
- 전체 렌더 크기는 **774×4154 / 9개 섹션 → 774×3528 / 8개 섹션**이다. 이 비교용 `after.png`에는 기존 사용 장면 사진을 그대로 썼다. 7(a)의 새 배경 검증 결과는 별도 PNG에 있다.

### 3. WebP 편집 입력 거절

- **실제 원인 — 관리자 추정과 일치:** MLX와 SGLang 편집 클라이언트가 WebP 바이트를 그대로 전달했다. 기존 `mlx-serve.log`의 PNG/JPEG decode 오류 5회에 더해, 수정 전 동일 WebP로 MLX에 요청하여 실제 HTTP 400을 재현했다(`R/before-webp-edit.json`).
- **수정:** `src/local_detail_page_ai/clients.py`의 공통 `_prepare_edit_image`를 두 클라이언트의 `edit`에서 사용한다. PNG/JPEG는 그대로 통과시키고 WebP 등 다른 이미지 형식은 Pillow로 디코딩·EXIF 방향 정규화 후 RGB/RGBA PNG로 변환한다. 호출부별 변환은 추가하지 않았다. `source_photos.py`의 원본 해시 계산은 변경하지 않았다.
- **테스트:** `tests/test_be_flow_fixes.py`에서 MLX JSON과 SGLang multipart의 실제 송신 바이트가 PNG인지, WebP의 크기·RGBA 픽셀이 보존되는지, 생성 사진의 `source_sha256`이 변환 전 WebP 해시인지 검증했다.
- **실제 서버 결과:** 1280×851 WebP를 PNG 참조 입력으로 보낸 디테일 02 편집과 사용 장면 편집 모두 **1024×1024 PNG 반환 성공**. 각각 27.45초 / 29.48초. 요청의 입력 형식·크기·원본/송신 해시는 `after-webp-detail-02-request.json`, `after-webp-usage-scene-request.json`에 있다.
- **전후 PNG:** 기존 크롭 대체 사진은 재현 폴더의 `assets/objects/a9/a9b468e232a2c07d8f7ea942e8f25758891b2d581b19dd9a580e106d132255e8.png`. 편집 성공 결과는 `R/after-webp-detail-02.png`, `R/after-webp-usage-scene.png`. 실패했던 수정 전 요청 자체에는 반환 PNG가 없다.
- **한계:** 실제 모델 검증은 MLX에서 했다. SGLang은 전송 경계 단위 테스트로 검증했으며 실제 SGLang GPU 서버에서는 실행하지 않았다. 형식 수용 성공은 생성 모델의 문양·숨은 형상 정확성을 보장하지 않는다.

### 4. 색 견본과 hex 불일치

- **실제 원인 — HTML 추정은 일치, React는 추가 결함:** HTML은 항목의 값을 무시하고 순번 클래스로 회색·흰색·하늘색·짙은 회색을 칠했다. 기존 React 문서는 팔레트 항목과 색 견본 자체를 만들지 않았다.
- **수정:** `react_document.py`의 공통 `palette_swatch_color`가 기존 `_HEX_COLOR_PATTERN`과 같은 #3/#4/#6/#8 형식을 전체 문자열로 검증한다. 유효한 hex만 사용하고, 나머지는 기존 CSS 순번 색으로 대체한다. `html_renderer.py`가 이 값으로 견본을 칠하며, `react_document_builder.py`의 `_palette_items`가 동일한 색·항목을 AST에 만든다.
- **테스트:** 유효한 hex 길이 4종, 잘못된 값·CSS 주입 시도, 순번 대체 색, HTML/React의 네 견본 값 일치를 검증했다.
- **전후 PNG:** `R/before-sections/04-palette.png` → `R/after-sections/04-palette.png`. 베이지·갈색·분홍·검은색이 각각 **#F5F0E6 / #C4A882 / #E8A0B0 / #2C2C2C**로 바뀌었다. Chromium의 computed backgroundColor와 `after-react-document.json`의 색도 동일함을 `render-audit.json`에서 확인했다.
- **한계:** 항목 `value`가 완전한 hex일 때만 적용한다. 색 이름이나 설명문 속의 hex는 추출하지 않고 기존 순번 색으로 처리한다. FE 연동은 범위 밖이므로 AST 값과 서버 HTML을 검증했다.

### 5. 관리 안내에 특징 3개가 붙음

- **실제 원인 — 빈 목록 대체 추정과 일치:** notice 렌더 분기 이전의 `html_renderer.py::_block_items`가 빈 items를 제품 특징 3개로 채웠다. notice 자체의 items 처리보다 공통 대체 로직이 원인이었다.
- **수정:** 특징 대체를 `feature_grid`에만 한정했다. notice의 items가 비면 `<ul>`도 만들지 않는다. 명시된 관리 항목이 있으면 그대로 유지한다.
- **테스트:** 빈 notice가 본문만 렌더되는지, feature 불릿이 없는지, 명시적 notice 목록은 유지되는지 검증했다. React notice는 원래 명시된 items만 사용했다.
- **전후 PNG:** `R/before-sections/08-notice.png` → `R/after-sections/07-notice.png`. 특징 불릿 **3개 → 0개**, 섹션 높이 **371 → 200px**. 판매자 관리 본문은 유지된다. 실제 DOM의 notice 목록 0개를 확인했다.
- **한계:** notice 본문 자체의 사실 여부는 이 수정이 검증하지 않는다. 판매자가 입력한 본문과 명시적 items를 보존한다.

### 6. 판매자 관리 문장이 확인 필요 경고로 중복됨

- **실제 원인 — 관리자 저장 위치 추정과 다름:** SQLite의 `draft_profile.uncertain_information`에는 크기·무게·가격·제작자·원산지와 제외된 AI 문구만 있었다. 판매자 관리 문장 3개는 **`safety_notes`에 저장**되어 있었다. `AiFeProductSummaryDto.from_profile`이 두 필드를 합쳐 warnings로 반환했다. 기존 sanitizer는 seller hints를 받지 않았고, 초안 수정·승인에서도 저장된 hints를 전달하지 않았다.
- **수정:** `validation.py::sanitize_profile_for_render`가 user_hints의 전체 값과 문장을 Unicode NFKC·공백·종결 문장부호 기준으로 정규화해 `uncertain_information`과 `safety_notes` 양쪽에서 일치 문장을 제거한다. `pipeline.py`의 생성·초안 재구성 경로와 `service.py`의 수정·승인 경로에 저장된 user_hints를 전달한다. 프롬프트에도 판매자 관리 안내를 불확실 정보로 분류하지 않도록 명시했다.
- **테스트:** 두 경고 필드, 여러 문장·공백·종결 문장부호 차이, hints가 없을 때 보존, 확인되지 않은 경고 보존, 원본 해시 보존을 검증했다. `tests/test_draft_flow.py`에는 기존에 저장된 잘못된 경고를 주입한 뒤 수정과 승인에서 각각 제거되는 서비스 회귀 테스트를 추가했다.
- **전후 결과:** warnings **9개 → 6개**, 판매자 관리 문장 3개만 제거하고 나머지 확인 필요 경고는 유지했다(`before-metrics.json`, `after-metrics.json`, `render-audit.json`). warnings는 PNG에 노출되는 필드가 아니므로 해당 차이는 JSON으로 검증했다. 관리 안내 본문 유지 PNG는 위 5의 전후 경로와 같다.
- **한계:** 결정적 문자열·문장 일치 방식이다. 모델이 의미는 같지만 다른 문장으로 바꾼 경고까지 의미 추론으로 삭제하지 않는다. 이 경우 확인 필요 항목이 남을 수 있다.

### 7(a). 사용 장면의 무관한 접시·식기

- **실제 원인 — 금지 누락 외에 충돌 지시도 확인:** lifestyle은 일반 `build_background_prompt`가 아닌 `build_usage_context_background_prompt`를 사용했다. 이 경로에 명시적 식기 금지가 없었다. 또한 `background plate`라는 다의적 표현을 반복했고, 빈 배경을 요구하면서 공통 이미지 지시에서는 “제품을 시각적 중심으로 둔다”는 문장·제품 재질/소품 지시를 섞고 있었다.
- **수정:** `prompts.py`에서 배경을 `background photograph`로 부르고 실제 실내·완전히 빈 탁자 지시를 앞에 둔다. lifestyle 배경에서 제품 중심의 공통 mood 문단을 제외하고 자연광·표면 질감·중립 색 지시만 남겼다. plate/dish/bowl/cup/cutlery/serving tray 금지와 `runner.py::MlxServeBackgroundGenerator.generate`의 negative prompt를 보강했다. 참조 사진으로 만드는 사용 장면에도 무관한 식기 추가 금지를 명시하되 원본의 기존 식기는 보존한다.
- **테스트:** 배경/참조 편집의 식기 금지, 실제 요청 negative prompt, 배경 문구의 모호한 `plate` 표현 제거, 빈 장면 지시 우선 배치, 제품 중심 지시가 섞이지 않는지를 검증했다. 기존 프롬프트 테스트의 `background plate` 기대 문자열은 새 `background photograph` 기대 문자열과 `background plate` 부재 검증으로 바꿨다. 다른 검증과 임계값은 줄이지 않았다.
- **실제 생성으로 수정 방향 확인:** 금지어만 추가한 `R/after-usage-background.png`에는 접시가 남았다. 표현/지시 순서를 바꾼 `R/after-usage-background-v2.png`에는 접시 대신 물병이 생겼다. 충돌하는 공통 mood 지시까지 제거한 **`R/after-usage-background-v3.png`는 식기·물병 없이 앞 탁자가 완전히 비었다**(1024×1024 PNG, 10.97초). 참조 WebP 편집 결과 `R/after-webp-usage-scene.png`에서도 원본 부채·박스 외 식기가 없음을 육안 확인했다.
- **전후 PNG:** 기존 접시가 있는 사용 장면 `R/before-sections/05-usage-scene.png`와 위 배경 변형 3개 및 참조 편집 PNG. 최종 배경 프롬프트·요청·수치는 `after-background-v3-prompt.txt`, `after-usage-background-v3-request.json`, `after-usage-background-v3-result.json`에 있다.
- **한계:** 프롬프트의 충돌과 생성 결과를 확인했지만 접시의 원인을 특정 단어 하나로 단정할 수는 없다. 이번 모델/입력의 성공 사례이며, 확률적 생성에서 모든 입력에 소품이 생기지 않는다는 보장은 아니다. 기존 사진을 재사용한 전체 `after.png`의 사용 장면은 새 배경으로 교체하지 않았다.

### 7(b). 실제 상품 없는 「함께 보기」 추천

- **실제 원인 — 모델 문구와 HTML 대체가 함께 문제:** 저장된 page_plan의 recommendation은 실제 상품 항목 없이 `items: []`이고, 다른 전통 공예품을 권하는 본문만 있었다. HTML 공통 items 대체 로직이 제품 특징을 다시 붙였다. 요청/프로필에는 추천을 뒷받침할 관련 상품 목록이 없다.
- **수정:** 프롬프트에서 관련 상품 데이터 없이 다른 상품·공예품을 권하지 않도록 했다. `validation.py::sanitize_page_plan`이 빈 recommendation과 다른/관련 상품을 권하는 recommendation을 제외한다. 초안·최종 HTML·React 문서가 이 검증을 사용한다. 입력에 내용이 있는 제품 자체의 배치·활용 제안은 유지한다. `_block_items` 수정으로 특징을 추천 항목으로 대체하는 문제도 사라졌다.
- **테스트:** 빈 추천과 items까지 채워진 관련 상품 문구가 HTML·React 양쪽에서 제거되는지, 유효한 제품 배치 제안은 남는지 검증했다. 기존 raw-dict page_plan 호출도 DTO로 정규화해 기존 렌더 테스트와 호환시켰다.
- **전후 PNG:** `R/before-sections/07-recommendation.png`와 전체 `R/before.png` → `R/after.png`. 약 455px의 허구 추천 섹션이 제거되었고, DOM과 React 문서에도 해당 섹션이 없다. 실제 상품 데이터가 없으므로 새 상품·링크는 만들지 않았다.
- **한계:** 관련 상품 문구 검사는 한국어·영어의 명시적 표현을 대상으로 한다. 모든 우회 표현을 의미적으로 판별하지 않으며, 이후 실제 상품 추천 기능을 만들 때는 검증 가능한 상품 목록을 별도 계약으로 전달해야 한다.

---

## 검수 — 7(b) 되돌려 보냄 (관리자, 2026-10-01)

3·4·5·6·7(a)는 확인했다(전체 486 passed 재현). **7(b)의 `sanitize_page_plan` 이 정상 추천 블록까지 지운다.**

```
정상: 추천 연출 — "이 작품은 거실 선반 위나 현관 벽에 두면 잘 어울립니다."   → 제거됨 (유지돼야 함)
정상: 추가로 즐기는 방법 — "이 제품은 여름철 장식으로도 쓸 수 있습니다."     → 제거됨 (유지돼야 함)
대상: "전주에서 만든 다른 전통 공예품도 함께 살펴보세요."                    → 제거됨 (맞음)
```

원인: 정규식이 `추천|추가|새로운` 뒤 18자 안에 `작품|제품|상품` 이 오면 잡는다. recommendation 블록의 제목 자체가 "추천 연출"이라 제품 배치 제안이 거의 다 걸린다.

고칠 것:
- **다른 상품을 권하는 표현만** 잡는다 — 예: `다른|관련|연관|유사|비슷한` 이 상품 명사를 직접 수식하는 경우, "함께 살펴보세요/둘러보세요/구매" 처럼 다른 상품 탐색을 권하는 표현. `추천`·`추가`·`새로운` 단독으로는 제거하지 않는다
- 위 두 정상 사례가 **유지**되는 테스트와, 제거 대상 사례가 제거되는 테스트를 추가한다
- 빈 items 인 recommendation 제거는 유지해도 된다

끝나면 이 섹션 아래 `## 결과 2` 에 바꾼 규칙과 테스트, 전체 pytest 결과를 적어라. git 상태 변경 금지는 그대로다.

## 결과 2

### 7(b) 정상 제품 배치 제안 삭제 수정 — 2026-10-01

- **원인 확인:** 검수 지적과 일치했다. 이전 필터가 제목·본문·항목을 한 문자열로 합친 뒤 `추천|추가|새로운`과 뒤쪽 제품 명사를 임의의 문자 간격으로 연결했다. 검수의 두 정상 사례를 포함한 보존 회귀 테스트 8개가 수정 전 모두 실패했다. `남다른 작품` 속 `다른`과 “다른 방향에서 이 작품”도 같은 방식으로 잘못 삭제되었다.
- **변경 파일·규칙:** `src/detail_page_ai/validation.py`의 `_RELATED_PRODUCT_PITCH`, `sanitize_page_plan`을 수정했다.
  - `추천·추가·새로운` 및 영어 `recommended·additional`은 제거 조건에서 뺐다.
  - `다른·관련·연관·유사(한)·비슷한`이 `상품·제품·공예품·작품`을 직접 수식하는 구문만 검사한다. 재현 문구의 “다른 전통 공예품”을 위해 `전통·수공예` 수식어를 허용한다. 영어도 `other·related·similar`와 상품 명사의 직접 연결 및 `traditional·handmade` 수식어로 한정했다.
  - 제목·본문·각 항목의 label/value/description을 **각각 검사**한다. 임의의 문자 간격과 필드 간 연결을 없앴고, 단어 중간의 `다른`을 잡지 않도록 경계를 추가했다.
  - “함께 살펴보세요/둘러보세요/구매”가 위의 다른 상품 구문과 함께 나오면 제거된다. 현재 제품을 살펴보라는 문구 자체는 제거 사유가 아니다.
  - **빈 items recommendation 제거는 유지**했다. 일반 제품 배치 제안은 items가 있을 때 제목·본문·항목을 그대로 보존한다.
- **추가 테스트:** `tests/test_be_flow_fixes.py`에 16개 매개변수 회귀 사례를 추가했다. 두 정상 검수 문구, `새로운 배치`, 다른 공간·방향, `남다른 작품`, 영어 추천/추가 활용의 **보존 8개**와, 원래의 다른 전통 공예품 문구 및 관련/연관/유사/비슷한 상품·영어 다른 상품 탐색의 **제거 8개**다. 제거 사례에도 정상 배치 items를 넣어 빈 목록 조건으로 우연히 통과하지 않게 했다. 실제 sanitizer의 page_plan 및 HTML·React 문서의 섹션 유무를 검증한다. 기존 테스트와 임계값은 변경하지 않았다.
- **검증 결과:**
  - 수정 전 새 회귀 테스트: **8 failed, 8 passed** — 보존 사례가 모두 삭제되는 문제 재현.
  - 수정 후 관련 테스트: `.venv/bin/python -m pytest -q tests/test_be_flow_fixes.py tests/test_html_renderer.py tests/test_draft_flow.py` → **82 passed**.
  - 전체: `.venv/bin/python -m pytest -q` → **502 passed, 2 warnings in 21.19s**. 기존 Starlette/httpx 및 anyio 경고 2건만 남았다.
  - `git --no-optional-locks diff --check` 통과. 금지된 git 변경 명령을 실행하지 않았다. 이번 수정은 위 Python 필터, 회귀 테스트, 이 보고에 한정했다.

### 기존 사진 재사용 렌더 확인

재현 승인 draft의 recommendation 문구와 items에 검수 사례를 대입하여 렌더했다. 재현 자료의 원본 WebP 및 사진 **8장을 그대로 재사용**했고, 기존 `assets/objects/`와 이전 결과의 사진 해시까지 대조했다. 모델 호출·이미지 생성은 없었다. 비교 입력에서 바꾼 것은 recommendation의 제목·본문·items뿐이다.

결과 디렉터리:

```text
<scratchpad>/be-repro/fixes-20261001-review-7b/
```

| 사례 | 결과 | PNG |
| --- | --- | --- |
| 추천 연출 — 이 작품은 거실 선반 위나 현관 벽에 두면 잘 어울립니다. | 유지, 9개 섹션 | `normal-display.png` / `normal-display-sections/07-recommendation.png` |
| 추가로 즐기는 방법 — 이 제품은 여름철 장식으로도 쓸 수 있습니다. | 유지, 9개 섹션 | `additional-use.png` / `additional-use-sections/07-recommendation.png` |
| 전주에서 만든 다른 전통 공예품도 함께 살펴보세요. | 제거, 8개 섹션 | `related-products.png` |

정상 두 섹션의 제목·본문·배치 항목을 PNG에서 육안 확인했다. 각 사례의 React 문서도 같은 디렉터리의 `*-react-document.json`에 저장했다. 입력 문구·필터 결과·재사용 사진 해시는 `metrics.json`, 재현 스크립트는 `render_review_cases.py`에 있다.

**남은 한계:** 명시적 상품 수식 구문을 검사하는 문자열 필터이며 모든 우회 표현을 의미적으로 판별하지 않는다. `전통·수공예` 외 수식어가 끼어 있는 문구 등은 놓칠 수 있다. 반대로 직접적인 관련 상품 언급은 recommendation에서 제거되므로, 실제 관련 상품 데이터를 이용한 추천은 별도 계약이 필요하다. 이번 수정에서는 정상 현재 제품 제안의 과도한 삭제를 줄이는 쪽으로 범위를 좁혔다.
