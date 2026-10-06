# 수정 작업 — 계약·아키텍처 문서 (치명 2건 + 불일치 1건 + 사소 1건)

검수에서 확정된 결함만 고칩니다. **코드는 고치지 마세요. 코드가 맞고 문서가 틀렸습니다.**

## 담당 파일 (이 5개만 수정. 다른 파일은 다른 워커가 동시에 고치는 중이니 절대 건드리지 마세요)
- docs/api/be-fe-ai-integration-spec.md
- docs/api/ai-dto-contract.md
- docs/api/react-json-output-contract.md
- docs/architecture/ai-architecture-design.md
- docs/api/ai-fe-io-spec.md

## 고칠 것

### [치명 C-1] 허용 `asset_mode` 목록에 `source_original` 누락
- `docs/api/be-fe-ai-integration-spec.md:486-494` 의 허용 목록에 `source_original` 이 빠져 있다.
- `docs/api/ai-dto-contract.md:113-115` 도 상품 픽셀의 권위 있는 근거를 `source`, `source_crop`, `source_composite` 로만 적는다.
- 정본은 `src/detail_page_ai/models.py:22-30` 의 `AssetMode` 이며 여기에는 `source_original` 이 있다.
- hero 는 실제로 `asset_mode="source_original"`, `product_generated=False`, `fidelity_status="VERIFIED"` 를 내보낸다(`src/detail_page_ai/source_photos.py:1065-1083`). 즉 **원본 사진을 그대로 쓰는 대표 이미지**를 가리키는 값이다.
- 두 문서 모두에 `source_original` 을 추가하고, 그것이 무엇인지(hero 대표 이미지에 촬영 원본을 손대지 않고 쓰는 경우) 한 줄로 설명할 것.

### [치명 C-2] `react_document` 전달 경로의 존재하지 않는 `status.` 래퍼
- `docs/api/react-json-output-contract.md:19-21` 이 `status.draft.react_document`, `status.result.detail_page.react_document` 로 적었다.
- `docs/architecture/ai-architecture-design.md:284-285` 에도 같은 표기가 있다.
- 정본은 `src/detail_page_ai/ai_dto.py:84-95` 의 `AiToProductBeStatusResponseDto` 다. 여기서 `status` 는 **문자열 필드**이고 `draft` 와 `result` 가 최상위에 나란히 있다.
- 실제 경로는 `draft.react_document` 와 `result.detail_page.react_document` 다. 두 문서를 이 경로로 고칠 것.
- 초안 저장 응답은 `AiFeDraftResponseDto` 를 반환하며(`src/detail_page_ai/app.py:402-418`) `react_document` 는 초안 결과의 최상위 필드다(`src/detail_page_ai/dto.py:358-373`). 저장 응답 행도 실제 구조에 맞게 고칠 것.

### [불일치 I-1] 허용 태그에 `h1`
- `docs/api/be-fe-ai-integration-spec.md:104` 가 제한 태그 예시에 `h1` 을 넣었다.
- 정본 allowlist 는 `src/detail_page_ai/react_document.py:231-257` 이며 `section`, `article`, `div`, `h2`, `h3`, `h4` … 로 **`h1` 이 없다.**
- `docs/api/react-json-output-contract.md:88-94` 의 목록에도 `h1` 이 없다. `be-fe-ai-integration-spec.md:104` 에서 `h1` 을 빼고 실제 allowlist 와 맞출 것.

### [사소 T-5] health 경로가 API 목록에 없음
- `docs/api/ai-fe-io-spec.md:104-114` 와 `:164-169` 의 경로 목록에 다음 둘을 추가할 것.
  - `GET /health` — liveness. 인증 불필요, 항상 200 `{"status":"ok"}`, 추론 서버를 호출하지 않음 (`src/detail_page_ai/app.py:158`)
  - `GET /health/ready` — readiness. 인증 불필요, SGLang 두 서버의 `/v1/models` 확인 후 200 또는 503 + 사유 (`src/detail_page_ai/app.py:163`)

## 지켜야 할 것
- **코드 변경 금지.** 이 4건은 전부 문서가 틀린 것이다.
- 검증되지 않은 것을 검증된 것처럼 쓰지 말 것. 서버 GPU 실행은 아직 한 번도 없었다.
- 위 5개 파일 외에는 열지도 고치지도 말 것. 특히 `docs/deliverables/experiments/`, `docs/evaluation/`, `docs/refactoring/`, `docs/operations/` 는 **시점 기록이거나 다른 워커 담당**이다.
- 끝나면 `.venv/bin/python -m pytest -q` 를 돌려 **358 passed** 를 확인할 것.

## 보고
`## 결과` 에 파일별로 `행 번호 · 고치기 전 값 → 고친 후 값` 을 적고, 마지막 줄에 `완료: 수정 N개 파일, 테스트 358 passed` 를 출력하세요.
