# 작업 — BE 팀 2차 요청 문서 작성

## 만들 파일 (이 하나만)
`docs/api/be-handoff-2026-09-18.md`

다른 파일은 열지 마세요. `src/`·`tests/` 는 다른 워커가 동시에 고치는 중이고, `docs/evaluation/` 은 시점 기록이라 수정 금지입니다.

## 배경
2026-09-17 에 드린 요청(`docs/api/be-handoff-2026-09-17.md`, BE-1~BE-8)에 BE 가 대응했고, 2026-09-18 에 다시 붙여 봤습니다. 실측 기록은 `docs/evaluation/reintegration-test-2026-09-18.md` 에 있습니다. **그 문서를 읽고 사실을 그대로 옮기세요. 새로 지어내지 마세요.**

## 문서 성격
**먼저 해결된 것을 인정하고, 그다음 남은 것을 요청하는** 문서입니다. 앞 문서와 달리 대부분이 해결됐으므로 어조가 달라야 합니다.

## 구성

### 1. 먼저 — 해결된 것 (표)
BE 가 반영한 것을 앞 문서 번호와 함께 적으세요. 실측 기록의 「BE 가 반영한 것」 표를 근거로:
- BE-1 HTTP/1.1 고정
- BE-2 `@Async` 자기 호출 → `GenerationAsyncExecutor` 분리, 202 가 `PROCESSING` 으로
- BE-4 재시도 (`attempt=2,3` 로그)
- BE-7 설정 이름 → `AI_CHAT_BOT_URL`·`AI_CONTENT_URL`
- 요청 경로·형식을 **우리 계약에 맞춰 와 준 것** (`/internal/v1/ai/detail-page-jobs`, multipart, `X-AI-Internal-Token`, `Idempotency-Key`)
- 콜백 ACK 를 **우리 스키마 그대로** 만들어 준 것

**"덕분에 전 구간이 처음으로 이어졌다"** 는 사실을 명시하세요 — 접수 202 → DRAFT_READY → 콜백 → BE `COMPLETED`.

### 2. 남은 요청 (번호는 `BE-9` 부터 이어서)

| 새 번호 | 내용 |
| --- | --- |
| **BE-9** | **가이드의 콜백 경로가 존재하지 않습니다.** 가이드 3-3 은 `/internal/generations/complete/multipart` 와 `/complete/json` 을 안내하는데 실제 구현은 `AiCallbackController` 의 `POST /internal/generations/{generationId}/completion` 입니다. 가이드 경로로 보내면 `NoResourceFoundException` 과 함께 **500**, 실제 경로로 보내면 **200 `SAVED`** 였습니다. **어느 쪽이 정본인지** 알려 주세요. 이 답에 따라 우리 구현이 달라집니다 — 고정 경로면 설정만으로 되고, `{generationId}` 경로면 우리 클라이언트가 경로를 조립하도록 고쳐야 합니다 |
| **BE-10** | **없는 경로에 404 가 아니라 500 이 돌아옵니다.** `GlobalExceptionHandler` 가 `NoResourceFoundException` 을 잡아 500 으로 바꿉니다. 경로 오타를 찾기 어렵습니다 |
| **BE-11** | **콜백 시점을 정해 주세요.** 우리 파이프라인은 `DRAFT_READY` 에서 멈추고, 설계상 그다음은 장인 **승인** 단계이며 BE 전달은 승인 뒤에 일어납니다. 그런데 BE 는 작업 제출 후 콜백을 기다립니다 — 이번 테스트에서 BE 가 10분간 `QUEUED` 로 남았습니다. **초안이 나온 시점에 콜백할지, 승인 뒤에 할지**, 그리고 **승인을 누가 어느 API 로 하는지** 정해 주세요 |
| **BE-12** | **이미지 URL 수집 확인.** BE 가 `images[0]` 을 직접 내려받아 우리에게 multipart 로 보냅니다. 리다이렉트하는 URL(`picsum.photos`)을 주니 **400 `Invalid product image`** 가 났고, 리다이렉트 없는 직접 URL 로는 정상이었습니다. 실제 S3 presigned URL 에서 리다이렉트 처리가 되는지 확인 부탁드립니다 |

각 항목은 **증상 → 근거(로그/파일) → 요청** 순으로. 근거는 실측 기록에 있는 것만 쓰세요.

### 3. 우리가 고치는 것
`metadata` 키 표기를 BE 가 읽는 **camelCase** 로 맞추는 작업을 진행 중이라고 적으세요. 같은 경로에 snake_case 로 보내면 500, camelCase 로 보내면 200 `SAVED` 였다는 실측을 근거로 답니다. **BE 에 요청하는 것이 아니라 우리가 맞추는 것**임을 분명히 하세요.

### 4. 챗봇 (참고)
`chat_bot/Dockerfile` 이 올라와 이미지 빌드에 성공했습니다(10.4GB). 다만 **`USER` 지시가 없어 root 로 실행**되며, 인프라 운영 기준의 "가능하면 Non-root" 항목에 걸립니다. 챗봇 팀 확인 사항으로 한 줄만 적으세요. 우리 소관이 아닙니다.

## 지켜야 할 것
- 측정하지 않은 것을 단정하지 마세요. **서버 GPU 에서는 아직 한 번도 실행되지 않았습니다.**
- 콜백은 이번 테스트에서 **수동으로 보냈습니다.** 자동으로 동작한 것처럼 쓰지 마세요.
- 없는 데이터를 만들지 마세요.

## 검증
- 인용한 경로·수치가 `docs/evaluation/reintegration-test-2026-09-18.md` 와 일치하는지 대조
- 상대 링크가 실제로 존재하는지 확인

## 보고
`## 결과` 에 항목 수와 인용 근거를 적고, 마지막 줄에 `완료: docs/api/be-handoff-2026-09-18.md, N줄` 출력.
