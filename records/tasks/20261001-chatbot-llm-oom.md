# 챗봇 LLM 사이드카 OOMKill · 첫 요청 타임아웃 — 원인 확인과 수정안

챗봇 담당에게 전달할 **수정안**을 만든다. 코드나 설정을 실제로 바꾸지 않는다. 결과는 이 파일 하단 `## 결과`에 쓴다.

## 상황 (Stage, 2026-10-01, 관리자가 Loki·kubectl로 수집)

- Pod `ai-ollama-6bdc55f77-jdtlm` (네임스페이스 `ai`, T4 노드). 컨테이너 2개
  - `ai-ollama` (챗봇 API, FastAPI) — limit 2Gi, 최근 30분 최대 1.81 GiB
  - `chatbot-llm` (Ollama, `gemma4:12b`) — limit 10Gi, GPU 1
- 시간순 (KST)
  - 12:55 컨테이너 시작. 모델은 첫 채팅 요청(14:13:49)이 올 때까지 올라가지 않았다. 적재 약 83초
  - 14:10까지 메모리(working set) 0.4 GiB → 14:15 1.9 → 14:20 6.8 → 14:25 7.0 GiB
  - **14:25:48 `chatbot-llm` OOMKilled (exit 137)** → 재시작
  - 14:48:24 재시작 뒤 첫 채팅 → 모델 다시 적재(14:50:36 완료) → Ollama `/api/chat` **3m0s 만에 500**, 챗봇 API 읽기 타임아웃 180초 초과(`ReadTimeoutError`), `/ai/chat`은 200(대체 응답 추정)
- 로그에서 본 것
  - llama-server 명령: `-c 16384 -np 1 ... --spec-type draft-mtp ... --load-mode none --flash-attn auto -b 1024 -ub 1024 --context-shift --keep 4`
  - `prompt cache is enabled, size limit: 8192 MiB` / `use --cache-ram 0 to disable the prompt cache`
  - `cache state: 1 prompts, 2960.002 MiB (limits: 8192.000 MiB ...)` 등, `prompt_save ... total state size = ~400 MiB` 18회
  - `created context checkpoint N of 32 (... size = 320.013 MiB)` 46회 (gemma SWA, `n_swa = 1024`)
  - `disabling mmap for llama-server load due to host memory pressure ... system_total="10.0 GiB"`
  - Ollama 설정: `OLLAMA_KEEP_ALIVE` 무기한(-1), `OLLAMA_NUM_PARALLEL:1`, `OLLAMA_CONTEXT_LENGTH:0`
- 준비 확인: `chatbot-llm` readinessProbe 가 `/api/tags` — 모델이 안 올라가 있어도 200

## 자료 (읽기 전용 — 수정 금지)

- 로그·매니페스트: `<scratchpad>/chatbot-handoff/`
  - `chatbot-llm-previous.log` (OOMKill 된 컨테이너), `chatbot-llm-current.log`, `ai-ollama-api.log`, `pod.json`, `ollama-deployment.yaml`(infra `k8s/base/ai`)
- 챗봇 코드 (GenAI `main` 사본): `<scratchpad>/GenAI-0929/chat_bot/`
  - 특히 `deploy/ollama/Dockerfile`, `app/pipeline/llm.py`(타임아웃·keep_alive), `app/main.py`(lifespan warmup), `app/readiness.py`

## 할 일

1. **원인 확인**: 위 가설(① 프롬프트 캐시 + 컨텍스트 체크포인트가 호스트 RAM을 키워 10Gi 초과, ② 사이드카 재시작 후 모델이 안 올라가 첫 요청이 적재+추론으로 180초 초과, ③ readiness 가 모델 적재를 보지 않음)이 로그와 코드로 맞는지. 다른 원인이 보이면 그것도
2. **수정안** — 각각 근거(로그 줄, 코드 위치, Ollama·llama.cpp 문서나 소스)와 함께
   - 프롬프트 캐시·체크포인트 메모리 상한: Ollama가 띄우는 llama-server 에 `--cache-ram`, `--ctx-checkpoints` 같은 값을 **실제로 넘길 수 있는 방법**이 있는지 (예: `LLAMA_ARG_*` 환경 변수가 자식 llama-server 까지 전달되는지, Ollama 설정·Modelfile 파라미터). 이미지의 Ollama 버전 기준으로 확인하고, 확인 못 하면 못 했다고 쓴다
   - 모델 사전 적재: `chatbot-llm` 이 뜰 때 모델을 올려 두는 방법 (진입점 스크립트, postStart 등)과 준비 확인을 모델 적재 기준으로 바꾸는 방법 (`/api/ps` 등)
   - 챗봇 API 타임아웃(180초)·재시도 정책을 바꿀 필요가 있는지
   - 메모리 limit 조정이 필요한지 (T4 노드 메모리 한계도 고려), `ai-ollama` 2Gi 여유
   - 각 수정안의 **파일·변경 내용(diff 수준)**, 담당(챗봇 코드 / 인프라 매니페스트), 위험, 검증 방법
3. 우선순위 1~3개를 추천

## 하지 말 것

- 어떤 저장소·파일도 수정하지 않는다 (이 파일의 `## 결과` 작성만). **git 상태 변경 금지**
- Stage 클러스터에 아무 명령도 실행하지 않는다
- 로그에서 사용자 대화 내용을 옮겨 적지 않는다 (토큰 수·시간·오류만)

## 결과

### 조사 범위와 결론

2026-10-01. 제공된 로그·Pod 정보·GenAI `main` 사본과 Ollama **v0.35.0**, 그 버전이 사용하는 llama.cpp **b11081** 소스를 읽어 수정안을 작성했다. 아래 diff는 담당자에게 전달할 **제안**이며 적용하지 않았다. Stage 명령, 컨테이너 실행·재시작, 모델 요청, 코드·설정 변경, git 변경 작업은 수행하지 않았다. 사용자 대화는 보고에 옮기지 않았다.

우선순위는 **① RAM 캐시·체크포인트 제한과 이미지 버전 고정 → ② 사이드카 자체 사전 적재와 준비 확인 교체 → ③ 재시도 교정 및 실측 기반 자원 조정**이다. ①·②는 함께 배포하는 것을 권한다. 캐시를 줄이면 프롬프트 재계산 시간이 늘 수 있으므로 메모리와 응답 시간을 함께 검증해야 한다.

자료 경로 표기:

- `L/` = `<scratchpad>/chatbot-handoff/`
- `C/` = `<scratchpad>/GenAI-0929/chat_bot/`
- 아래 로컬 줄 번호는 이 사본 기준이다. 변경 대상은 GenAI의 `chat_bot/...`와 인프라의 `k8s/base/ai/ollama-deployment.yaml` 및 실제 Stage 이미지 참조 overlay이다.

### 1. 원인 확인

| 항목 | 판정 | 직접 확인한 근거와 한계 |
|---|---|---|
| 호스트 메모리 OOM | **확정** | `L/pod.json`의 `chatbot-llm.lastState.terminated`: `OOMKilled`, exit 137, 종료 `2026-10-01T05:25:48Z` = 14:25:48 KST. limit 10Gi, 재시작 1회. API 컨테이너는 재시작 0회. |
| RAM 캐시·체크포인트가 메모리 증가에 기여 | **강한 근거가 있음. 정확한 OOM 순간의 메모리 합계는 미확정** | previous 로그 1439줄: RAM 캐시 상한 8192MiB, 1442줄: 슬롯별 체크포인트 최대 32개. 2247줄의 캐시 약 2961.253MiB, 2448줄의 체크포인트 `9 of 32`, 개당 320.013MiB. 마지막 2467줄도 약 398MiB 상태 저장 중이다. 저장 시 현재 체크포인트를 캐시로 복사하는 소스가 확인된다. 다만 `memory.current/peak/events`, RSS·file cache 분해와 커널 OOM 기록이 없으므로 이 로그만으로 순간 10Gi 초과의 배분을 확정할 수 없다. |
| 재시작 후 첫 요청이 적재 비용을 부담 | **확정** | current 로그 282줄 적재 시작, 803줄 적재 완료까지 **131.15초**. 822줄 첫 요청 프롬프트 **6192토큰**, 832–837줄에서 3072토큰까지 처리하다 839줄 `/api/chat` 500, 소요 **3m0s**, 840줄 작업 취소. 적재만으로 180초 중 약 131초를 소비했다. |
| 500의 직접 원인이 Ollama 자체 180초 제한 | **그렇게 단정할 수 없음** | API 로그 1622·1636·1667줄에 read timeout 180초 및 이를 감싼 `ConnectionError`가 있고, Ollama 작업 취소 시점과 일치한다. 클라이언트 제한에 따른 취소로 설명되지만 서버 500 응답 본문·요청 ID가 없어 독립적인 서버 오류까지 배제하지는 못한다. |
| 준비 확인이 적재 여부를 보지 않음 | **확정, 두 컨테이너 모두 해당** | `L/ollama-deployment.yaml:121–134`의 sidecar startup/readiness는 `/api/tags`. `C/app/readiness.py:66–86`도 `/api/tags`에 모델명이 있는지만 확인한다. current 로그에서 적재 전·중에도 tags는 200이었다. |
| API 예열이 재시작 후 자동 재실행 | **실행되지 않음** | `C/app/main.py:90–101`은 API lifespan에서 한 번만 예열하고 실패를 잡아 계속 시작한다. API 로그 3·12·55·60–73줄에서 첫 예열이 `/api/show` 연결 거절로 실패했다. API 시작 03:53:40Z, 이전 LLM 시작 03:55:56Z여서 시작 순서 경쟁도 확인된다. LLM만 재시작했으므로 API lifespan은 다시 실행되지 않았다. |
| `/ai/chat` 200이 추론 성공을 의미 | **아님** | API 로그 1668줄은 timeout 예외 직후 POST 200. `C/app/main.py:247–282`는 해당 예외를 잡아 `ChatResponse` 대체 응답을 기본 200으로 반환한다. 반환 본문 원문은 조사 결과에 복사하지 않았다. |

**메모리 수치 해석에서 바로잡을 점**

- 체크포인트 **46회는 누적 생성 이벤트**다. 46개가 동시에 살아 있었다는 뜻이 아니다. 제공 로그에서 확인한 최대 번호는 9이며, 설정의 32개가 모두 할당되었다고도 말할 수 없다. 최대 설정만 계산하면 32 × 320.013MiB ≈ **10GiB/슬롯**으로, 컨테이너 전체 limit와 맞먹는 위험한 설정이다.
- `cache state`의 용량에는 **저장된 체크포인트가 이미 포함**된다. 캐시 약 3GiB에 모든 체크포인트 이벤트를 더하면 중복 계산이다. 다만 **활성 슬롯의 체크포인트와 캐시에 복사된 체크포인트는 함께 존재할 수 있다**. b11081 `server-task.cpp:1722–1783`은 저장 상태 크기에 체크포인트를 합산하고, 새 캐시 항목에 이를 복사한다. 캐시 상한은 캐시 항목들을 제한할 뿐 활성 체크포인트·모델·임시 버퍼를 포함한 전체 RSS 상한이 아니다. [상태 저장 소스](https://github.com/ggml-org/llama.cpp/blob/b11081/tools/server/server-task.cpp#L1722), [캐시 크기 계산](https://github.com/ggml-org/llama.cpp/blob/b11081/tools/server/server-task.h#L597)
- GPU에 모델 49/49 레이어를 올린 로그가 있고(previous 1125–1128줄), CUDA_Host 모델 버퍼 약 **787.50MiB**, draft 모델 호스트 버퍼 약 **272MiB**도 있다(1319–1320줄). GPU 적재 상태에서도 호스트 RAM 사용이 사라지지 않는다. 제공 로그에는 CUDA OOM 오류가 없다. 이번 종료 원인은 Pod에 기록된 메모리 OOM이며, GPU OOM으로 분류할 근거는 없다.
- previous 949줄에서 mmap을 끈 것은 이미 감지한 호스트 메모리 압력에 대한 Ollama의 선택이다. 로그의 `system_total=10GiB`를 **노드 물리 RAM**으로 해석할 수 없다. working set 샘플 최고 7GiB도 짧은 할당 피크와 cgroup에 청구되는 전체 메모리를 보여 주지 않으므로 OOM 기록과 모순되지 않는다.
- CPU limit 2개, draft/MTP·멀티모달 초기화 및 긴 프롬프트 처리는 적재·추론 비용 요인이다. 그러나 CPU throttling 수치가 없으므로 CPU 제한을 이번 지연의 확정 원인으로 지목하지 않는다.

주요 로컬 근거: [이전 LLM 로그](<scratchpad>/chatbot-handoff/chatbot-llm-previous.log:1439), [재시작 후 LLM 로그](<scratchpad>/chatbot-handoff/chatbot-llm-current.log:803), [API 오류](<scratchpad>/chatbot-handoff/ai-ollama-api.log:1622), [Pod 종료 정보](<scratchpad>/chatbot-handoff/pod.json).

### 2. 우선순위 1 — RAM 캐시·체크포인트 제한, 실행 버전 고정

#### 2.1 환경 변수 전달 경로 확인

실제 두 LLM 로그 5줄 모두 Ollama **0.35.0**을 기록한다. Dockerfile 27줄의 `latest`를 보고 현재 최신 버전을 추정하지 않았다. 조사한 v0.35.0 태그의 commit은 `cc4069396f3ad2c370c53eed2e4a42ac13adab84`, `LLAMA_CPP_VERSION`은 **b11081**이다. [버전 파일](https://github.com/ollama/ollama/blob/v0.35.0/LLAMA_CPP_VERSION), [빌드 시 버전 참조](https://github.com/ollama/ollama/blob/v0.35.0/llama/server/CMakeLists.txt#L114)

소스 기준으로 다음 경로가 확인된다.

1. Ollama `llm/llama_server.go:434`가 자식 서버 실행 전 환경 설정 함수를 호출한다.
2. 같은 파일 448–478줄은 부모 환경 전체를 `os.Environ()`으로 가져오고 라이브러리 경로 등 필요한 항목만 갱신한다. `LLAMA_ARG_*`를 제거하는 allowlist 방식이 아니다.
3. llama.cpp b11081 `common/arg.cpp:781–806`은 환경 변수를 먼저 읽고 이후 CLI 인수를 읽는다.
4. 1695–1701줄은 `LLAMA_ARG_CTX_CHECKPOINTS`를 슬롯별 체크포인트 수에, 1713–1719줄은 `LLAMA_ARG_CACHE_RAM`을 캐시 **MiB** 상한에 연결한다. RAM 캐시 0은 비활성화이며, checkpoint 0도 `server-context.cpp:1365–1369`에서 비활성화된다.
5. 현재 Ollama의 서버 인수 생성 코드와 실제 명령에는 이 두 값을 덮어쓰는 CLI 옵션이 없다. 따라서 **sidecar 컨테이너 env → Ollama 부모 환경 → llama-server 환경 → 옵션 파서**로 전달할 수 있다. 실행 명령 문자열에 옵션이 추가되지 않아도 적용될 수 있다. [Ollama 자식 환경](https://github.com/ollama/ollama/blob/v0.35.0/llm/llama_server.go#L434), [llama.cpp 환경 파싱](https://github.com/ggml-org/llama.cpp/blob/b11081/common/arg.cpp#L781), [캐시·체크포인트 옵션](https://github.com/ggml-org/llama.cpp/blob/b11081/common/arg.cpp#L1695), [0일 때 비활성화](https://github.com/ggml-org/llama.cpp/blob/b11081/tools/server/server-context.cpp#L1351)

**확인 한계:** 제공된 ECR 이미지 자체를 실행하거나 바이너리 help·자식 `/proc/.../environ`을 확인하지는 않았다. Pod의 현재 sidecar image digest는 `sha256:75fae7b45a7872b1d798fef6c2e74855601cdc181bd9d2b9ac705d1579ae00b2`다. 위 전달 방법은 **로그와 일치하는 공개 버전 소스에서 확인**했으며, 사설 이미지가 해당 소스를 그대로 포함하는지와 변경 env의 실제 적용은 담당자의 이미지 검증 단계에 남는다.

Ollama v0.35.0의 API Runner 옵션에는 `cache_ram`, `ctx_checkpoints`가 없다. 이를 임의의 `options` JSON 또는 Modelfile `PARAMETER`로 넣는 안은 채택하지 않는다. `OLLAMA_KV_CACHE_TYPE`은 별도의 KV 표현 설정이다. [지원 Runner 옵션](https://github.com/ollama/ollama/blob/v0.35.0/api/types.go#L588)

#### 2.2 제안 diff

**인프라 담당 — `k8s/base/ai/ollama-deployment.yaml`, `chatbot-llm`에 추가:**

```diff
         - name: chatbot-llm
+          env:
+            - name: LLAMA_ARG_CACHE_RAM
+              value: "0"
+            - name: LLAMA_ARG_CTX_CHECKPOINTS
+              value: "0"
+            - name: OLLAMA_CONTEXT_LENGTH
+              value: "16384"
+            - name: OLLAMA_NUM_PARALLEL
+              value: "1"
```

초기 안정화안은 **두 저장 기능 모두 끄고 10Gi limit를 유지**한다. 단순히 캐시만 끄면 활성 슬롯의 체크포인트 RAM은 남는다. 반대로 체크포인트만 줄이면 약 8GiB 캐시 상한이 남는다. `num_ctx`는 API에서 이미 16384를 명시하므로 이 env만으로 API 컨텍스트가 줄어들지는 않는다. CLI도 실제 `-c 16384 -np 1`이었다.

**챗봇 담당 — `chat_bot/deploy/ollama/Dockerfile`:**

```diff
-FROM ollama/ollama:latest
+FROM ollama/ollama:0.35.0
```

재빌드할 때 검증한 베이스 이미지 digest까지 고정하고, 인프라 Stage overlay의 ECR 참조도 새 빌드의 immutable digest로 교체한다. 확인하지 않은 digest를 임의로 제안하지 않는다. 버전을 바꾸면 RAM 캐시 환경 변수와 파서의 지원 여부부터 다시 확인한다.

**위험·후속 조정:** SWA 체크포인트와 RAM 프롬프트 재사용이 줄어들어 intent/응답 생성 사이 전환 및 긴 대화에서 prefill 시간이 늘 수 있다. 기능·지연 검증 후 재사용이 꼭 필요하면 **`LLAMA_ARG_CACHE_RAM=1024`, `LLAMA_ARG_CTX_CHECKPOINTS=1`**을 별도 비교 후보로 삼는다. 이는 약 1GiB 저장 캐시와 활성 슬롯의 체크포인트 최대 1개를 허용하는 설정이며 전체 프로세스 메모리 상한을 보장하지 않는다. `-np 1` 유지도 전제다. 처음부터 8192/32로 되돌리는 것은 권하지 않는다.

**컨텍스트 축소는 후순위:** `C/app/pipeline/llm.py:94–113`에는 과거 8192컨텍스트에서 입력 8044 + 출력 148토큰으로 JSON이 잘린 근거가 있다. 프롬프트·이력·후보와 출력 토큰 예산을 먼저 정하고 회귀 검증하기 전에는 8192로 낮추지 않는다. 요청의 명시적 옵션이 모델 기본값보다 뒤에 적용되며, Ollama는 `NumCtx × NumParallel`로 서버 `-c`를 구성한다. [옵션 우선순위](https://github.com/ollama/ollama/blob/v0.35.0/server/routes.go#L127), [서버 컨텍스트 인수](https://github.com/ollama/ollama/blob/v0.35.0/llm/llama_server.go#L378)

**검증 — 챗봇·인프라 공동, 후속 적용 시:** 해당 빌드 바이너리의 버전·옵션 지원을 확인하고 새 서버 로그에 RAM 캐시 비활성화 및 체크포인트 비활성화가 모두 표시되는지 확인한다. bounded 후보를 사용하면 1024MiB/최대 1개가 표시되어야 한다. 환경 변수 선언이나 명령 문자열만으로 적용 성공을 판정하지 않는다. 여러 합성 세션에서 intent/생성 프롬프트를 반복 전환하고 긴 이력을 포함해 JSON 완결성·문맥 보존·prefill 시간·메모리 피크를 비교한다.

### 3. 우선순위 2 — 시작 시 적재, 적재·예열 기준 준비 확인

#### 3.1 사이드카가 사전 적재를 소유해야 하는 이유

현재 `C/deploy/ollama/Dockerfile:36–39`는 **빌드 중 모델을 pull**하고 서버를 종료한다. 런타임의 `ENTRYPOINT ["ollama", "serve"]`는 모델 파일을 보유할 뿐 자동으로 모델을 올리지 않는다. API의 1회 예열에만 의존하면 지금처럼 시작 순서 경쟁·LLM 단독 재시작을 처리하지 못한다.

Ollama는 모델과 빈 입력을 담은 `/api/generate` 또는 `/api/chat` 요청으로 사전 적재할 수 있다. 요청 `keep_alive=-1`은 적재 유지에 사용한다. `/api/ps`에는 실행 모델의 이름·digest·context_length·size_vram이 제공된다. [사전 적재·keep_alive 문서](https://docs.ollama.com/faq), [실행 모델 API](https://docs.ollama.com/api/ps), [v0.35.0 PsHandler](https://github.com/ollama/ollama/blob/v0.35.0/server/routes.go#L2422)

**`/api/ps` HTTP 200만 검사해서는 안 된다.** 빈 models 배열도 200이다. 또한 v0.35.0 `server/sched.go:721–750,1760–1799`는 적재 중 runner 잠금 때문에 조회가 기다릴 수 있다. 짧은 timeout을 둔 probe는 이 경우 준비 실패로 처리해야 한다. 빈 입력 적재 성공과 1토큰 smoke 성공 표시를 함께 사용한다. [스케줄러의 적재와 상태 조회](https://github.com/ollama/ollama/blob/v0.35.0/server/sched.go#L721)

#### 3.2 제안 diff — 이미지와 스크립트

**챗봇 담당 — `chat_bot/deploy/ollama/Dockerfile`:**

```diff
+RUN apt-get update && apt-get install -y --no-install-recommends curl jq \
+    && rm -rf /var/lib/apt/lists/*
+COPY deploy/ollama/start-and-preload.sh /usr/local/bin/start-and-preload
+COPY deploy/ollama/ready.sh /usr/local/bin/ollama-ready
+RUN chmod 755 /usr/local/bin/start-and-preload /usr/local/bin/ollama-ready
-HEALTHCHECK --interval=30s --timeout=5s --start-period=120s --retries=3 \
-    CMD ["sh", "-c", "ollama list | grep -q \"$OLLAMA_MODEL\" || exit 1"]
+HEALTHCHECK --interval=30s --timeout=5s --start-period=600s --retries=3 \
+    CMD ["/usr/local/bin/ollama-ready"]
-ENTRYPOINT ["ollama", "serve"]
+ENTRYPOINT ["/usr/local/bin/start-and-preload"]
```

위 COPY는 현재 이미지 빌드 컨텍스트가 `chat_bot/`라는 전제이며, 담당자는 실제 CI build context에 맞춰 경로를 확정한다. 베이스 이미지 패키지 관리자와 curl/jq 설치도 빌드에서 검증한다. Docker HEALTHCHECK는 Kubernetes probe를 대신하지 않으므로 아래 매니페스트 변경도 필요하다.

**새 `chat_bot/deploy/ollama/start-and-preload.sh`의 구현 내용:**

1. 이전 완료 표시 `/tmp/chatbot-llm-preloaded`를 삭제한다. emptyDir는 컨테이너 재시작에도 남으므로 삭제가 필수다.
2. `ollama serve &`를 실행하고 PID를 저장한다. PID 1 스크립트에 EXIT/TERM/INT cleanup을 두어 완료 표시를 지우고 서버에 TERM을 전달한 뒤 wait한다. 서버가 죽으면 스크립트도 실패 종료하도록 감독한다.
3. 최대 60초 동안 로컬 `/api/tags` 연결을 확인한다(요청당 connect 1초/read 포함 총 2초). 대기 중 PID 종료도 확인한다. 여기서 tags는 **연결 준비 확인**으로만 사용한다.
4. 아래 JSON을 `/api/generate`에 **한 번** 보낸다. `curl --fail --connect-timeout 2 --max-time 300`으로 제한하고 HTTP 성공 및 JSON `done=true`를 모두 검사한다. 모델명은 `$OLLAMA_MODEL`, 컨텍스트는 `$OLLAMA_CONTEXT_LENGTH`로 안전하게 `jq --arg/--argjson`을 사용해 생성한다.

```json
{"model":"gemma4:12b","stream":false,"keep_alive":-1,"options":{"num_ctx":16384}}
```

5. 같은 모델·num_ctx로 합성된 아주 짧은 입력, `num_predict=1`, `think=false`의 실제 생성 smoke를 최대 180초로 한 번 실행한다. 현재 대상 gemma4에 대한 thinking capability를 확인해 `think`를 넣고, 지원하지 않는 모델로 변경하면 이 필드를 생략한다. HTTP 성공·`done=true`를 검사한다. 1토큰 출력은 준비 시험용이며 제품 JSON 품질 시험은 별도다.
6. 성공 시에만 완료 표시를 만들고 `wait "$server_pid"`로 계속 감독한다. 연결 대기·적재·smoke를 합해 약 540초로 제한한다. 실패하면 서버를 정리하고 nonzero로 종료해 컨테이너 재시작 정책을 적용한다. full preload/생성을 무제한 재시도하지 않는다.

빈 적재만으로 **6192토큰 프롬프트의 prefill 비용까지 제거되지는 않는다**. smoke와 API 업무 예열은 이 차이를 관찰하기 위한 것이며, RAM 캐시를 끈 상태에서 모든 시스템 프롬프트가 계속 캐시된다고 보장하지 않는다. 사전 적재·업무 요청의 `num_ctx` 등 runner 옵션은 일치시켜 불필요한 재적재를 막는다.

**새 `chat_bot/deploy/ollama/ready.sh` 제안:**

```sh
#!/bin/sh
set -eu
test -f /tmp/chatbot-llm-preloaded
curl --fail --silent --show-error --connect-timeout 1 --max-time 2 \
  http://127.0.0.1:11434/api/ps |
  jq -e --arg model "$OLLAMA_MODEL" \
    --argjson ctx "${OLLAMA_CONTEXT_LENGTH:-16384}" \
    'any(.models[]?; ((.name // .model) == $model) and (.context_length == $ctx))' \
  >/dev/null
```

이 예시는 현재 정확한 모델명 `gemma4:12b` 기준이다. 별칭·registry 접두사를 쓰는 배포라면 정상화된 이름 또는 기대 digest로 식별한다. `/api/ps`가 잘못된 JSON·빈 목록·timeout을 반환하면 실패해야 한다. 완료 파일만으로 준비를 통과시키지 않는다. 실제 GPU offload 여부는 size_vram과 시작 로그로 별도 검증한다.

#### 3.3 제안 diff — Kubernetes와 API

**인프라 담당 — `k8s/base/ai/ollama-deployment.yaml`, 두 probe를 변경:**

```diff
           startupProbe:
-            httpGet:
-              path: /api/tags
-              port: ollama
+            exec:
+              command: ["/usr/local/bin/ollama-ready"]
             periodSeconds: 10
             timeoutSeconds: 5
             failureThreshold: 120
           readinessProbe:
-            httpGet:
-              path: /api/tags
-              port: ollama
+            exec:
+              command: ["/usr/local/bin/ollama-ready"]
             periodSeconds: 10
             timeoutSeconds: 5
             failureThreshold: 3
```

기존 startup 허용 약 1200초는 우선 유지한다. 스크립트 최대 약 540초가 그 안에 들어간다. sidecar는 readOnlyRootFilesystem이지만 `/tmp`가 쓰기 가능한 emptyDir로 마운트되어 있다(매니페스트 113–115·144–155줄). 적재 실패를 liveness가 계속 재시작시키는 구성을 추가하지 않는다. 준비 실패는 트래픽에서 제외하고, 시작 실패는 startup/진입점에서 처리한다. [Kubernetes probe 동작](https://kubernetes.io/docs/concepts/workloads/pods/probes/)

**챗봇 담당 — `chat_bot/app/readiness.py`:**

```diff
     if backend == "ollama":
-        url = f"{settings.OLLAMA_HOST.rstrip('/')}/api/tags"
+        url = f"{settings.OLLAMA_HOST.rstrip('/')}/api/ps"
```

이 변경에 더해 Ollama 분기에서 응답 models의 **기대 모델명과 context_length=16384**를 검사하고, 아래 API 예열 완료 상태를 `/ai/ready` 판정에 합친다. 기존 2초 조회 timeout 및 실패 시 503을 유지한다. 다른 백엔드의 모델 목록 검사는 유지한다. `/ai/chat` 진입 직전에도 loaded/not-ready 검사를 하여 probe 갱신 전 유입·직접 호출이 다시 콜드 적재를 시작하지 않도록 한다. 준비되지 않았으면 현재 대체 응답 경로로 즉시 처리하고 실패 원인 metric을 기록한다. HTTP 503으로 바꾸려면 BE의 응답 계약과 재시도 정책도 함께 변경해야 한다.

**챗봇 담당 — `chat_bot/app/main.py`, 신규 예열 상태 helper `chat_bot/app/llm_warmup.py`:**

```diff
 async def lifespan(app: FastAPI):
-    try:
-        orchestrator.warmup()
-    except Exception:
-        logger.exception(...)
-    yield
+    worker = asyncio.create_task(maintain_warmup_state())
+    try:
+        yield
+    finally:
+        worker.cancel()
+        # CancelledError 처리 후 worker 종료를 기다린다.
```

위 lifecycle diff는 변경 지점을 보여 주는 스케치다. `main.py`에는 asyncio/helper import와 worker 취소 처리를, `readiness.py`에는 helper의 완료 상태 확인을 추가한다. 신규 `llm_warmup.py`에 `maintain_warmup_state()`와 상태 조회 함수를 구현하며, worker 계약은 다음과 같다.

- API는 먼저 기동하여 health에 응답하고, 예열은 background에서 수행한다. blocking requests와 `orchestrator.warmup()`은 `asyncio.to_thread` 등으로 event loop 밖에서 실행한다.
- loaded 모델 확인이 실패하면 예열 완료 상태를 false로 한다. loaded로 전환되면 현재 `C/app/pipeline/orchestrator.py:672–708` 업무 예열을 **동시에 하나만** 실행한다. 성공 시에만 ready 상태를 true로 한다. 이를 readiness 검사 때마다 실행하지 않는다.
- 연결/예열 실패는 backoff 30초, 전환마다 최대 3회로 제한하고, 실패 원인·load_duration·prompt_eval_duration 등 시간과 토큰 수만 남긴다. 예열 실패 중에는 `/ai/ready`를 503으로 둔다.
- 사이드카 단독 재시작도 놓치지 않도록 현재 두 컨테이너가 공유하는 `/tmp` 완료 표시의 **부팅 세대 ID**를 worker가 관찰한다. 구현 시 스크립트는 완료 표시 내용에 매 시작마다 새로운 ID를 기록하고, API는 ID 변경/삭제 때 예열 상태를 무효화한다. 이름이 같은 모델의 digest만 비교하면 동일 이미지 재시작을 구분하지 못한다. API 예열은 완료 표시가 생긴 후 시작한다.
- 새로운 세대가 예열 도중 나타나면 이전 결과로 ready를 설정하지 않는다. API 종료 시 thread task 취소만으로 HTTP 요청이 중단된다고 가정하지 말고 예열 HTTP timeout도 제한한다. sidecar 적재와 업무 예열의 대기 시간은 실제 측정 후 조정한다.

**진입점 vs postStart:** 권장안은 사이드카 진입점이다. postStart는 ENTRYPOINT보다 먼저 실행됨이 보장되지 않아 연결 대기와 실패·종료 처리를 여전히 필요로 한다. 일반 initContainer는 뒤에 시작하는 일반 Ollama 컨테이너를 기다리는 적재 요청에 적합하지 않다. [컨테이너 lifecycle hook 문서](https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/)

**위험:** 시작·재시작 시 수 분간 서비스가 unready일 수 있다(현재 replicas 1, Recreate 전략). 잘못된 스크립트/예열 gating은 영구 unready 또는 restart loop를 만들 수 있다. 환경 값·모델명·컨텍스트 일치, 종료 신호 전달, 오래된 완료 파일 삭제와 세대 무효화를 이미지 시험에서 검증해야 한다.

**검증 — 담당자 후속 시험:** 모델 미적재 상태에서는 양쪽 readiness가 실패하고, 적재·smoke·API 업무 예열 후에만 ready가 된다. 최초 요청에 모델 재적재가 없는지 확인한다. LLM 컨테이너만 재시작시켜 API 프로세스가 그대로 있어도 준비 상태가 내려갔다가 적재·업무 예열 후 회복하는지 확인한다. PID 1에 TERM을 보내 자식 종료·파일 정리를 확인하고, 적재 실패·잘못된 모델명·`/api/ps` timeout에서도 false ready가 없는지 확인한다. 이 재시작·Stage 시험은 이번 조사에서 실행하지 않았다.

### 4. 우선순위 3 — 타임아웃·재시도 교정과 자원 여유

#### 4.1 타임아웃과 재시도

`C/app/pipeline/llm.py:24,78,123`의 기본 180초는 개별 HTTP 호출 제한이다. `stream=false`에서 이번 요청은 적재 131초 + 절반의 prefill로 이를 소진했다. 먼저 적재를 트래픽에서 분리하고 캐시 제한 후 prefill을 측정한다. **일반 요청을 일괄 300초로 늘리는 것을 첫 조치로 삼지 않는다.** 적재 전용 300초와 API 업무 예열의 제한은 별도로 설정한다. Requests의 scalar timeout은 연결·읽기 제한이며 전체 `/ai/chat` wall-clock deadline을 보장하지 않는다. [Requests timeout 문서](https://requests.readthedocs.io/en/latest/user/advanced/#timeouts)

재시도 코드 31–38줄은 주석의 “연결 실패만 재시도”와 다르다. `read=0`이 있어도 POST의 500/502/503/504를 `status_forcelist`로 지정했으므로 응답 상태에 따라 **원 요청 + 최대 2번** 생성 요청을 다시 보낼 수 있다. 이번 read timeout이 재시도됐다는 증거는 없지만, 서버 오류 때 장시간 추론을 중복 수행할 위험은 별도로 존재한다. [urllib3 Retry의 connect/read/status 구분](https://urllib3.readthedocs.io/en/stable/reference/urllib3.util.html#urllib3.util.Retry)

**챗봇 담당 — `chat_bot/app/pipeline/llm.py` 제안:**

```diff
 _retry = Retry(
     total=2,
     connect=2,
     read=0,
+    status=0,
+    other=0,
+    redirect=0,
+    respect_retry_after_header=False,
     backoff_factor=0.5,
-    status_forcelist=[500, 502, 503, 504],
     allowed_methods=["POST"],
 )
@@
-        timeout=timeout,
+        timeout=(2, timeout),
```

위 timeout 변경은 Ollama 생성 POST의 connect/read 분리를 뜻한다. `/api/show`도 `(2, 10)`처럼 분리한다. read timeout·이미 처리된 5xx 응답을 자동 재전송하지 않고 대체 응답/오류 metric으로 처리한다. 준비되지 않음이나 busy를 반환받은 호출자의 재시도는 전체 요청 예산 내에서 따로 정하며, API와 BE가 각각 독립적인 재시도 루프를 만들지 않는다. `requests>=2.31`만 선언되어 있고 런타임 urllib3 정확한 버전은 제공되지 않았으므로 담당자는 설치 버전의 옵션 호환성을 확인한다.

**추가 변경 범위 — 챗봇 코드 + BE 조율:** `/ai/chat`은 intent·생성 등 여러 LLM 호출을 할 수 있다. `main.py → orchestrator.py → intent.py/generate.py → llm.py`에 하나의 monotonic deadline을 전달하고, 다음 단계의 남은 예산을 확인해 connect/read 시간을 줄인다. 기존 `CHAT_TIMEOUT_SECONDS`가 “호출당”이라는 의미는 문서화하고 전체 budget은 별도 설정으로 둔다. BE/ingress/client 제한보다 짧게 정해야 하며, 제공 자료에 그 제한이 없어 전체 예산 숫자는 확정하지 않는다. socket timeout 또는 background future timeout만으로 서버 추론까지 확실히 취소되었다고 주장하지 않는다.

**과부하 제어 후보 — 인프라와 챗봇 공동:** `OLLAMA_NUM_PARALLEL=1`을 유지하고 sidecar `OLLAMA_MAX_QUEUE="4"`를 작은 대기열 후보로 시험한다. API도 실행 동시성 1 및 제한된 대기열을 두고 예열/실사용 요청이 무제한으로 쌓이지 않게 한다. 실제 요청량·허용 지연이 없으므로 4는 확정 용량이 아니다. 준비되지 않음/busy에 대한 처리 계약과 queue wait metric을 먼저 정한다. [Ollama 큐 제한 문서](https://docs.ollama.com/faq)

출력에 `num_predict` 상한이 없는 점도 후속 점검 대상이다. intent·응답 스키마의 정상 최대 출력 및 thinking 토큰을 측정한 다음 한도를 정한다. 임의의 낮은 값으로 JSON을 자르는 수정은 제안하지 않는다. keep_alive는 API 요청에서 이미 `-1`로 명시하므로 sidecar `OLLAMA_KEEP_ALIVE`만 유한값으로 바꾸어도 해당 요청 동작은 바뀌지 않는다(`llm.py:109`).

**위험·검증:** 5xx 자동 재시도를 없애면 일시 오류가 더 빨리 대체 응답으로 드러날 수 있다. 연결 실패만 최대 2회 재시도하고, read timeout과 500/503 응답에는 재시도가 0회인지 stub server로 검증한다. timeout이 `ConnectionError`로 감싸져도 현재 예외 경로가 처리하는지 확인한다. 캐시 0/0 및 bounded 후보 각각에서 적재 후 최초·연속 요청, 긴 프롬프트, queue wait를 측정한다. 일반 요청 180초에서도 지속적으로 실패한다면 프롬프트·출력량·CPU throttling과 deadline을 함께 조정하고, timeout 증설만으로 해결됐다고 판정하지 않는다.

#### 4.2 메모리 requests/limits

**LLM limit 10Gi:** 우선 RAM 캐시·체크포인트를 제한한 뒤 유지한다. 8GiB 캐시와 최대 32개 활성 체크포인트를 그대로 둔 채 12/16Gi로 늘리는 것은 성장 원인을 해결하지 못한다. `use_mmap=true` 강제도 현재 압력 감지 선택을 덮어쓰므로 검증 없이 적용하지 않는다.

**API limit 2Gi:** 제공된 최대 working set 1.81GiB는 여유 **약 0.19GiB, 9.5%**에 불과하다. 현재 Pod에는 API OOM 기록이 없지만 임베딩·세션 및 순간 할당 여유가 부족할 가능성을 별도로 검증해야 한다. 실제 node allocatable이 허용하면 다음을 조정 후보로 삼는다.

**인프라 담당 — `k8s/base/ai/ollama-deployment.yaml`, `ai-ollama` 후보 diff(용량 확인 후):**

```diff
           resources:
             requests:
               cpu: 250m
-              memory: 1Gi
+              memory: 2Gi
             limits:
               cpu: "1"
-              memory: 2Gi
+              memory: 3Gi
```

LLM request 6Gi도 캐시 제한 후의 정상 사용·적재 피크로 재산정한다. request를 올리는 것은 스케줄링 예약·overcommit을 개선하고, limit을 올리는 것은 컨테이너 OOM 경계를 바꾸는 별도 조치다. cache 0/0 이후에도 실제 전체 메모리 피크가 10Gi에 가깝다면 제한을 유지한 채 **LLM limit 12Gi**를 추가 후보로 검토한다. 수집 자료만으로 지금 증설이 필수라고 확정하지 않는다. [Kubernetes requests·limits·메모리 OOM 설명](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)

**노드 한계 확인이 선행 조건이다.** Pod에는 노드 이름과 T4 GPU 지정만 있고 인스턴스 타입·물리 RAM·allocatable·다른 Pod 점유 자료가 없다. GPU VRAM 용량과 호스트 RAM은 서로 다르다. 10Gi+3Gi면 이 Pod의 limit 합계 13Gi, 12Gi+3Gi면 15Gi이므로 노드 allocatable에서 다른 워크로드·DaemonSet와 운영 여유를 뺀 값에 비춰 검토한다. allocatable에 이미 반영된 시스템 예약을 중복 차감하지 않는다. requests 합계만 맞는다고 동시 피크까지 안전한 것은 아니다. 이 확인을 위해 Stage 조회 명령을 실행하지 않았다.

**위험·검증:** request 증가로 Pod가 Pending이 될 수 있으며 limit 증가로 노드 전체 압력·다른 Pod 축출 위험이 커질 수 있다. 인프라 담당이 allocatable, 다른 Pod requests/실사용, MemoryPressure, CPU throttling을 확인한다. API의 임베딩 초기화·동시 세션에서도 cgroup 메모리 피크를 측정해 3Gi 후보가 필요한지 결정한다. 초기 10Gi LLM limit에서 피크 8Gi 이하 정도의 20% 여유를 목표 후보로 삼되, working set 한 지표만으로 통과시키지 않는다.

### 5. 인계·검증 기준

| 순위 | 담당·변경 파일 | 적용 후 반드시 볼 항목 |
|---|---|---|
| 1 | 인프라: sidecar env·이미지 digest. 챗봇: `deploy/ollama/Dockerfile` 버전 고정 | 실제 바이너리 버전/지원, 캐시·체크포인트 비활성화 로그, 전체 cgroup 메모리 피크, JSON·긴 문맥 회귀와 prefill 지연 |
| 2 | 챗봇: 진입점·ready helper·`app/readiness.py`·`app/main.py` 예열 worker. 인프라: startup/readiness exec | 적재·예열 전 unready, 사전 적재 후 ready, 최초 업무 요청에 load 비용 없음, LLM 단독 재시작/부팅 세대 변경 후 재예열, TERM 전달·오래된 완료 파일 정리 |
| 3 | 챗봇: `app/pipeline/llm.py`, 요청 budget 전달·동시성. 인프라: 노드 용량 검토 후 requests/limits·큐 설정. BE: timeout/오류 계약 | 연결 실패 외 자동 재생성 없음, 전체 요청 예산·큐 제한, API 메모리 여유, Pending·노드 MemoryPressure 없음 |

담당자 후속 검증은 모델 최초 시작과 LLM 단독 재시작을 포함하고, 합성 대화로 최소 30–60분 또는 100회 이상의 intent/생성 전환을 수행한다. 사용자 원문을 새 로그에 복사하지 않고 토큰 수·시간·상태·익명 요청 ID만 남긴다. cgroup `memory.current`, `memory.peak`, `memory.events`의 oom/oom_kill, working set·RSS·file cache, container restart, GPU VRAM, CPU throttling, Ollama load/prompt_eval/eval duration을 함께 수집한다. OOM·예기치 않은 재시작 0회, false ready 0회, 정의한 지연 budget 만족과 JSON 정상 완료를 함께 통과 조건으로 삼는다.

이번 결과는 **원인 조사와 수정안 인계까지**다. 코드·설정 구현, 이미지 재빌드, 실제 env 적용 시험과 Stage 검증은 수행하지 않았으므로 해당 결과가 통과했다고 보고하지 않는다.

작성 후 확인: 이 파일의 기존 지시문은 그대로이며, 해시 비교 대상으로 잡은 기존 제공 자료·GenAI 사본 67개는 SHA-256 변경이 없었다. 비교 중 handoff 디렉터리에 신규 요약 파일 1개가 나타났으나 본 작업에서 생성하거나 수정한 파일은 아니다. `git --no-optional-locks status --short`는 시작 때와 동일했다(기존 README 변경 및 미추적 설계 문서·skill 디렉터리만 표시). 본 작업의 쓰기는 이 파일의 `## 결과`에만 수행했다.
