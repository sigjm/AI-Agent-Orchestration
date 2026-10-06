# 승인 렌더 블로킹 · 동시성 · 멱등성 조회 · 전달 재시도 수정

## 권한과 금지 — 먼저 읽어라

- **수정 허용**: `src/`, `tests/` 아래 파일. 그리고 **이 지시 파일 하단에 `## 결과` 를 쓰는 것**
- **금지**: `git reset/checkout/commit/stash/restore/switch` 등 git 상태 변경. 커밋·머지는 내가 한다
- 기존 테스트를 약화시키지 마라. 깨지면 이유를 보고해라
- 기준 코드는 이 저장소 `src/` (GenAI main 과 동일)

## 배경 — 네 리뷰 4건을 서로 교차검증했다

네 교차검증 지적을 전부 받아들였다. 특히 **2번 "현재 발생 안 함"은 내 판단이 틀렸다** — 재시작 경로와 백그라운드
전달 스레드가 반례다. 그래서 **프로세스 안 잠금 대신 저장소 층의 원자적 갱신**으로 간다.

내가 따로 찾은 것 하나: `approve_draft` 는 `approval_idempotency_key` 를 **렌더가 끝난 뒤에** 저장한다
(`service.py` 298행 근처). 그래서 `"Approval is already in progress"` 검사는 절대 걸리지 않는 죽은 코드다.

## 설계의 중심 — 원자적 read-modify-write 하나

저장소에 `update(job_id, fn)` 같은 **원자적 갱신 하나**를 두고, 작업 레코드를 쓰는 모든 경로가 이걸 거치게 해라.

- SQLite: `BEGIN IMMEDIATE` 로 쓰기 잠금을 잡고 → 읽기 → `fn` 으로 검사·변경 → 쓰기 → 커밋. 스레드·프로세스 모두 안전
- 인메모리: 잠금 안에서 같은 의미
- `fn` 이 예외를 던지면 아무것도 쓰지 않는다

이걸로 아래를 한다. **렌더처럼 오래 걸리는 일은 절대 이 트랜잭션 안에서 하지 마라.**

## 고칠 것

### A. 승인 렌더가 이벤트 루프를 막는다 (리뷰 1번)

- 승인 엔드포인트 **두 곳 모두** 렌더를 `run_in_threadpool` 로: 내부 `approve_internal_detail_page`(`app.py:431`) 와
  legacy 경로(`app.py:298` 의 `service.pipeline.run`). 초안 저장도 스레드 풀로
- **작업 큐 + 콜백으로 바꾸지 마라.** 승인 응답 계약은 BE 와 미결정(BE-11). 응답 형태 그대로

### B. 승인 선점 — 렌더 **전에** 원자적으로 잡는다 (리뷰 2번 + 죽은 코드)

`approve_draft` 를 세 단계로:

1. **선점** (원자적 갱신 안): 승인 상태가 비었거나 이전 실패면 → 키·지문·"진행 중" 기록. 같은 키로 진행 중이면 "진행 중",
   이미 완료면 저장된 결과 반환, 다른 키·지문이면 `IdempotencyConflictError`
2. **렌더** (갱신 밖)
3. **완료 기록** (원자적 갱신 안): 결과 저장. **렌더가 실패하면** 선점을 풀어(실패 상태) 재요청이 다시 선점할 수 있게

`save_draft` 는 원자적 갱신 안에서 **버전 비교 + 승인 진행 중·완료면 거절**.

**재시작 복구**: 서비스 시작 시 "진행 중" 인데 결과가 없는 승인은 실패 상태로 풀어라(시작 시점엔 돌고 있는 렌더가 없다).
이러면 BE 재요청 시 다시 렌더된다. 첫 시도가 BE 전달까지 했을 수 있으므로 **중복 전달 가능성**을 결과에 적어라
(BE 가 `generation_id` 로 멱등 처리하는지는 우리가 확인하지 못했다 — 추정으로 안전하다고 쓰지 마라).

**백그라운드 전달 재시도**(`service.py:471` `_retry_delivery`)의 작업 레코드 쓰기도 원자적 갱신으로 바꿔라.

### C. 작업 생성 멱등성 · 조회 비용 (리뷰 2·3번)

- `detail_page_jobs` 에 멱등성 **범위 키 컬럼** 추가: `product_id` 가 NULL 이어도 성립하게 만들어라
  (예: `coalesce(product_id, '')` 와 키를 합친 한 컬럼). 그 컬럼에 UNIQUE 인덱스. SQLite 는 NULL 을 서로 다르게 봐서
  단순 `UNIQUE(product_id, idempotency_key)` 로는 NULL 끼리 중복을 못 막는다
- `create` 가 중복으로 실패하면 → 기존 작업을 읽어 **요청 지문 비교** → 같으면 기존 작업 반환, 다르면 `IdempotencyConflictError`
- `find_by_idempotency` 는 그 컬럼 WHERE 조회로. 전체 스캔·전체 역직렬화 제거
- **기존 DB 마이그레이션**: 컬럼 추가 → `payload_json` 에서 백필 → UNIQUE 인덱스. 기존 데이터에 이미 중복 키가 있으면
  인덱스 생성이 실패한다. **어떻게 처리했는지 결과에 적어라. 조용히 무시하지 마라**
- 인메모리 저장소도 같은 계약

### D. 전달 재시도 (리뷰 4번)

- `outbox.mark_failed` 에 재시도 가능 여부를 넘겨라. `retryable=False` 면 **재시도 목록에서 빠지는 별도 상태**
- **최초 전달**(`pipeline.py:449` 근처)과 **재시도**(`retry_backend_delivery`) 두 경로 모두
- 최초 전달이 재시도 가능하게 실패하면 `approve_draft` 가 **재시도를 예약**해라(지금은 안 한다)
- `_retry_delivery` 는 `exc.retryable` 이 False 면 재시도 예약 안 함
- 재시도가 **성공하면** 작업의 `approval_backend_delivery_pending` 을 False 로 (원자적 갱신으로)
- 시도 한도 초과·영구 실패는 `list_retryable` **과 `claim` 둘 다**에서 제외. 한도는 서비스의 `max_delivery_attempts` 와 같게
- SQLite·인메모리 outbox 둘 다
- 상태 조회 API 에 전달 대기 여부를 노출하는 것(`ai_dto.py:85`)은 **BE 계약 변경이라 하지 마라.** 결과에 후속 과제로 적어라

### E. 미사용 import 4개

`ruff check --select F401 src` 의 4개만. **`ruff format` 전체 재포맷은 하지 마라**

## 테스트 — 실패→통과를 보여라

1. 느린 가짜 승인(예: 2초) 중에 `/health` 가 즉시 응답 (동시 요청)
2. 같은 승인을 스레드 2개에서 동시에 → 렌더 1번
3. 렌더 실패 후 같은 승인 재요청 → 다시 렌더
4. 승인 진행 중 `save_draft` → 거절 / 오래된 버전 `save_draft` → 충돌
5. 같은 멱등성 키로 작업 생성을 스레드 2개에서 동시에 → 작업 1개 (`product_id` 있음·없음 둘 다)
6. 새 컬럼이 없는 기존 DB 파일을 열면 백필되고 멱등성 조회가 동작
7. `retryable=False` 전달 실패(최초·재시도 둘 다) → 재시도 예약 없음, `list_retryable`·`claim` 에서 빠짐
8. 시도 한도 초과 → `list_retryable`·`claim` 에서 빠짐
9. 재시작: 진행 중 표시가 남은 승인 → 서비스 시작 시 풀림
10. 재시도 성공 → `approval_backend_delivery_pending` 이 False

**수정 전 코드로 1·2·5·7·8 이 실패하는 것**을 보여라. git 을 쓰지 말고, 수정 전 파일을 임시 복사해 두고 비교하는 식으로 해라.

## 보고 — 이 파일 하단에 `## 결과`

- 전체 `.venv/bin/python -m pytest -q` 결과
- 파일별 변경 요약
- 마이그레이션 중복 키 처리 방식
- 재시작 복구 시 중복 전달 가능성
- 수정 전 실패 증거
- 하지 않은 것(상태 API 노출 등)과 이유

## 결과

- 전체 검사: `.venv/bin/python -m pytest -q` → **450 passed, 2 warnings** (기존 Starlette/AnyIO deprecation 경고). `ruff check --select F401 src`와 `git diff --check`도 통과했다.
- 수정 전 증거: 새 회귀 테스트를 구현 전에 실행했을 때 `tests/test_concurrency_fix.py`가 **19 failed**였다. 특히 느린 내부 승인이 `/health`를 약 0.51초 막았고(기준 0.3초), 동시 승인에서 렌더가 2회 호출됐으며, 동일 생성 키의 동시 요청이 서로 다른 작업 ID를 받았다(`product_id` 유무 모두). 최초 영구 전달 실패는 `FAILED`로 남았고, 한도에 도달한 전달도 `list_retryable`에 남았다. 즉 요청한 1·2·5·7·8의 실패를 수정 전에 확인했다. 최종 회귀 테스트는 SQLite 사례를 보강한 **23 passed**다.
- `src/detail_page_ai/app.py`: 내부·legacy 승인 렌더와 초안 저장을 `run_in_threadpool`로 옮겼다. 승인 응답은 동기 완료 형태를 유지한다.
- `src/detail_page_ai/persistence.py`: 작업 레코드의 잠금 기반/`BEGIN IMMEDIATE` 기반 원자적 `update`를 추가하고, 승인 상태와 시도 ID를 영속화했다. 생성 키 범위 컬럼·UNIQUE 인덱스·조회 인덱스 경로를 추가했다. 두 outbox에 영구 실패 상태와 서비스 설정 시도 한도를 적용해 재시도 조회와 선점에서 제외했다.
- `src/detail_page_ai/service.py`: 생성 키 충돌 시 기존 작업의 지문을 비교한다. 승인을 렌더 전에 원자적으로 선점하고 완료/실패를 기록하며, 시작 시 미완료 선점을 해제한다. 초안 버전 검사, 작업 진행·완료 기록, 백엔드 재시도 후 승인 대기 상태 갱신을 원자적으로 처리한다. 재시도 가능한 최초 전달 실패만 예약하고 영구 실패는 예약하지 않는다.
- `src/detail_page_ai/pipeline.py`: 최초 전달과 재시도 양쪽에서 `BackendDeliveryError.retryable`을 outbox에 전달하고 미사용 import를 제거했다.
- `src/detail_page_ai/dto.py`, `src/detail_page_ai/training_augmentation.py`: F401 정리. `dto.GenerationOptions`는 기존 코드가 가져다 쓰는 공개 이름이므로 제거하지 않고 명시적 재수출로 유지했다.
- `tests/test_concurrency_fix.py`: 이벤트 루프 응답성, 승인·생성 동시성, 실패 후 재승인, 초안 버전, 기존 DB 백필/중복, 두 outbox의 영구 실패·시도 한도, 재시작 복구, 전달 성공 후 대기 해제, 원자적 롤백을 검증한다. `tests/test_service.py`는 기존 단계 순서 검사의 관찰 지점을 `save`에서 새 원자적 `update`로 옮겼고 기대 단계 목록은 유지했다.
- 기존 DB에 같은 범위 키가 이미 여러 건이면 마이그레이션에서 `ValueError`로 **명시적으로 실패**하며 트랜잭션을 롤백한다. 데이터를 임의로 선택하거나 중복을 숨기지 않는다. 운영자가 중복 레코드를 정리한 뒤 다시 시작해야 한다. `product_id=NULL`도 범위 키 JSON 표현으로 UNIQUE 검사를 받는다.
- 재시작 시 진행 중 승인 표시는 해제되어 같은 요청을 다시 렌더할 수 있다. 첫 시도가 백엔드 전달까지 마친 뒤 중단됐다면 **중복 전달 가능성**이 있다. BE가 `generation_id`로 중복 제거하는지는 확인되지 않았다.
- BE 상태 조회 DTO에 전달 대기 여부를 추가하지 않았다. 이는 BE 계약 변경이므로 별도 합의가 필요한 후속 과제다. 전체 파일 재포맷과 커밋도 하지 않았다.
