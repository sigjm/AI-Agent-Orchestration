# outbox 콜백 재전송 버그 수정 — PR 올리고 머지까지

관리자 지시. 사용자 요청: "1번 코덱스 시켜서 PR 올리고 머지까지 진행해".
이 작업에 한해 **git 커밋·브랜치·push·PR·머지를 허용**한다(아래 범위 안에서만). 결과는 이 파일 하단 `## 결과`에 한국어로.

## 무엇을 반영하나

2026-10-01 Ubuntu E2E에서 네가 찾고 고친 버그다(`20261001-ubuntu-e2e.md` 참고).
AI가 BE 콜백을 SQLite outbox에 저장했다가 다시 꺼내 보낼 때 BE 전용 DTO(`AiToBePersistRequestDto`)의 camelCase 별칭이 사라져
`metadata.productId`·`metadata.detailPage.reactDocument`가 빠지고 BE `AiCallbackController`가 500을 낸다(재시도 8회 모두 실패).
Stage에서도 첫 콜백이 실패해 outbox 재전송으로 넘어가면 같은 일이 생긴다.

작업 트리에 이미 있는 변경:
- `src/detail_page_ai/persistence.py`
- `tests/test_persistence.py` (`test_outbox_reopen_preserves_strict_be_callback_wire_aliases`)

## AWS에 필요한 것만 (사용자 추가 지시)

사용자: "그 PR은 AWS에서만 필요한 작업만 PR하게 해야 한다".
- PR에는 **AWS Stage 런타임에 실제로 필요한 변경**(outbox 콜백 별칭 수정)과 그 회귀 테스트(GenAI CI가 돌린다)만 넣는다.
- Mac·Ubuntu 테스트 환경에서만 의미 있는 것은 넣지 않는다: MLX·로컬 설정(`local.env` 등), Ubuntu E2E용 compose·스크립트·우회 코드, FE·BE 사본 수정, 문서, 증거 파일.
- 검토 중 고친 내용 중에도 로컬 테스트 편의를 위한 분기·설정이 있으면 빼고, 결과에 무엇을 뺐는지 적는다.

## 커밋하면 안 되는 것

작업 트리의 다른 변경은 **건드리지도, 커밋하지도 않는다**: `docs/phase4/README.md`, `docs/phase4/operations/gpu-sequential-model-loading-design.md`, `excalidraw-diagram-skill/`.
`git add`는 위 두 파일만 경로로 지정한다(`git add -A`, `git add .` 금지).

## 순서

1. **검토**: diff를 다시 읽고 확인한다
   - 새로 저장하는 outbox 행이 BE 콜백 DTO면 별칭으로 저장되고, 복원 시 같은 DTO로 돌아오는지
   - 배포 전에 쌓인 옛 형식 행(별칭 없는 snake_case)도 복원·재전송이 되는지 — 옛 행 복원 테스트가 없으면 추가
   - `except ValueError` 범위가 넓어 진짜 오류를 삼키지 않는지
2. **테스트**: `uv run pytest -q` 전체 통과 (이전 기준 533 passed + 새 테스트). 실패하면 고치고, 못 고치면 멈추고 결과에 쓴다
3. **작업 저장소 PR** (`sigjm/Team3_EcommerceSystemAI`)
   - 현재 브랜치 `deploy/ubuntu`에서 `fix/outbox-callback-aliases` 브랜치를 만들어 두 파일만 커밋
   - 커밋 메시지·PR 제목은 기존 관례(영어 `fix: ...`, 예: #13 `fix: draw React document sections in the PNG's colors`), PR 본문은 한국어로 원인·수정·테스트 결과
   - base `deploy/ubuntu`로 PR → 머지(이 저장소는 CI가 없다) → 로컬 `deploy/ubuntu`를 원격과 맞춘다. 작업 트리의 다른 변경이 사라지지 않게 주의
4. **GenAI 동기화 PR** (`Jangingmall/GenAI`, 상세페이지 코드는 `page_generation/` 아래)
   - 관례는 GenAI #59: 브랜치 `sync/outbox-callback-aliases`, 같은 두 파일을 `page_generation/src/detail_page_ai/persistence.py`, `page_generation/tests/test_persistence.py`로 반영, 본문에 "작업 저장소 sigjm/Team3_EcommerceSystemAI#<번호>와 같은 내용"
   - GenAI `main`의 두 파일이 작업 저장소의 머지 직전 내용과 같은지 먼저 확인하고(다르면 멈추고 보고), 같으면 덮어쓴다
   - CI(Docker validation·Test 등) **전부 통과 확인 후** 머지. 실패하면 원인을 고치거나 멈추고 보고
5. 머지 뒤 `main` 푸시로 도는 이미지 발행 워크플로가 성공하는지 확인하고 page-generation 이미지 digest를 결과에 적는다. **인프라 저장소에는 아무것도 올리지 않는다**(갱신 요청 메시지는 관리자가 따로 쓴다)

## 결과에 쓸 것

- 검토에서 바꾼 점, 테스트 결과(통과 수)
- 작업 저장소 PR 번호·머지 커밋, GenAI PR 번호·CI 결과·머지 커밋
- 발행된 page-generation 이미지 digest와 발행 워크플로 실행 링크

## 결과

- **검토·수정:** BE 콜백 DTO는 outbox 저장 시 alias로 직렬화하고, 복원 시 `AiToBePersistRequestDto`로 되살리도록 확인했습니다. 옛 snake_case 행도 strict DTO의 `populate_by_name`으로 복원돼 재전송 wire payload에서 `productId`와 `detailPage.reactDocument`를 보존하는 테스트를 추가했습니다. 잘못된 strict payload를 기본 DTO로 강등해 검증 오류를 삼키던 `except ValueError` fallback은 제거했고, 손상된 payload가 실패하는 테스트도 추가했습니다.
- **범위:** 변경은 `persistence.py`와 `test_persistence.py` 두 파일뿐이며 AWS Stage outbox 경로와 회귀 테스트입니다. 로컬/MLX 설정, E2E compose·스크립트·우회, FE·BE 사본, 문서 및 증거 파일은 PR에 포함하지 않았습니다. `docs/phase4/README.md`, `docs/phase4/operations/gpu-sequential-model-loading-design.md`, `excalidraw-diagram-skill/`의 기존 작업 트리 변경도 수정·스테이징·커밋하지 않았습니다. 인프라 저장소에는 push하지 않았습니다.
- **테스트:** 작업 저장소 `uv run pytest -q tests/test_persistence.py` — 14 passed; `uv run pytest -q` — 536 passed, 2 deprecation warnings. GenAI `page_generation` 로컬 CI 명령도 536 passed, 2 deprecation warnings.
- **작업 저장소 PR:** [#14](https://github.com/sigjm/Team3_EcommerceSystemAI/pull/14), `deploy/ubuntu`로 병합. 병합 커밋 `5e13109db33f5f093c5968264ad272bb4484e97d`. CI 없음. 로컬 `deploy/ubuntu`를 원격 병합 커밋까지 fast-forward했습니다.
- **GenAI 동기화:** 최신 `origin/main`과 작업 저장소의 병합 전 파일 두 개가 일치함을 확인한 뒤 동기화했습니다. [PR #61](https://github.com/Jangingmall/GenAI/pull/61)은 Test page-generation, Test chatbot-api, 세 Docker validation 및 AWS CodeBuild가 모두 통과한 뒤 병합됐습니다. 병합 커밋 `16ed39eb3b7ebfec7b80223f64216b80f003d6e3`.
- **이미지 발행:** main push workflow [#37259193933](https://github.com/Jangingmall/GenAI/actions/runs/37259193933) 전체 성공. page-generation 이미지 `<aws-account>.dkr.ecr.ap-northeast-2.amazonaws.com/jangin-ai/page-generation@sha256:5321fe7be40a23b9e0ec5d2e817e9a46b19ce3df04d7a8bc83e43d30248fcc5c` 발행을 확인했습니다.
