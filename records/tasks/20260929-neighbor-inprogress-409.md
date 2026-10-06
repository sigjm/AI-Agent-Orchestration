# 검수 지적 1건 — "승인 진행 중"이 400 "Invalid product image" 로 나간다

## 권한과 금지

- 수정 허용: `src/`, `tests/`, 이 파일 하단 `## 결과`
- **git 상태 변경 금지** (reset/checkout/commit/stash/restore/switch)

## 검수 결과

잘 고쳤다. 내가 직접 확인한 것:
- 전체 450 passed. 수정 전 코드에 새 테스트를 돌려 **행동 실패**를 확인했다 — `/health` 0.507초,
  동시 승인 렌더 2회, 동시 생성 작업 ID 2개, 영구 실패가 `FAILED`, 한도 초과 건이 목록에 남음
- 선점 → 렌더(트랜잭션 밖) → 시도 ID 확인 후 완료 / 자기 시도만 해제 흐름이 맞다
- `tests/test_service.py` 변경은 관찰 지점 이동일 뿐 약화가 아니다

## 고칠 것 — 하나

`service.approve_draft` 의 `reserve` 가 진행 중이면 `ValueError("Approval is already in progress")` 를 던진다.
그런데 `app.py` 의 `approve_internal_detail_page` 는 `ValueError` 를 **400 "Invalid product image"** 로 바꾼다.

```
BE 가 렌더 도중 같은 승인을 재요청
  수정 전: 첫 렌더가 끝날 때까지 기다렸다가 200 (결과)
  지금  : 400 "Invalid product image"   ← 틀린 메시지 + 영구 오류로 보임
```

BE 가 4xx 를 영구 실패로 처리하면 **곧 성공할 렌더를 실패로 기록**한다. 수정 전엔 죽은 코드라 안 보였던 경로다.

1. 전용 예외(예: `ApprovalInProgressError`)를 만들어 `reserve` 에서 던져라
2. `finish` 에서 시도 ID 가 바뀌어 `LeaseOwnershipError` 가 나는 경우도(다른 시도가 선점 — 재시작 뒤에만 가능)
   같은 예외로 바꿔라. 지금은 앱에서 매핑이 없어 500 이 된다
3. `approve_internal_detail_page` 에서 이 예외를 **409, detail "Approval is already in progress"** 로 매핑해라.
   기존 `IdempotencyConflictError` → 409 "Idempotency key conflict" 와 **detail 로 구분**되게
4. HTTP 수준 테스트: 느린 승인 중 같은 승인을 한 번 더 보내면 **409 + 그 detail** 이고 400 이 아님.
   수정 전(지금 코드)에서 400 이 나오는 것도 보여라

## 하지 말 것

- `"Draft is not ready for approval"` 도 같은 400 "Invalid product image" 로 나가는데, 이건 **이번 수정 전부터 있던 문제**라 건드리지 마라.
  결과에 따로 적기만 해라
- 초안 저장의 409 "Draft cannot be saved" 는 그대로 둬라

## 보고 — 이 파일 하단 `## 결과`

- 전체 pytest 결과, 바꾼 곳, 수정 전 400 이 나오던 증거

## 결과

- 수정 전 HTTP 회귀 테스트: 첫 승인 렌더 중 같은 요청을 보내면 첫 요청은 200, 두 번째 요청은 **400 `{"detail":"Invalid product image"}`** 였다. 완료 직전 승인 시도 ID를 바꾼 경우에는 `LeaseOwnershipError`가 났다.
- `src/detail_page_ai/service.py`: `ApprovalInProgressError`를 추가하고 승인 선점 중 중복 요청과 완료 시 시도 ID 불일치에 사용했다. 불일치 시 기존 시도의 실패 정리가 새 시도 ID를 지우지 않는 것도 테스트했다.
- `src/detail_page_ai/app.py`: 내부 승인 엔드포인트에서 이 예외를 **409 `{"detail":"Approval is already in progress"}`** 로 매핑했다. 멱등성 충돌의 기존 409 detail은 유지했다.
- `tests/test_concurrency_fix.py`: 실제 HTTP 동시 요청의 409 응답과 완료 직전 시도 교체를 검증하는 테스트 2개를 추가했다.
- 전체 `.venv/bin/python -m pytest -q`: **452 passed, 2 warnings** (기존 Starlette/AnyIO deprecation 경고). `ruff check --select F401 src`도 통과했다.
- `"Draft is not ready for approval"`이 400 `"Invalid product image"`로 나가는 기존 문제는 이번 범위에서 수정하지 않았다. 초안 저장의 409 `"Draft cannot be saved"`도 그대로다. Git 상태 변경과 커밋은 하지 않았다.
