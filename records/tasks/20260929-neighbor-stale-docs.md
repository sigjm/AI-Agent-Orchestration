# 오래된 상시 문서 현황 갱신

## 배경

네 조사 보고서(`20260929-neighbor-doc-inventory.md`)를 검수했다. "갱신이 필요한 상시 문서" 5건과
Phase 3 README 문구 1건을 원문과 대조해 **전부 사실로 확인했다.** 이제 고친다.

## 고칠 것 — 이 6개 파일만

| 파일 | 고칠 부분 |
| --- | --- |
| `docs/evaluation/metrics-definition.md` | 1절·5절의 "60건 전체 평가 미실행" 등 실행 **현황** 문구. 지표 **정의**는 건드리지 마라 |
| `docs/architecture/ai-evaluation-and-safety-policy.md` | 데이터셋 현황표의 "모델 실행 대기" |
| `docs/architecture/ai-architecture-and-safety.md` | 평가 데이터셋 절의 같은 현황 |
| `docs/operations/ubuntu-deployment.md` | 상단 검증 상태의 "이미지도 아직 빌드하지 않았습니다" |
| `docs/operations/aws-deployment.md` | EKS 전환·검증 상태 |
| `docs/superpowers/specs/2026-08-27-source-preserving-detail-page-design.md` | 상단 구현 메모의 "현재 실행 경로는 로컬 Gemma + Flux2" |
| `docs/deliverables/phase3/README.md` | 5행 "원본을 그대로 옮긴 복사본" — 05번은 9줄 스텁이 아니라 620줄 통합 명세 전문이다 |

## 원칙 — 반드시 지켜라

1. **상태를 세 가지로 나눠 적어라. 섞지 마라.**
   - 모델 실행 여부 (예: 10차에서 60건 실행됨)
   - 권리 최종 확인 여부
   - 사람 라벨·점수 여부 — **이 프로젝트에 사람 검수 점수는 없다.** 가이드가 있다고 점수가 있는 게 아니다
2. **배포 상태도 세 가지로 나눠라.** 이미지 빌드(9/18 amd64) / Stage 기동 시도(9/23, 텍스트 서버 캐시 예산 실패 → 수정됨) /
   **GPU 추론 성공은 아직 확인되지 않았다.** "EKS 로 배포 완료" 같은 과장 금지
3. 갱신한 문장마다 **근거 문서와 날짜**를 괄호로 달아라. 예: `(round-10, 2026-09-11)`
4. 기존 문장을 지우지 말고 대체하되, 그 문서에 날짜가 박힌 이력 절이 있으면 그 절은 건드리지 마라
5. 8/27 설계서는 **상단 구현 메모만** 고쳐라. 본문의 당시 설계(Bedrock·Gemma 예시)는 당시 기록이라 그대로 둔다.
   메모에 "본문 모델명은 당시 기준이며 현재 로컬 분석 모델은 Qwen3.8-27B" 식으로 적어라

## 하지 말 것

- 위 7개 파일 외 수정 금지. 특히 날짜 붙은 시점 기록(`evaluation/*-2026-*`, `operations/*-handoff-*`, 차수 기록)은 절대 수정 금지
- 문서에 없는 사실을 만들지 마라. 확신 없으면 `확인 필요`
- 커밋 금지

## 보고

이 파일 하단에 `## 결과`:
- 파일별로 바꾼 문장 **전/후**를 짧게
- 각 변경의 근거 문서
- `git diff --stat`

## 결과

지정된 **7개 문서**의 현황 문구만 갱신했다. 날짜가 붙은 시험·인계·차수 기록과 지표 정의는 수정하지 않았고, 커밋하지 않았다. 모델 실행, 권리 최종 확인, 사람 라벨·점수는 각각 별도 상태로 적었다. 배포도 이미지 빌드, Stage 시도·수정, GPU 추론 성공 여부를 구분했다.

최종 점검 중 다른 세션이 동일한 7개 변경을 `3bbf4a6`으로 커밋했다. 승인받아 `git reset --mixed HEAD^`로 그 커밋만 해제했고, 7개 문서 수정은 작업트리에 미커밋 상태로 남겼다.

| 파일 | 변경 전 → 변경 후 (요지) | 근거 문서·날짜 |
| --- | --- | --- |
| `docs/evaluation/metrics-definition.md` | “60건 전체 평가 미실행”, “실제 Gemma/Flux 실행 필요” → 10차에서 `cma_real_v1` **60/60 모델 실행 완료**. 권리 최종 확인과 사람 정답 라벨은 마지막 데이터 점검에서 대기, 이후 완료 근거는 확인 필요. 사람 검수 점수는 없음. 9월 8일 smoke test는 당시 기록으로 표시했다. | `docs/evaluation/pilot-report-2026-09-09.md` (2026-09-09); `docs/deliverables/experiments/round-10/03-experiment-report.md` (2026-09-11); `docs/data/collection-license-cleaning-plan.md` (2026-09-08); `docs/deliverables/phase4/01-ai-evaluation-report.md` (2026-09-22) |
| `docs/architecture/ai-evaluation-and-safety-policy.md` | “파일·검증만 완료, 모델 실행 대기” → 60/60 실행 완료. 권리 승인, 사람 라벨, 사람 점수의 상태를 각각 명시했다. | `round-10/03-experiment-report.md` (2026-09-11); `collection-license-cleaning-plan.md` (2026-09-08); `phase4/01-ai-evaluation-report.md` (2026-09-22) |
| `docs/architecture/ai-architecture-and-safety.md` | 평가 입력군 표의 “권리·라벨·모델 실행 대기” → 모델 실행 완료 / 권리 최종 확인 대기 / 사람 정답 라벨 대기 / 사람 점수 없음으로 분리했다. | `round-10/03-experiment-report.md` (2026-09-11); `collection-license-cleaning-plan.md` (2026-09-08); `phase4/01-ai-evaluation-report.md` (2026-09-22) |
| `docs/operations/ubuntu-deployment.md` | “이미지도 아직 빌드하지 않았고 GPU 미실행” → 9월 18일 `linux/amd64` 이미지 빌드 확인, 9월 23일 Stage EKS 기동 시도와 텍스트 캐시 예산 실패·기동 순서 수정 기록. 수정본의 GPU 추론 성공은 미확인으로 남겼다. | `docs/operations/eks-workload-spec.md` (2026-09-18); `docs/operations/infra-handoff-2026-09-23b.md` (2026-09-23) |
| `docs/operations/aws-deployment.md` | “EKS 산출물 전무·미결정, GPU 컨테이너 기동 이력 없음” → EKS 이미지 빌드, Stage 기동 실패와 수정 이미지 발행을 반영했다. Compose는 문서의 설계 기준으로 구분하고, EKS 운영 채택 및 GPU 추론 성공은 확인 필요로 남겼다. | `docs/operations/aws-migration-checklist.md` (2026-09-16); `docs/operations/eks-workload-spec.md` (2026-09-18); `docs/operations/infra-handoff-2026-09-23b.md` (2026-09-23) |
| `docs/superpowers/specs/2026-08-27-source-preserving-detail-page-design.md` | 상단 “현재 로컬 Gemma + Flux2” → 본문의 Bedrock·Gemma는 당시 설계 기록이며, 현재 로컬 기본 분석은 Qwen3.8-27B, 이미지는 Flux2 Klein 9B라고 명시했다. 본문 설계는 그대로 뒀다. | `docs/operations/local-llm.md` (2026-09-17) |
| `docs/deliverables/phase3/README.md` | “5개 문서 모두 원본 그대로 복사” → 01~04는 복사본, 05는 9줄 원본 스텁과 BE/FE 통합 명세 전문을 함께 실은 제출본이라고 명시했다. | `docs/deliverables/01-implementation-checkpoint.md` (2026-09-09); `docs/deliverables/05-be-fe-interface.md` (2026-09-17); `docs/api/be-fe-ai-integration-spec.md` (2026-09-23) |

`git diff --stat`:

```text
 docs/architecture/ai-architecture-and-safety.md    |  2 +-
 .../ai-evaluation-and-safety-policy.md             |  7 +++--
 docs/deliverables/phase3/README.md                 |  3 ++-
 docs/evaluation/metrics-definition.md              | 25 ++++++++++-------
 docs/operations/aws-deployment.md                  | 31 +++++++++++-----------
 docs/operations/ubuntu-deployment.md               |  7 ++---
 ...6-08-27-source-preserving-detail-page-design.md |  4 +--
 7 files changed, 46 insertions(+), 33 deletions(-)
```
