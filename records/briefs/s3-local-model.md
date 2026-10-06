# 수정 — 모델을 로컬 경로(S3 사전 업로드분)에서 읽을 수 있게

## 배경
인프라팀이 모델을 **S3 에 미리 올려두고 GPU Pod 가 S3 Gateway Endpoint 로 받는** 방식을 제안했습니다(`jangin-{env}-s3-models`, NAT 미경유·무료·빠름). 관리자가 **(가)안**으로 확정했습니다.

- **인프라팀**이 S3 → PVC 동기화를 담당합니다 (initContainer 또는 Job 의 `aws s3 sync`)
- **우리 컨테이너는 로컬 디렉터리만 읽습니다.** AWS CLI·boto3·IAM 권한 **모두 불필요**합니다

지금은 `TEXT_MODEL_PATH=cyankiwi/Qwen3.8-27B-AWQ-INT4` 처럼 **Hugging Face 저장소 ID** 를 넣고 `--revision <커밋SHA>` 로 버전을 고정합니다. 로컬 디렉터리를 넣으면 **`--revision` 이 무의미하거나 실패**합니다.

## 담당 파일
- `deploy/sglang/entrypoint.sh`
- `deploy/sglang/Dockerfile` (ENV 주석·기본값)
- `.env.example`
- `tests/` (새 테스트)

문서(`docs/`)는 다른 워커가 동시에 고치니 열지 마세요.

## 바꿀 것

### 1. 모델 경로가 로컬 디렉터리면 `--revision` 을 빼고 오프라인으로 동작
`entrypoint.sh` 의 두 서버 기동부(35-45행 텍스트, 47-56행 이미지)에서:

- `$TEXT_MODEL_PATH` (그리고 `$IMAGE_MODEL_PATH`) 가 **디렉터리로 존재하면** → **로컬 모드**
  - `--revision` 을 **전달하지 않는다**
  - `HF_HUB_OFFLINE=1` 을 설정해 **네트워크를 아예 시도하지 않게** 한다 (S3 방식의 목적이 NAT 미경유이므로 중요)
- 그렇지 않으면 → **HF 모드** (지금과 동일하게 `--revision` 전달)

두 서버가 각각 독립적으로 판정해야 합니다. 텍스트는 로컬, 이미지는 HF 인 구성도 가능해야 합니다.

### 2. 로컬 모드인데 모델이 없으면 즉시 명확히 실패
로컬 모드로 판정됐는데 해당 디렉터리에 `config.json` 이 없으면 **기동을 중단하고 사람이 읽을 수 있는 메시지**를 남기세요. 예:

```
ERROR: TEXT_MODEL_PATH=/var/lib/detail-page-ai/models/qwen 는 디렉터리지만 config.json 이 없습니다.
       S3 동기화가 끝나기 전에 파드가 뜬 것일 수 있습니다.
```

SGLang 이 수십 초 뒤에 내는 모호한 오류보다 낫습니다.

### 3. 검증 가능하게 만들기 — `DRY_RUN`
`entrypoint.sh` 에 `DRY_RUN=1` 을 지원하세요. 설정되면 **서버를 실행하지 않고 조립된 명령줄을 표준 출력에 한 줄씩 출력하고 종료**합니다. 그래야 테스트가 플래그 조합을 확인할 수 있습니다.

### 4. `.env.example` · Dockerfile ENV
두 방식을 **모두** 쓸 수 있음을 주석으로 남기세요.
- 기본값은 지금처럼 HF 저장소 ID 를 유지합니다 (단일 EC2 compose 구성이 이 경로를 씁니다)
- EKS 에서는 인프라가 PVC 에 넣어준 디렉터리 경로를 주입한다고 적으세요. 예: `/var/lib/detail-page-ai/models/qwen3.8-27b-awq`
- **기존 커밋 SHA 값은 지우지 마세요.** HF 모드에서 여전히 필요합니다.

## 테스트 (`tests/` 에 추가)
`DRY_RUN=1` 로 `bash deploy/sglang/entrypoint.sh` 를 실행해 확인합니다.
1. 모델 경로가 HF ID → 출력에 `--revision <SHA>` 가 **있다**
2. 모델 경로가 `config.json` 있는 임시 디렉터리 → `--revision` 이 **없고** `HF_HUB_OFFLINE=1` 이 설정된다
3. 텍스트만 로컬·이미지는 HF → 각각 다르게 조립된다
4. 로컬 경로인데 `config.json` 이 없으면 **0 이 아닌 종료 코드**와 오류 메시지

기존 테스트를 고치거나 지우지 마세요.

## 지켜야 할 것
- `--mem-fraction-static`, `--context-length`, `--dit-cpu-offload false`, `--text-encoder-cpu-offload false`, `--num-gpus 1`, 포트 30000·30001, `--served-model-name` 은 **그대로**
- FastAPI 를 PID 1 로 실행하고 자식이 죽으면 종료하는 현재 동작 유지
- AWS CLI·boto3 를 **추가하지 마세요.** 이 방식의 핵심은 우리 컨테이너에 AWS 자격이 들어가지 않는 것입니다

## 검증
`.venv/bin/python -m pytest -q` → **369 + 추가분**. 줄어들면 회귀입니다.
`bash -n deploy/sglang/entrypoint.sh` 문법 검사 통과.

## 보고
`## 결과` 에 바꾼 행, 추가 테스트, 두 모드의 조립 결과 예시를 적고, 마지막 줄에 `완료: 테스트 N passed` 출력.
