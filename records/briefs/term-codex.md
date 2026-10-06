# 표현 정리 — 계약 문서군

## 담당 파일 (이 5개만. 다른 파일은 다른 워커가 동시에 고치는 중이니 열지 말 것)
- docs/api/ai-dto-contract.md (38곳)
- docs/api/be-fe-ai-integration-spec.md (39곳)
- docs/api/ai-fe-io-spec.md (16곳)
- docs/api/react-json-output-contract.md (6곳)
- docs/api/ai-product-content-generation-agreement.md (2곳)

## 바꾸는 것
문서 본문의 **호칭 표현** `상품 BE` → `BE` 로 통일한다. 연동 상대 팀의 이름은 "상품 BE" 가 아니라 그냥 **BE** 다.

## 절대 바꾸지 말 것 (이걸 바꾸면 배포와 계약이 깨진다)
- **환경변수 이름**: `BACKEND_PRODUCT_URL`, `BACKEND_AUTH_TOKEN`, `BACKEND_TIMEOUT_SECONDS` 등. `BACKEND_PRODUCT_URL` 은 이미 인프라팀에 전달된 배포 규격이다.
- **DTO·클래스 이름**: `ProductBeToAiCreateJobRequestDto`, `AiToProductBePersistRequestDto`, `ProductBeToAiPersistAckDto` 등 `ProductBe`·`ProductBE` 가 들어간 모든 식별자.
- **필드 이름**: `product_id`, `product_generated`, `source_asset_id` 등.
- **코드 블록·표의 식별자 칸 안의 값.** 설명 문장만 고친다.
- `상품` 이 팀 이름이 아니라 **물건**을 뜻하는 곳: 예) "상품 사진", "상품 픽셀", "상품 정보", "상품 사실". 이런 건 그대로 둔다.

## 문장이 어색해지지 않게
기계적으로 지우지 말고 읽어서 고친다.
- `상품 BE가` → `BE가`, `상품 BE는` → `BE는`, `상품 BE의` → `BE의`
- `상품 BE↔AI` → `BE↔AI`
- `상품 BE 저장 schema` → `BE 저장 schema`
- 바꾼 뒤 그 문장을 다시 읽어 주어가 사라지거나 뜻이 흐려진 곳이 없는지 확인할 것.

## 검증
1. 담당 파일에 `상품 BE` 가 **0건**인지 확인 (단, 위 예외에 해당해 일부러 남긴 게 있으면 그 이유를 보고할 것)
2. `ProductBe`·`BACKEND_PRODUCT_URL` 등 식별자가 **하나도 사라지지 않았는지** `git diff` 로 확인. 식별자가 diff 에 지워진 채로 나타나면 잘못 고친 것이다.
3. `.venv/bin/python -m pytest -q` → **358 passed**

## 보고
`## 결과` 에 파일별 치환 건수, 일부러 남긴 것과 그 이유, 위 검증 3건 결과를 적고, 마지막 줄에 `완료: 수정 N개 파일, 테스트 358 passed` 출력.
