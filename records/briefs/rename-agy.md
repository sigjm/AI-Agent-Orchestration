# 이름 변경 반영 — 계약·아키텍처 문서

팀 호칭이 BE 로 정리되면서 코드의 DTO 클래스와 환경변수 이름이 바뀐다. 문서 표기를 맞춘다.

## 담당 파일 (이 5개만)
- docs/api/ai-dto-contract.md
- docs/api/be-fe-ai-integration-spec.md
- docs/api/ai-fe-io-spec.md
- docs/architecture/ai-architecture-design.md
- docs/architecture/ai-architecture-and-safety.md

## 바꿀 것 1 — 환경변수 표기
`BACKEND_PRODUCT_URL` → **`BACKEND_URL`** (설정 속성으로 적힌 `backend_product_url` 도 `backend_url`)

## 바꿀 것 2 — DTO 클래스 이름 8개
| 현재 | 변경 후 |
| --- | --- |
| `ProductBeToAiCreateJobRequestDto` | `BeToAiCreateJobRequestDto` |
| `ProductBeToAiApproveDraftRequestDto` | `BeToAiApproveDraftRequestDto` |
| `ProductBeToAiSaveDraftRequestDto` | `BeToAiSaveDraftRequestDto` |
| `ProductBeToAiPersistAckDto` | `BeToAiPersistAckDto` |
| `AiToProductBeAcceptedResponseDto` | `AiToBeAcceptedResponseDto` |
| `AiToProductBeStatusResponseDto` | `AiToBeStatusResponseDto` |
| `AiToProductBeApprovedResponseDto` | `AiToBeApprovedResponseDto` |
| `AiToProductBePersistRequestDto` | `AiToBePersistRequestDto` |

부분 문자열이 아니라 위 8개 이름 전체를 정확히 매칭해 바꿀 것. `AiBePersistAck`, `AiBeProductPersistRequest` 처럼 `ProductBe` 형태가 아닌 이름은 건드리지 말 것.

## 절대 바꾸지 말 것 — 바꾸면 BE 와의 계약이 깨진다
- **JSON 필드 이름**: `product_id`, `product_generated`, `source_asset_id`, `generation_id`, `idempotency_key`, `asset_mode`, `fidelity_status` 등. wire 계약이고 `product_id` 는 상품의 ID 라는 뜻이라 이름도 정확하다.
- **HTTP 경로**(`/internal/v1/ai/...`), **헤더**(`X-AI-Internal-Token`, `Idempotency-Key`, `Authorization`).
- 다른 환경변수(`BACKEND_AUTH_TOKEN`, `BACKEND_TIMEOUT_SECONDS`, `AI_INTERNAL_AUTH_TOKEN`, `AI_CORS_ORIGINS` …).
- 예시 JSON 본문 안의 키·값.

## 주의
코드는 다른 워커가 동시에 고치고 있다. `src/`, `tests/`, `.env.example` 은 **열지도 말 것.** 문서에 적힌 표기만 맞춘다.

## 검증
1. 담당 파일에 `ProductBeToAi`·`AiToProductBe`·`BACKEND_PRODUCT_URL`·`backend_product_url` 이 **0건**
2. `git diff` 에서 `product_id`·`source_asset_id`·`product_generated`·`X-AI-Internal-Token` 의 삭제행 수와 추가행 수가 같은지 확인 (딸려 바뀐 것이 없는지)
3. `.venv/bin/python -m pytest -q` → **358 passed**

## 보고
`## 결과` 에 파일별 치환 건수와 위 검증 3건 결과를 적고, 마지막 줄에 `완료: 수정 N개 파일, 테스트 358 passed` 출력.
