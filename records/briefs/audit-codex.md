# 검수 작업 — 계약·아키텍처 문서와 실제 코드 대조

당신은 검수자입니다. **파일을 절대 수정하지 마세요.** 발견 사항만 보고서에 적습니다.

## 담당 파일 (이 목록 밖의 파일은 읽기만 하고, 다른 워커 범위이므로 보고하지 마세요)
- docs/api/ai-dto-contract.md
- docs/api/ai-fe-io-spec.md
- docs/api/ai-product-content-generation-agreement.md
- docs/api/be-fe-ai-integration-spec.md
- docs/api/react-json-output-contract.md
- docs/architecture/ai-architecture-and-safety.md
- docs/architecture/ai-architecture-design.md
- docs/architecture/ai-evaluation-and-safety-policy.md
- README.md

대조 기준(읽기 전용): src/detail_page_ai/**, src/local_detail_page_ai/**, tests/**, assets/references/detail-page-layouts.json

## 확인 항목
1. 문서에 적힌 **HTTP 엔드포인트 경로와 메서드**가 src/detail_page_ai/app.py 의 실제 라우트와 일치하는가. 문서에만 있거나 코드에만 있는 경로를 전부 나열.
2. 문서에 적힌 **응답/요청 필드명**(react_document, asset_mode, fidelity_status, product_generated 등)이 실제 코드의 필드명과 철자까지 일치하는가.
3. **인증 헤더 이름**(예: X-AI-Internal-Token)과 인증이 걸리는 경로가 코드와 일치하는가. /health, /health/ready 가 무인증인지도 확인.
4. **vLLM / Diffusers / Ollama** 언급이 남아 있는가. 서버 추론 구성은 SGLang 으로 확정됐다. 단 Mac 로컬 개발 구성은 MLX 가 맞으므로, 어느 문맥인지 구분해서 보고할 것. (문맥 구분 없이 "MLX 언급 발견"으로 보고하면 오탐이다.)
5. **'참고용' 라벨** 관련 서술이 남아 있는가. 이 라벨은 제거됐다.
6. 문서가 말하는 **레이아웃 카탈로그 종수**가 assets/references/detail-page-layouts.json 의 실제 항목 수와 일치하는가. (과거에 "20종"으로 잘못 적힌 전례가 있다.)
7. **존재하지 않는 데이터를 사실로 적은 문장**이 있는가. 이 프로젝트에는 사람 평가 점수·설문 결과·GPU 실측치가 존재하지 않는다. 그런 수치가 단정형으로 적혀 있으면 전부 보고.

## 보고 규칙
- 근거는 반드시 `파일경로:행번호` 로 적을 것. 행 번호 없는 지적은 채택하지 않는다.
- 추측은 `[추정]` 으로 표시. 코드에서 확인한 것은 `[확인]`.
- 문제가 없던 항목도 "이상 없음"으로 적을 것. 무엇을 봤는지 증명되어야 한다.
- 심각도를 3단계로: `치명`(외부에 잘못된 계약을 전달) / `불일치`(문서-코드 차이) / `사소`(표기).

## 산출물
`.orchestration/reports/audit-2026-09-16/codex.md` 한 파일.
끝나면 마지막 줄에 `완료: .orchestration/reports/audit-2026-09-16/codex.md, 발견 N건` 을 출력하세요.
