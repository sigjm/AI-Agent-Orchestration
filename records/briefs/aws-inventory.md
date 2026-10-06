# 작업 — AWS 에 올릴 것 목록 만들기

## 관리자 지시
"AWS 서버에 올릴것들 정리해놔"

배포 때 **무엇을 어디에 올려야 하는지** 한 장으로 보이는 목록을 만듭니다.

## 만들 파일 (이 하나만)
`docs/operations/aws-deploy-inventory.md`

**다른 파일은 절대 열지 마세요.** 지금 다른 워커 둘이 `deploy/`·`.env.example`·`tests/` 와 `docs/operations/eks-workload-spec.md`·`aws-migration-checklist.md` 를 동시에 고치고 있습니다. 읽기만 하고 수정하지 마세요.

## 확정 사양 (이대로 쓰세요)

### 모델 확보 방식 — S3 사전 업로드로 확정됨
- **인프라팀**이 S3(`jangin-{env}-s3-models`) → PVC 동기화를 담당 (initContainer 또는 Job 의 `aws s3 sync`, S3 Gateway Endpoint 경유라 NAT 미경유)
- **우리 컨테이너는 PVC 의 로컬 디렉터리만 읽습니다.** AWS CLI·boto3·IAM 권한 **불필요**
- 로컬 경로 모드에서는 `--revision` 이 적용되지 않으므로 **어느 커밋의 가중치인지는 S3 쪽에서 관리**해야 함

### 올릴 모델 2개
| 모델 | 저장소 | 커밋 | 크기 |
| --- | --- | --- | --- |
| 텍스트·비전 | `cyankiwi/Qwen3.8-27B-AWQ-INT4` | `6e134bae811fb5adac50ee042ae5f029ac6779aa` | 가중치 19.6 GiB |
| 이미지 확산 | `circulus/FLUX.2-klein-9B-bnb-4bit` | `58c2804f31af12c8888504b96250010c50b55e44` | 약 10.2 GiB |

`config.json` 과 `*.safetensors` 가 든 **디렉터리 형태**여야 하고 모델마다 별도 디렉터리여야 합니다.

## 문서 구성
표 중심으로 짧게. 설명을 길게 쓰지 말고 **무엇을·어디에·누가** 가 보이게.

1. **컨테이너 이미지** — `deploy/sglang/Dockerfile` 로 빌드해 ECR 에. 빌드 컨텍스트는 `page_generation/` 디렉터리. 단일 컨테이너에 FastAPI(:8000) + SGLang 텍스트(30000) + 이미지(30001)
2. **모델** — 위 표, S3 로
3. **영구 볼륨** — PVC 1개 `gp3`/`ReadWriteOnce`/100Gi, 마운트 `/var/lib/detail-page-ai`, `fsGroup: 10001`. 하위 경로 구조(state.sqlite3, assets, models, cache)
4. **시크릿** — 이름만. `BACKEND_AUTH_TOKEN`, `AI_INTERNAL_AUTH_TOKEN`. **`HF_TOKEN` 은 S3 방식에서는 불필요**하다는 점을 명시
5. **설정값(ConfigMap)** — `TEXT_MODEL_PATH`·`IMAGE_MODEL_PATH`(PVC 안 절대 경로), `BACKEND_URL`, 서빙 모델명, provider 값 등
6. **워크로드 자원** — `nvidia.com/gpu: 1`(L40S 48GB), CPU/메모리 요청·상한. **미검증 추정치임을 표시**
7. **프로브** — `/health`(liveness, 무인증 200), `/health/ready`(readiness, 200/503)
8. **네트워크** — BE 내부 주소(우리가 콜백할 곳), S3 Gateway Endpoint, 컨테이너 내부 30000·30001 은 노출 불필요
9. **이미지 발행** — `Jangingmall/GenAI` `main` push, `page_generation/**` 경로 트리거

각 항목에 **담당(우리 / 인프라팀 / BE팀)** 과 **상태(준비됨 / 회신 대기 / 미검증)** 열을 넣으세요.

## 반드시 지킬 것
- **서버 GPU 에서는 아직 한 번도 실행되지 않았습니다.** 맨 앞에 명시하세요.
- `deploy/sglang/Dockerfile`(SGLang+CUDA)은 **아직 빌드된 적이 없습니다.** 서비스 이미지(`deploy/Dockerfile`)만 2026-09-17 에 Linux 에서 빌드·기동을 확인했습니다. 이 둘을 섞지 마세요.
- 측정하지 않은 수치를 단정하지 마세요. CPU·메모리 권장값은 추정치입니다.
- 없는 사실을 만들지 마세요. 확실하지 않으면 "확인 필요" 로 두세요.
- 기존 문서와 **충돌하는 내용을 쓰지 마세요.** 쓰기 전에 `docs/operations/eks-workload-spec.md` 를 읽고 수치를 맞추세요(읽기만).

## 검증
- 인용한 경로·파일이 실제로 있는지 확인
- `.venv/bin/python -m pytest -q` → 369 이상

## 보고
`## 결과` 에 항목 수와 "회신 대기" 로 남긴 것 목록을 적고, 마지막 줄에 `완료: docs/operations/aws-deploy-inventory.md, N줄` 출력.
