# 수정 작업 — 운영·배포 문서 (치명 1건 + 불일치 4건 + 사소 2건)

검수에서 확정된 결함만 고칩니다. **코드는 고치지 마세요.**

## 담당 파일 (이 4개만 수정. 다른 파일은 다른 워커가 동시에 고치는 중이니 절대 건드리지 마세요)
- docs/operations/aws-migration-checklist.md
- docs/operations/aws-deployment.md
- docs/operations/ubuntu-deployment.md
- .env.example

## 고칠 것

### [치명 C-3] EKS PVC 용량 "최소 20Gi"
- `docs/operations/aws-migration-checklist.md:140` 의 `(EKS 설계 시 gp3 스토리지 클래스 기반 최소 20Gi ReadWriteOnce EBS PVC)`.
- 모델 가중치만 약 30GB 다(텍스트 19.6 GiB + 이미지 10.2 GiB). 20Gi 로 만들면 최초 기동 중 모델 다운로드가 디스크 풀로 실패한다.
- `docs/operations/eks-workload-spec.md:128` 이 **100Gi 권장**이므로 그 값으로 맞추고, 왜 그 크기인지(모델 약 30GB + 산출물·캐시) 한 줄 덧붙일 것.

### [불일치 I-2] 단위 테스트 개수 353 → 358
- `docs/operations/aws-deployment.md:13` 과 `:346`, `docs/operations/aws-migration-checklist.md:13` 과 `:213` 이 `353개`로 적었다.
- 실제 `.venv/bin/python -m pytest -q` 결과는 **358 passed** 다. `/health`·`/health/ready` 추가로 테스트 5건이 늘었다.
- 네 곳 모두 358 로 고칠 것. **주변의 "GPU 에서는 한 번도 실행되지 않았다" 문장은 사실이므로 그대로 둘 것.**

### [불일치 I-3] 헬스체크를 아직 404 방식으로 안내
- 다음 네 곳이 "없는 작업 조회 시 404 반환"을 헬스체크로 안내한다.
  - `docs/operations/aws-deployment.md:106` — "현재 FastAPI 의 기본 헬스체크 방식(없는 작업 조회 시 404)은 K8s httpGet probe 로 쓸 수 없으므로 exec probe 나 전용 200 엔드포인트가 필요하다"
  - `docs/operations/aws-deployment.md:136` — Dockerfile 헬스체크 표
  - `docs/operations/aws-deployment.md:290` — curl 예시
  - `docs/operations/aws-migration-checklist.md:170` — 0단계 점검
- 정본: `GET /health` 가 이미 구현돼 200 을 반환한다(`src/detail_page_ai/app.py:158`). `Dockerfile:55-56` 과 `sglang/Dockerfile:123-124` 의 HEALTHCHECK 도 `/health` 를 쓴다. readiness 용 `GET /health/ready` 도 있다(`:163`).
- 네 곳을 `GET /health` 200 기준으로 고칠 것. `:106` 의 "전용 200 엔드포인트가 필요하다"는 **이미 해소된 gap** 이므로 해소됐다고 고쳐 쓸 것. K8s 가 Dockerfile HEALTHCHECK 를 무시한다는 서술은 사실이므로 유지.

### [불일치 I-5] ubuntu-deployment.md 에 검증 상태 면책 문구가 없음
- 형제 문서 3개에는 모두 있다: `aws-deployment.md:13`, `aws-migration-checklist.md:13`, `eks-workload-spec.md:7`.
- `docs/operations/ubuntu-deployment.md` 에는 "GPU 에서 한 번도 실행되지 않았다"는 서술이 **한 곳도 없다.** 운영자가 가장 먼저 따라가는 문서라 누락이 크다.
- 문서 상단(제목 직후)에 형제 문서와 같은 취지의 검증 상태 블록을 추가할 것. 담을 내용:
  - 단위 테스트 358개는 Mac 로컬에서 통과했다.
  - **이 구성은 GPU 에서 한 번도 실행된 적이 없고, 이미지도 아직 빌드하지 않았다.**
  - 두 모델 동시 적재, 4bit 파이프라인 로딩, 생성·편집 품질, 처리 시간은 전부 미검증이며 첫 배포에서 실측해야 한다.
  - 확인 항목은 이 문서의 검증 체크리스트에 있다.
- **본문의 다른 서술은 고치지 말 것.** 4.3절의 `docker compose ps` 출력은 `출력 예시` 라고 이미 명시돼 있어 결함이 아니다.

### [불일치 I-4] `.env.example` 이미지 모델 기본값 주석
- `.env.example:39` 주석 머리글이 `[기본값: black-forest-labs/FLUX.2-klein-4B] (가중치 7.22 GiB, Apache 2.0 라이선스)` 다.
- 실제 값은 46행 `IMAGE_MODEL_PATH=circulus/FLUX.2-klein-9B-bnb-4bit` 이고 이것이 관리자 결정으로 확정된 기본값이다.
- 주석 머리글을 실제 기본값으로 바꾸고, `FLUX.2-klein-4B` 는 **대안(Apache 2.0)** 으로 내려 적을 것. 원본 9B 가 FLUX Non-Commercial License 라는 고지는 **반드시 유지**할 것.

### [사소 T-1] `.env.example:31` 정적 선점 용량
- `0.50 (약 24.0 GiB)` 로 적혀 있다. L40S 48GB 의 실제 가용은 **44.7 GiB** 이므로 0.50 은 **22.35 GiB** 다. 48 을 10진으로 오인한 계산이다.
- 같은 파일 30행의 `19.6 / 48 ≈ 0.41` 도 44.7 기준으로 다시 계산해 맞출 것.

### [사소 T-2] `aws-deployment.md:163` 용어 오류
- `| 가중치 하한 합계 | 약 32.55 GiB |` 로 적혀 있다.
- 순수 가중치 합은 **29.8 GiB**(19.6 + 10.2) 이고, 32.55 는 **텍스트 정적 선점(22.35) + 이미지 가중치(10.2)** 다.
- 항목 이름을 실제 의미에 맞게 고치고, 필요하면 가중치 합 행을 따로 둘 것.

## 지켜야 할 것
- **코드 변경 금지.**
- `docs/operations/` 안에서도 다음은 **절대 수정 금지**다: `sglang-serving-research.md`, `sglang-vllm-fit.md`, `local-generation-test-report.md`, `server-memory-estimate.md`, `local-llm.md`, `orchestration.md`, `eks-workload-spec.md`. 앞의 넷은 시점 기록이고 `eks-workload-spec.md` 는 이미 확정돼 인프라팀에 전달됐다.
- **검증되지 않은 것을 검증된 것처럼 쓰지 말 것.** 수치를 올릴 때도 "미검증 추정치" 표시가 있으면 유지할 것.
- 끝나면 `.venv/bin/python -m pytest -q` 로 **358 passed** 확인. `.env.example` 값을 검사하는 테스트가 있으니(`tests/test_security.py`) 반드시 돌릴 것.

## 보고
`## 결과` 에 파일별 `행 번호 · 전 → 후` 를 적고, 마지막 줄에 `완료: 수정 N개 파일, 테스트 358 passed` 출력.
