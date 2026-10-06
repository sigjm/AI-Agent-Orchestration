# 계약·아키텍처 문서 검수 보고서

검수 대상은 지시서에 열거된 9개 문서이며, 대조 기준은 src/detail_page_ai/**, src/local_detail_page_ai/**, tests/**, assets/references/detail-page-layouts.json이다. 지시대로 담당 문서와 코드에는 수정하지 않고 검수 결과만 기록했다.

## 총괄

- 치명: 0건
- 불일치: 3건
- 사소: 1건
- 총 발견: 4건

## 1. HTTP 엔드포인트 경로·메서드 대조

### [확인] 실제 AI 애플리케이션 라우트와 문서에 기재된 AI 라우트

src/detail_page_ai/app.py:214, src/detail_page_ai/app.py:270, src/detail_page_ai/app.py:502, src/detail_page_ai/app.py:516의 로컬 직접 API 4개는 docs/api/ai-fe-io-spec.md:164-168 및 docs/api/be-fe-ai-integration-spec.md:540-545와 메서드·경로가 일치한다.

src/detail_page_ai/app.py:325, src/detail_page_ai/app.py:383, src/detail_page_ai/app.py:402, src/detail_page_ai/app.py:427의 내부 API 4개는 docs/api/ai-fe-io-spec.md:108-112, docs/api/ai-dto-contract.md:189, docs/api/ai-dto-contract.md:247, docs/api/ai-dto-contract.md:283, docs/api/ai-dto-contract.md:349와 일치한다.

### [발견 1] [사소] 애플리케이션 health 라우트가 API 경로 목록에서 누락됨

[확인] 코드에는 GET /health(src/detail_page_ai/app.py:158)와 GET /health/ready(src/detail_page_ai/app.py:163)가 존재한다. 담당 문서의 AI 내부·직접 API 목록은 docs/api/ai-fe-io-spec.md:104-114 및 docs/api/ai-fe-io-spec.md:164-169, docs/api/be-fe-ai-integration-spec.md:540-545에 있으나 이 두 애플리케이션 health 경로는 열거하지 않는다. 따라서 코드에만 있는 애플리케이션 비즈니스 라우트는 다음 2개다.

- GET /health — src/detail_page_ai/app.py:158
- GET /health/ready — src/detail_page_ai/app.py:163

외부 계약 자체를 오해하게 하는 치명적 문제는 아니지만, 운영자가 애플리케이션 liveness/readiness 경로를 문서에서 찾을 수 없는 표기 누락이다.

### [확인] 문서에만 보이는 경로의 문맥 구분

다음 4개는 문서에만 보이지만, 공개 상품 BE API가 이 저장소에 구현되지 않았고 합의용 제안이라고 명시되어 있다(docs/api/be-fe-ai-integration-spec.md:5-6). 따라서 AI 서버 라우트 불일치로 세지 않았다.

- POST /api/v1/products/{product_id}/detail-page-jobs — docs/api/be-fe-ai-integration-spec.md:18
- GET /api/v1/products/{product_id}/detail-page-jobs/{job_id} — docs/api/be-fe-ai-integration-spec.md:19
- PUT /api/v1/products/{product_id}/detail-page-jobs/{job_id}/draft — docs/api/be-fe-ai-integration-spec.md:20
- POST /api/v1/products/{product_id}/detail-page-jobs/{job_id}/approve — docs/api/be-fe-ai-integration-spec.md:21

다음은 애플리케이션 라우트가 아닌 하위 모델 서버 경로다. 코드도 readiness에서 모델 서버의 GET /v1/models를 호출한다(src/detail_page_ai/app.py:167-175, src/detail_page_ai/app.py:189-190). 문서의 POST /v1/images/generations 역시 모델 어댑터 경계의 경로이며, AI 애플리케이션 외부 경로로 구분했다(docs/architecture/ai-architecture-and-safety.md:172, src/local_detail_page_ai/clients.py:235-247). 과거 /ai/products 계약은 폐기 문서에만 남아 있고 현재 활성 계약이 아니라고 명시되어 있다(docs/api/ai-product-content-generation-agreement.md:5-6).

## 2. 요청·응답 필드명 대조

### [확인] 필드명 철자

product_generated, asset_mode, fidelity_status는 문서 예시(docs/api/be-fe-ai-integration-spec.md:475-482)와 실제 DTO(src/detail_page_ai/dto.py:305-322)의 철자가 일치한다. react_document도 문서의 전달 위치 설명(docs/api/be-fe-ai-integration-spec.md:97-99)과 실제 FE 자산 DTO(src/detail_page_ai/dto.py:325-333), 초안 결과 DTO(src/detail_page_ai/dto.py:358-373)에 동일한 필드명으로 존재한다. 내부 요청 DTO의 product_id, source_asset_id, request_id, idempotency_key, template_id, locale, user_hints, options도 코드(src/detail_page_ai/ai_dto.py:34-47)와 계약 문서의 요청 정의(docs/api/ai-dto-contract.md:194-222)가 일치한다.

아래 3번·4번의 문제는 필드명 철자 자체가 아니라 JSON 경로와 허용 enum 집합의 불일치다.

### [발견 2] [불일치] react_document JSON 경로에 존재하지 않는 status 래퍼가 기재됨

docs/api/react-json-output-contract.md:17-23은 초안 상태·초안 저장·최종 결과를 각각 status.draft.react_document, status.draft.react_document, status.result.detail_page.react_document로 적고, docs/architecture/ai-architecture-design.md:284-285도 같은 status 래퍼를 사용한다.

[확인] 실제 상태 DTO는 최상위 status 문자열과 최상위 draft/result를 갖는다(src/detail_page_ai/ai_dto.py:84-95, src/detail_page_ai/dto.py:393-401). 따라서 상태 조회의 실제 경로는 draft.react_document 및 result.detail_page.react_document다. 더구나 초안 저장 라우트는 AiFeDraftResponseDto를 반환하고(src/detail_page_ai/app.py:402-418), service가 rebuilt.fe_draft를 그대로 반환한다(src/detail_page_ai/service.py:303-335). 이 응답의 react_document는 초안 결과의 최상위 필드다(src/detail_page_ai/pipeline.py:543-560, src/detail_page_ai/dto.py:358-373). 문서 경로대로 FE를 구현하면 상태 문자열을 객체처럼 탐색하거나 저장 응답에서 존재하지 않는 status.draft를 탐색하게 된다.

### [발견 3] [불일치] BE/FE AST 허용 태그에 h1이 포함되어 있으나 코드 allowlist에는 없음

docs/api/be-fe-ai-integration-spec.md:104는 root[]의 제한 태그 예시에 h1을 포함한다. 그러나 실제 AllowedTag에는 section, article, div 다음 h2, h3, h4부터 시작하며 h1이 없다(src/detail_page_ai/react_document.py:231-257). docs/api/react-json-output-contract.md:88-94의 allowlist에는 h1이 없어 문서 간에도 기준이 갈린다. FE 또는 BE가 be-fe 명세만 따를 경우 코드 검증기에서 허용하지 않는 h1을 계약상 허용 태그로 오인할 수 있다.

### [발견 4] [불일치] source_original이 자산 모드 권위 목록에서 누락됨

docs/api/be-fe-ai-integration-spec.md:486-494의 허용 asset_mode 목록은 source, source_crop, source_composite, generated_scene, generated_view만 열거하고 source_original을 빠뜨린다. docs/api/ai-dto-contract.md:113-115도 상품 픽셀의 권위 있는 근거를 source, source_crop, source_composite으로만 적는다.

[확인] 실제 AssetMode에는 source_original이 포함된다(src/detail_page_ai/models.py:22-30). source fidelity validator도 source_original을 허용하고 hero에 VERIFIED를 요구한다(src/detail_page_ai/source_photos.py:542-555). hero 생성 결과는 실제로 asset_mode=source_original, product_generated=False, fidelity_status=VERIFIED로 반환된다(src/detail_page_ai/source_photos.py:1065-1083). 반면 다른 아키텍처 문서는 이를 올바르게 적고 있다(docs/architecture/ai-architecture-and-safety.md:148, docs/architecture/ai-architecture-and-safety.md:224, docs/architecture/ai-architecture-design.md:17). 따라서 BE/FE 명세와 DTO 계약 문서의 허용 집합·권위 범위를 코드 및 아키텍처 문서와 맞춰야 한다.

## 3. 인증 헤더와 인증 적용 경로

### [확인] 이상 없음

내부 4개 라우트는 모두 X-AI-Internal-Token 헤더를 받고(src/detail_page_ai/app.py:334-340, src/detail_page_ai/app.py:389-393, src/detail_page_ai/app.py:409-412, src/detail_page_ai/app.py:435-440), 구현은 설정 토큰과 비교해 없거나 다르면 401/설정 미구성 시 503을 반환한다(src/detail_page_ai/app.py:90-98). 문서의 헤더 표기와 일치한다(docs/api/ai-fe-io-spec.md:108-114).

GET /health 및 GET /health/ready에는 인증 dependency가 없다(src/detail_page_ai/app.py:158-164). 테스트도 토큰 설정 상태에서 /health가 200임을 확인하고(tests/test_app.py:446-457), readiness가 SGLang text/image의 /v1/models를 검사하는 것을 확인한다(tests/test_app.py:460-492). 로컬 직접 API는 ENABLE_LEGACY_DEMO_API=true일 때만 열리는 별도 경로다(src/detail_page_ai/app.py:101-105, src/detail_page_ai/app.py:229-230, src/detail_page_ai/app.py:280). 인증 헤더명과 인증 적용 범위에 추가 불일치는 없다.

## 4. 추론 서버·로컬 provider 문맥

### [확인] 이상 없음

담당 문서에서 vLLM과 Diffusers의 잔존 언급은 키워드 검색상 0건이다. 서버 운영은 SGLang으로 명시되어 있다(docs/architecture/ai-architecture-and-safety.md:23, docs/architecture/ai-architecture-and-safety.md:164-166). MLX는 Mac 로컬 개발 문맥이고, Ollama도 별도 로컬 검증 옵션으로 구분되어 있다(docs/architecture/ai-architecture-design.md:123, docs/architecture/ai-architecture-design.md:187, docs/architecture/ai-architecture-and-safety.md:160). 실제 provider factory도 mlx, ollama, sglang을 구분해 선택한다(src/detail_page_ai/config.py:22-23, src/local_detail_page_ai/factory.py:39-54). 따라서 MLX/Ollama 언급을 서버 구성의 낡은 표기로 오탐하지 않았다.

## 5. 참고용 라벨

### [확인] 이상 없음

문서에 남은 참고용 표현은 제거 정책을 설명하는 부정문이다. README.md:9, README.md:73과 docs/architecture/ai-architecture-and-safety.md:144, docs/architecture/ai-architecture-design.md:18은 화면에 별도 참고용 표시를 붙이지 않는다고 한다. react JSON 계약도 reference-label 노드 제거를 명시한다(docs/api/react-json-output-contract.md:97). 실제 생성 자산 라벨은 AI 생성 활용 장면과 AI 생성 디테일이고 product_generated=true를 함께 설정한다(src/detail_page_ai/source_photos.py:927-940, src/detail_page_ai/source_photos.py:968-981). 제거된 라벨을 요구하는 활성 서술은 발견되지 않았다.

## 6. 레이아웃 카탈로그 종수

### [확인] 이상 없음

assets/references/detail-page-layouts.json:1은 배열이며 id 항목을 파일에서 직접 세면 25개다. 항목 시작 행은 assets/references/detail-page-layouts.json:3, 32, 63, 92, 121, 150, 179, 208, 239, 268, 297, 326, 355, 384, 413, 444, 475, 504, 533, 562, 593, 624, 657, 692, 725이고 마지막 항목명은 assets/references/detail-page-layouts.json:726이다. 담당 문서에서 카탈로그를 20종 또는 25종으로 단정하는 문장은 검색되지 않았다. 따라서 과거의 20종 오류는 현재 담당 문서에 없다. docs/architecture/ai-architecture-design.md:389의 “최대 20단계”는 AST 깊이 제한으로 카탈로그 종수와 다른 수치다.

## 7. 존재하지 않는 데이터의 단정 여부

### [확인] 이상 없음

사람 평가 점수·설문 결과·GPU 실측치를 실제 결과로 단정한 문장은 발견되지 않았다. 평가 정책은 현재 공개 입력 60건이 사람 정답 라벨·모델 실행 대기 상태라고 명시한다(docs/architecture/ai-evaluation-and-safety-policy.md:3-6, docs/architecture/ai-evaluation-and-safety-policy.md:55-60). 1~5점, 정확도 90%, 평균 4.0, 승인 80% 등은 평가 방법 또는 초기 release gate 목표로 제시된다(docs/architecture/ai-evaluation-and-safety-policy.md:155-167, docs/architecture/ai-evaluation-and-safety-policy.md:171-193). 서버 GPU의 동시 적재·처리 시간·peak VRAM도 아직 검증하지 않았다고 명시한다(docs/architecture/ai-architecture-and-safety.md:9, docs/architecture/ai-architecture-and-safety.md:557-560, README.md:205). 따라서 이 수치들을 실측 결과로 보고하지 않았다.

완료: .orchestration/reports/audit-2026-09-16/codex.md, 발견 4건
