# 운영·배포 문서 검수 보고서 (대조 검증)

- **검수자 (워커)**: agy
- **검수일시**: 2026-09-16
- **대조 대상 파일**:
  - `docs/operations/aws-deployment.md`
  - `docs/operations/aws-migration-checklist.md`
  - `docs/operations/eks-workload-spec.md`
  - `docs/operations/local-generation-test-report.md`
  - `docs/operations/local-llm.md`
  - `docs/operations/orchestration.md`
  - `docs/operations/server-memory-estimate.md`
  - `docs/operations/sglang-serving-research.md`
  - `docs/operations/sglang-vllm-fit.md`
  - `docs/operations/ubuntu-deployment.md`
- **대조 기준 (정본 소스코드 및 설정)**:
  - `.env.example`
  - `docker-compose.yml`
  - `Dockerfile`
  - `sglang/Dockerfile`
  - `sglang/entrypoint.sh`
  - `docker/sglang-diffusion.Dockerfile`
  - `notebooks/colab_sglang_smoke_test.ipynb`
  - `src/local_detail_page_ai/clients.py`
  - `src/detail_page_ai/app.py`

---

## 총평 및 요약

- **총 발견 건수**: 11건
  - **치명 (Fatal)**: 3건 (인프라팀이 이 문서대로 구성 시 배포 실패 또는 장애 직결)
  - **불일치 (Inconsistency)**: 5건 (문서와 코드/문서 간 사실 차이)
  - **사소 (Trivial)**: 3건 (수치 계산 오기, 주석 불일치, 규약 표기)
- **문서 간 대상 차이 정합성**:
  - `eks-workload-spec.md`(EKS, 단일 파드, 단일 컨테이너, 단일 PVC)와 `ubuntu-deployment.md`/`aws-deployment.md`(단일 호스트 EC2, Docker Compose, 3개 컨테이너)는 쿠버네티스 GPU 디바이스 플러그인의 배타적 할당 제약으로 인한 의도된 대상 분리이며 상호 모순이 아님을 확인했습니다.
- **Mac 로컬 문서 분리 상태**:
  - `local-llm.md`, `local-generation-test-report.md`, `server-memory-estimate.md`는 Mac 로컬(MLX, 포트 11234/11235) 전용 문서로 서버 운영 설정과 안전하게 분리되어 있습니다.

---

## 상세 발견 사항 목록

### 1. 치명 (3건)

#### [치명-01] EKS EBS PVC 용량 부족으로 최초 모델 다운로드 실패
- **대상 파일**: `docs/operations/aws-migration-checklist.md:140`
- **내용**: `(EKS 설계 시 gp3 스토리지 클래스 기반 최소 20Gi ReadWriteOnce EBS PVC)`
- **대조 근거 [확인]**:
  - `docs/operations/eks-workload-spec.md:128`: `용량: 100Gi 권장 (모델 약 30GB + 산출물·캐시)`
  - `docs/operations/eks-workload-spec.md:83`: 텍스트 가중치(19.6 GiB) + 이미지 가중치(10.2 GiB) = 약 29.8 GiB (~30 GB)
  - `sglang/Dockerfile:115-116`: 모델 다운로드 경로가 `/var/lib/detail-page-ai/models/huggingface`로 PVC에 저장됨
- **영향**: 체크리스트의 "최소 20Gi" 지침대로 인프라팀이 20Gi PVC를 생성하면 파드 최초 기동 시 모델 다운로드 도중 `No space left on device` 디스크 풀 에러로 컨테이너가 영구 충돌(CrashLoopBackOff)합니다.

#### [치명-02] Ubuntu 배포 가이드 내 '미검증(GPU 미실행)' 주의 문구 누락 및 검증 완료 단정
- **대상 파일**: `docs/operations/ubuntu-deployment.md:11, 151-157, 231-249, 341-426`
- **내용**:
  - 151-157행: `docker compose ps` 출력 예시로 `Up 5 minutes (healthy)`, `Up 15 minutes (healthy)` 상태를 단정 제시.
  - 231-249행: `실제 런타임 기동 결함 3건을 공식 문서 기반으로 진단하고 해결했습니다... 컨테이너 이미지화했습니다... 검증합니다`로 서술.
  - 341-426행: `상태 전이 확인: QUEUED → ANALYZING → EXTRACTING → RENDERING → COMPLETED` 등 정상 완료를 기정사실화.
- **대조 근거 [확인]**:
  - `docs/operations/eks-workload-spec.md:7`: `다만 이 Dockerfile 은 아직 빌드하지 않았고, GPU 에서도 한 번도 실행하지 않았습니다.`
  - `docs/operations/aws-deployment.md:13, 345-346`: `그러나 GPU 에서는 한 번도 실행되지 않았다. 두 모델 동시 적재, 4-bit 파이프라인 로딩, 편집 품질, 처리 시간 모두 미검증 상태이며 첫 배포 실측을 통해 확인해야 한다.`
  - `docs/operations/aws-migration-checklist.md:13, 213`: `GPU 에서는 한 번도 실행되지 않았다.`
- **영향**: 본 저장소의 GPU 서빙 구성은 실제 GPU에서 실행된 적이 없고 Dockerfile도 빌드된 적이 없는 상태입니다. 타 문서에는 이 면책 사실이 명확히 기재되어 있으나 `ubuntu-deployment.md`에는 문서 전반에 미검증 사실 경고가 누락되어 있어, 인프라 담당자가 이미 실서버에서 완벽히 검증된 운영 절차로 오인하게 만듭니다.

#### [치명-03] 애플리케이션 헬스체크 규격 구식화 (404 조회 vs 신규 200 /health 구현)
- **대상 파일**:
  - `docs/operations/aws-deployment.md:106`: `현재 FastAPI의 기본 헬스체크 방식(없는 작업 조회 시 404 반환)은 K8s의 httpGet probe(2xx/3xx만 정상 판정)로 사용할 수 없으므로 exec probe나 전용 200 상태 엔드포인트가 필요하다.`
  - `docs/operations/aws-deployment.md:136`: `| Dockerfile 헬스체크 | GET /api/v1/ai/detail-page-jobs/does-not-exist (404 응답 확인) |`
  - `docs/operations/aws-deployment.md:290`: `curl -sS http://<host>:8000/api/v1/ai/detail-page-jobs/does-not-exist # HTTP 404 수신 시 FastAPI 프로세스 정상 기동 확인`
  - `docs/operations/aws-migration-checklist.md:170`: `0단계 | 애플리케이션 컨테이너 기본 기동 | curl -sS http://<host>:8000/api/v1/ai/detail-page-jobs/does-not-exist | HTTP 404 수신`
- **대조 근거 [확인]**:
  - `Dockerfile:55-56`: `HEALTHCHECK ... c.request('GET','/health'); sys.exit(0 if c.getresponse().status == 200 else 1)`
  - `sglang/Dockerfile:123-124`: `HEALTHCHECK ... c.request('GET','/health'); sys.exit(0 if c.getresponse().status == 200 else 1)`
  - `src/detail_page_ai/app.py:158-160`: `@app.get("/health") def health() -> dict[str, str]: return {"status": "ok"}`
  - `docs/operations/eks-workload-spec.md:56`: `GET /health | liveness | 인증 없이 항상 200 + {"status":"ok"}`
- **영향**: 인프라팀이 `aws-deployment.md`나 `aws-migration-checklist.md`의 지침을 따를 경우 구식 404 방식 점검을 시도하게 되며, 쿠버네티스 프로브 설정 시 불필요한 우회책을 검토하게 됩니다. 이미 정식 `GET /health` (200 OK)가 구현되었으므로 정정이 필요합니다.

---

### 2. 불일치 (5건)

#### [불일치-01] SGLang 서빙 조사 보고서 내 두 모델 공존 VRAM 여유분 산수 모순
- **대상 파일**: `docs/operations/sglang-serving-research.md:148`
- **내용**: `AWQ-INT4 (cyankiwi/Qwen3.8-27B-AWQ-INT4, 19.60 GiB): 가중치 점유가 약 19.6 GiB로 낮아져, 두 모델 공존 시 가장 넉넉한 VRAM 여유분(~24 GiB)을 확보할 수 있습니다.`
- **대조 근거 [확인]**:
  - `docs/operations/sglang-serving-research.md:55`: `GPU 여유분: 44.70 - (22.35 + 10.18) = 12.17 GiB`
  - `docs/operations/sglang-serving-research.md:265`: `순수 가중치 합계 하한: 29.78 GiB | L40S 가용(44.70 GiB) 대비 여유분: 약 14.92 GiB`
  - `.env.example:19`: `L40S 48GB에서 텍스트 메모리를 ~24GB 수준으로 통제하여 확산 모델(FLUX 4B)과 공존 시 넉넉한 여유분(~21GB)을 확보함.`
- **설명**: L40S 실가용량 44.70 GiB에서 텍스트 가중치(19.60 GiB)와 이미지 가중치(10.18 GiB)의 순수 합계만 29.78 GiB입니다. 따라서 두 모델이 공존할 때 남는 여유분은 순수 가중치 기준 약 14.92 GiB, 텍스트 정적 선점(22.35 GiB) 기준 약 12.17 GiB입니다. "~24 GiB 여유분"은 텍스트 모델만 단독 적재했을 때의 잔여량($44.7 - 19.6 \approx 25.1\text{ GiB}$)을 두 모델 공존 여유분으로 잘못 적은 명백한 계산 오류입니다.

#### [불일치-02] SGLang 서빙 조사 보고서 내 기동 명령 `--revision` 누락
- **대상 파일**:
  - `docs/operations/sglang-serving-research.md:61-68` (텍스트 기동 명령)
  - `docs/operations/sglang-serving-research.md:72-80` (확산 기동 명령)
- **대조 근거 [확인]**:
  - `.env.example:25, 49`: `TEXT_MODEL_REVISION=6e134bae811fb5adac50ee042ae5f029ac6779aa`, `IMAGE_MODEL_REVISION=58c2804f31af12c8888504b96250010c50b55e44`
  - `docker-compose.yml:45, 88`: `--revision ${TEXT_MODEL_REVISION:-6e134bae811fb5adac50ee042ae5f029ac6779aa}`, `--revision ${IMAGE_MODEL_REVISION:-58c2804f31af12c8888504b96250010c50b55e44}`
  - `sglang/Dockerfile:50, 55`: `TEXT_MODEL_REVISION`, `IMAGE_MODEL_REVISION` 고정
  - `sglang/entrypoint.sh:5, 10`: `--revision "$TEXT_MODEL_REVISION"`, `--revision "$IMAGE_MODEL_REVISION"` 전달
  - `notebooks/colab_sglang_smoke_test.ipynb:618-619`: `TEXT_MODEL_REVISION`, `IMAGE_MODEL_REVISION` 고정
- **설명**: `sglang-serving-research.md`는 2026-09-14 초기 조사 문서로 작성되어 당시에는 `--revision` 인자가 포함되지 않았습니다. 현재 정본 기준 커밋 해시 고정이 필수 규칙으로 확정되었으므로 불일치합니다.

#### [불일치-03] SGLang 서빙 조사 보고서 내 대안 모델명(`--served-model-name`) 불일치
- **대상 파일**:
  - `docs/operations/sglang-serving-research.md:93`: `--served-model-name qwen-vl`
  - `docs/operations/sglang-serving-research.md:103`: `--served-model-name sglang-image`
- **대조 근거 [확인]**:
  - `.env.example:28, 52`: `TEXT_SERVED_MODEL_NAME=qwen-text`, `IMAGE_SERVED_MODEL_NAME=flux-klein`
  - `docker-compose.yml:46, 89`: `--served-model-name ${TEXT_SERVED_MODEL_NAME:-qwen-text}`, `--served-model-name ${IMAGE_SERVED_MODEL_NAME:-flux-klein}`
  - `sglang/Dockerfile:51, 56`: `TEXT_SERVED_MODEL_NAME=qwen-text`, `IMAGE_SERVED_MODEL_NAME=flux-klein`
  - `notebooks/colab_sglang_smoke_test.ipynb:613-614`: `IMAGE_MODEL_NAME = "flux-klein"`, `TEXT_MODEL_NAME = "qwen-text"`
- **설명**: 안 2 대안 초안의 예시 명령에 임의의 모델명(`qwen-vl`, `sglang-image`)이 기재되어 있어, 클라이언트 설정(`LOCAL_TEXT_MODEL=qwen-text`, `LOCAL_IMAGE_MODEL=flux-klein`)과 불일치합니다.

#### [불일치-04] 단위 테스트 통과 건수 문서 간 불일치 (353건 vs 358건)
- **대상 파일**:
  - `docs/operations/aws-deployment.md:13, 346`: `로컬 단위 테스트 353개 통과`
  - `docs/operations/aws-migration-checklist.md:13, 213`: `로컬 단위 테스트 353개 통과`
- **대조 근거 [확인]**:
  - `docs/operations/eks-workload-spec.md:7`: `애플리케이션 테스트 358개는 Mac 로컬에서 통과했습니다.`
  - `.venv/bin/python -m pytest -q` 실행 결과: `358 passed, 2 warnings in 10.79s`
- **설명**: FastAPI 헬스체크 probe 엔드포인트(`GET /health`, `GET /health/ready`) 추가 및 관련 단위 테스트 5종(`tests/test_app.py:446-578`) 추가로 전체 통과 건수가 353건에서 358건으로 증가했으나, `aws-deployment.md` 및 `aws-migration-checklist.md`에는 구 수치(353개)가 남아 있습니다.

#### [불일치-05] `.env.example` 내 이미지 모델 기본값 주석과 실제 설정값 불일치
- **대상 파일**: `.env.example:39, 46`
- **내용**:
  - 39행 주석: `# [기본값: black-forest-labs/FLUX.2-klein-4B] (가중치 7.22 GiB, Apache 2.0 라이선스)`
  - 46행 설정: `IMAGE_MODEL_PATH=circulus/FLUX.2-klein-9B-bnb-4bit`
- **대조 근거 [확인]**:
  - `docker-compose.yml:87`: `${IMAGE_MODEL_PATH:-circulus/FLUX.2-klein-9B-bnb-4bit}`
  - `sglang/Dockerfile:54`: `IMAGE_MODEL_PATH=circulus/FLUX.2-klein-9B-bnb-4bit`
  - `notebooks/colab_sglang_smoke_test.ipynb:615`: `IMAGE_MODEL_PATH = "circulus/FLUX.2-klein-9B-bnb-4bit"`
  - `docs/operations/aws-deployment.md:49`: `circulus/FLUX.2-klein-9B-bnb-4bit (약 10.2 GiB)`
- **설명**: 관리자 결정으로 기본 모델이 9B 4bit(`circulus/FLUX.2-klein-9B-bnb-4bit`)로 확정되었고 실제 환경변수도 그렇게 지정되어 있으나, 바로 윗행 주석 머리글에는 구 대안인 `black-forest-labs/FLUX.2-klein-4B`가 기본값으로 잘못 표기되어 있습니다.

---

### 3. 사소 (3건)

#### [사소-01] `.env.example` 및 `aws-deployment.md` 내 VRAM 50% 선점 수치 10진/2진 혼동
- **대상 파일**:
  - `.env.example:31`: `8192 컨텍스트의 기본 KV 캐시 풀을 포함하여 0.50 (약 24.0 GiB)을 초기값으로 지정합니다.`
  - `docs/operations/aws-deployment.md:161`: `약 22.35~24.0 GiB`
- **대조 근거 [확인]**:
  - `docs/operations/sglang-serving-research.md:46`: `NVIDIA L40S 48GB의 실제 가용 바이너리 용량은 44.70 GiB(48 * 10^9 bytes / 1024^3)입니다.`
  - `docs/operations/sglang-serving-research.md:53`: `--mem-fraction-static 0.50 (약 22.35 GiB 선점)`
  - `docs/operations/ubuntu-deployment.md:305`: `정적 선점 22.35 GiB (--mem-fraction-static 0.50)`
  - `docs/operations/eks-workload-spec.md:84`: `--mem-fraction-static 0.50 으로 약 22.4 GiB 를 KV 캐시 포함 정적 선점`
- **설명**: L40S 48GB의 실제 바이너리 용량은 44.70 GiB이므로, SGLang에 0.50을 지정하면 실제 선점 메모리는 $44.70 \times 0.50 = 22.35\text{ GiB}$입니다. 48 GiB를 10진 48GB로 오인해 계산한 $48 \times 0.5 = 24.0\text{ GiB}$ 표기가 주석과 가이드에 혼재되어 있습니다.

#### [사소-02] `aws-deployment.md` 내 '가중치 하한 합계' 용어 오류
- **대상 파일**: `docs/operations/aws-deployment.md:163`
- **내용**: `| 가중치 하한 합계 | 약 32.55 GiB | 44.70 GiB(L40S 실가용량) 중 약 72.8% 점유 |`
- **대조 근거 [확인]**:
  - `docs/operations/ubuntu-deployment.md:309`: `GPU 순수 가중치 합계: 19.60 + 10.18 = 29.78 GiB (텍스트 정적 선점 기준으로는 22.35 + 10.18 = 32.53 GiB)`
  - `docs/operations/eks-workload-spec.md:83-84`: `가중치: 텍스트 19.6 GiB + 이미지 10.2 GiB = 약 29.8 GiB`, `실제 선점(계산값): 텍스트 서버 22.4 GiB + 이미지 10.2 GiB = 약 32.6 GiB`
- **설명**: 순수 모델 가중치의 하한 합계는 약 29.8 GiB입니다. 32.55 GiB는 텍스트 모델의 정적 선점 풀(22.35 GiB, 가중치 + KV 캐시 포함)에 이미지 가중치(10.20 GiB)를 더한 값이므로 "가중치 하한 합계"가 아닌 "정적 선점 + 이미지 가중치 합계"로 명명하는 것이 정확합니다.

#### [사소-03] `sglang-vllm-fit.md` 내 이미지 편집 규약 필드 오기
- **대상 파일**: `docs/operations/sglang-vllm-fit.md:100`
- **내용**: `multipart: image + model + prompt + output_format=png`
- **대조 근거 [확인]**:
  - `src/local_detail_page_ai/clients.py:366-373`: `response_format: "b64_json"`을 사용하며 `output_format` 필드는 사용하지 않음.
- **설명**: OpenAI 및 SGLang 이미지 핸들러 규격은 `response_format: "b64_json"`입니다. 다만 해당 문서는 2026-09-08 당시의 MLX 검토 기록(보존용)이므로 운영상 위험은 낮습니다.

---

## 항목별 검증 요약 매트릭스

| 검증 항목 | 판정 | 주요 내용 |
|---|:---:|---|
| **1. 모델 식별자 일치** | **불일치** | `sglang-serving-research.md`의 `--revision` 누락 및 대안 모델명 표기 차이, `.env.example` 주석 불일치 발견. 그 외 8개 정본 파일 간 모델 경로/커밋/공개명은 완벽 일치. |
| **2. 포트·경로 일치** | **치명** | 포트(8000, 30000, 30001), `/var/lib/detail-page-ai`, UID/GID 10001은 전 파일 완벽 일치. 단, `aws-migration-checklist.md`의 EKS PVC "20Gi" 표기(치명) 및 헬스체크 404 경로 구식화 발견. |
| **3. 수치 모순** | **불일치** | `sglang-serving-research.md:148`의 공존 여유분 "~24 GiB" 산수 오류 발견. 테스트 통과 건수(353 vs 358) 및 0.50 선점 용량(22.35 vs 24.0 GiB) 불일치 발견. |
| **4. 미검증의 검증 단정** | **치명** | `ubuntu-deployment.md`에 GPU 미실행/Dockerfile 미빌드 면책 사실이 완전히 누락되어 검증 완료로 오인 유발. 타 3개 문서(aws-deployment, checklist, eks-workload)는 이상 없음. |
| **5. SGLang 인터페이스 오기** | **사소** | `python3 -m sglang.launch_server`(text), `sglang serve`(image), 확산 서버 `/health` 부재 및 `/v1/models` 사용, 생성 JSON, 편집 multipart(`image`) 전반적으로 정확히 반영됨. `sglang-vllm-fit.md`의 사소한 필드명 오기 1건 발견. |
| **6. 문서 간 충돌** | **치명** | EKS(단일 컨테이너/파드) vs EC2(3 컨테이너 Compose) 구조 차이는 정당한 대상 분리(이상 없음). 단, EKS PVC 용량(20Gi vs 100Gi)과 헬스체크(404 vs 200)는 문서 간 모순. |
| **7. Mac 로컬 vs 서버 MLX 혼재** | **이상 없음** | `local-llm.md` 등 Mac 로컬 전용 문서와 서버 배포 문서가 명확히 분리되어 있으며, 서버 문서 내에 로컬 MLX 설정이 잘못 섞여 들어간 곳 없음. |
