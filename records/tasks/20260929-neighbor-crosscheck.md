# 교차검증 — 네 리뷰 4건에 대한 내 판정을 검증해 달라

## 중요 — git 상태 변경 금지

이 저장소에서 `git reset/checkout/commit/stash/restore` 등 **상태를 바꾸는 git 명령은 실행하지 마라.**
지난번 `git reset HEAD^` 로 커밋이 풀린 일이 있었다. 읽기(`git log/diff/show`)만 허용한다. 파일 수정도 금지다.

## 먼저 알아둘 것

네가 본 `~/PycharmProjects/GenAI` 클론은 **9/19(#27)에서 멈춘 옛 코드**다. 현재 코드는 이 저장소
`src/` 다(GenAI main 과 동일). `service.py` 는 그 사이 바뀌었다. **이 저장소 `src/` 기준으로** 검증해라.

## 내 판정

| # | 판정 | 내 근거 |
| --- | --- | --- |
| 1 | 사실, 가장 시급 | `app.py:431` `async def approve_internal_detail_page` 가 `service.approve_draft()`(동기, 내부에서 `pipeline.run` 으로 렌더 전체)를 await 없이 호출. 분석은 `executor.submit` 으로 넘기는데 승인만 인라인. 렌더 수 분 동안 이벤트 루프가 막혀 `/health` 도 응답 불가 → K8s liveness 가 `/health` 면 렌더 중 재시작 가능 |
| 2 | **구조상 사실, 현재 배포에선 발생 안 함** | uvicorn 워커 1개(`app.py:540`), 파드 1개. 작업 생성(`service.submit`)·초안 저장(`service.save_draft`)을 `async` 엔드포인트 안에서 **동기로** 호출하므로 같은 이벤트 루프에서 두 요청이 이 코드 안에서 섞이지 않는다. 단 **1번을 스레드 풀로 고치면 실제 병렬이 되어 2번이 진짜 문제**가 된다. 특히 BE 가 렌더 도중 타임아웃으로 같은 승인을 재요청하면 중복 렌더 |
| 3 | 사실 | `persistence.py:405` `SELECT payload_json FROM detail_page_jobs` 전체 스캔 + 행마다 역직렬화(원본 이미지 포함). 스키마(`persistence.py:314`)에 멱등성 키 컬럼 자체가 없음 |
| 4 | 사실, **지적보다 넓음** | ① `pipeline.retry_backend_delivery` 가 모든 `BackendDeliveryError` 를 `mark_failed`→`FAILED`, `service._retry_delivery`(`service.py:477`)도 `retryable` 무시하고 재시도 예약. ② `list_retryable`(`persistence.py:892`)이 `status IN ('PENDING','FAILED')` 만 보고 **attempts 를 안 봄**. ③ 재시작 때뿐 아니라 `_replay_due_outbox_deliveries` 가 **임대 만료 재처리 때마다** 한도 넘은 건도 다시 보냄 |

## 내가 제안하는 수정 설계

1. **1번**: 승인·초안 저장을 `run_in_threadpool` 로 넘긴다. **작업 큐 + 콜백 방식은 BE 승인 계약(BE-11, 미결정)을 바꾸므로 지금은 하지 않는다**
2. **2번**: (a) 멱등성 — `product_id`·`idempotency_key` 컬럼 + UNIQUE 인덱스, 중복 INSERT 는 IntegrityError 로 잡아 기존 작업 반환. (b) 초안 저장·승인 — **작업별 잠금**으로 같은 작업의 저장·승인을 직렬화(단일 프로세스 한정임을 주석으로 명시)
3. **3번**: 2(a) 의 인덱스 컬럼으로 `find_by_idempotency` 를 WHERE 조회로
4. **4번**: `retryable=False` 는 재시도 대상에서 제외되는 별도 상태로, `list_retryable` 은 한도 초과 건 제외
5. 정적 검사: 미사용 import 5개는 고친다. **포맷 23개 파일은 하지 않는다** — 프로젝트에 formatter 설정이 없어 기준이 아니고, diff 가 거대해진다

## 해 달라는 것

1. 위 판정 중 **틀렸거나 근거가 약한 것**을 찾아라. 특히 2번 "현재 발생 안 함" — 반례(예: 백그라운드 스레드가 같은 레코드를 쓰는 경로, 재시작 복구 경로)가 있으면 제시해라
2. 수정 설계에서 **빠진 경로**를 찾아라. 예: 최초 전달 실패 경로(재시도 아닌)도 4번 영향을 받는지, 인메모리 저장소도 같이 고쳐야 하는지, 기존 DB 파일 마이그레이션(기존 행 백필, 중복 키가 이미 있으면 UNIQUE 인덱스 생성 실패)
3. 네 리뷰에 **내가 놓친 문제**가 있으면 추가해라

## 보고

이 파일 하단에 `## 결과`. 항목마다 `동의 / 반박 / 보완` + 근거(파일:줄). 파일 수정·git 상태 변경 금지.
