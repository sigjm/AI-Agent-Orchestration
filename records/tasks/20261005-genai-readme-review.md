# GenAI 저장소 README 검수

관리자 지시. 사용자 요청: "코덱스한테 readme.md 검수 맡겨봐".
**읽기 전용 검수다. 파일을 고치지 말고**, 찾은 문제와 고칠 문장을 이 파일 하단 `## 결과`에 한국어로 쓴다. git 상태를 바꾸는 명령도 금지.

## 검수 대상

- 새 README: `<scratchpad>/genai-readme/README.md`
  - 이 폴더는 `Jangingmall/GenAI` `main`(`16ed39e`)을 받은 사본이고, README와 `docs/images/`만 바뀌었다. 바뀌기 전 README는 `git -C <그 폴더> show HEAD:README.md`로 볼 수 있다
- 아키텍처 그림: 같은 폴더 `docs/images/genai-architecture.png`(README에 들어가는 이미지), 원본 `docs/images/genai-architecture.html`
- 형식 참고(사용자가 준 다른 프로젝트 README): `~/Downloads/README-3.md`, `~/Downloads/README-2.md`

## 확인할 것

1. **사실 정확성 — 코드·설정과 대조** (가장 중요)
   - 엔드포인트·메서드·상태 코드: `page_generation/src/detail_page_ai/app.py`, `chat_bot/app/main.py`
   - 작업 상태 이름과 흐름(`QUEUED → ANALYZING → DRAFT_READY → 승인 → RENDERING → COMPLETED`): `page_generation/src/detail_page_ai/dto.py`, `ai_dto.py`, `pipeline.py`
   - 모델 이름·양자화·포트·GPU 메모리 비율(`--mem-fraction-static 0.50`), 누끼 CPU, 작업 순차 처리, 모델 프로세스가 죽으면 API 종료: `page_generation/deploy/sglang/entrypoint.sh`, `src/detail_page_ai/source_photos.py`, `pipeline.py`, `app.py`
   - 근거 검증 설명(사진에서 보이는 문구만 남기고 추정 문구는 '확인 필요'로 분리): `page_generation/src/detail_page_ai/validation.py`의 `sanitize_profile_for_render`
   - 챗봇: 하이브리드 검색·RRF·유사도 컷·등급 가중 랭킹·좁혀 가기 캐시 30분, LLM 캐시 상한 2,048MiB·체크포인트 2개·사전 적재·워밍업 재시도: `chat_bot/app/`, `chat_bot/deploy/ollama/`
   - 실행 명령·환경변수 이름: `page_generation/README.md`, `local.env.example`, `chat_bot/README.md`, `chat_bot/README-docker.md`, `chat_bot/app/config.py`
   - CI 설명과 테스트 수(536 passed / 303 passed, 3 deselected): `.github/workflows/genai-ci.yml`, 최근 실행 `gh run view 37259193933 -R Jangingmall/GenAI`
   - 배포 서술(EKS, T4 16GB / L40S 48GB, ECR 이미지 이름, S3→PVC, CodeBuild 러너, Secrets Store CSI): 이전 README와 인프라 매니페스트(읽기 전용 사본 `<scratchpad>/infra-ro`, `k8s/base/ai`, `k8s/overlays/stage`)
   - 코드로 확인할 수 없는 주장은 "근거 없음"으로 표시한다
2. **이전 README에서 빠진 중요한 정보**가 있는지 (예: 4-2 상품 동기화 backfill, 4-4 세션·이력, 응답 규약 등). 빠져도 되는 것과 되살려야 하는 것을 나눈다
3. **링크·이미지**: 상대 경로 링크와 앵커가 모두 실제로 있는지, GitHub에서 그대로 렌더되는지(HTML 정렬 태그, 배지 URL 포함)
4. **아키텍처 그림과 본문이 서로 맞는지** (노드·화살표·라벨이 본문 설명과 다르지 않은지)
5. **문장**: 한국어가 자연스러운지, 같은 대상을 다르게 부르는 곳(예: BE/백엔드, 상세페이지 AI/상세페이지 서버), 너무 긴 문장, 오타
6. **형식**: 참고 README 두 개의 구성(커버·배지·목차·핵심 기술 문제와 해결·아키텍처·배포·품질·스택·구조·실행·API·협업)을 잘 따랐는지, 빠진 섹션이 있는지
7. **공개 저장소에 올려도 되는지**: 비밀값·계정 번호·내부 전용 주소·개인 정보가 들어가 있지 않은지

## 결과에 쓸 것

- 심각도별 목록(틀린 사실 > 빠진 중요 정보 > 링크·렌더 > 문장·형식): 줄 번호, 문제, 근거(파일·줄), **바꿀 문장 제안**
- 문제없음으로 확인한 항목도 짧게 (무엇을 대조했는지)
- 그대로 올려도 되는지 한 줄 판정

## 결과

### 1. 사실 오류·운영 상태 설명 — 우선 수정

1. **README 202행 — 모든 모델 가중치가 이미지 밖에 있다는 설명은 틀립니다.** `chat_bot/deploy/ollama/Dockerfile:50-55`는 빌드 중 `gemma4:12b`를 이미지에 `ollama pull`하고, CI 주석 `.github/workflows/genai-ci.yml:135-138`도 챗봇 LLM이 이미지에 포함된다고 확인합니다. 반면 상세페이지·BGE-M3는 Infra 문서 `k8s/components/ai-model-storage/README.md:6,12,46`에서 S3/PVC 경로로 설명합니다. README 198행의 챗봇 Pod 설명과도 모순됩니다.
   - **제안 문장:**
     > 상세페이지 모델과 BGE-M3는 S3에서 PVC로 준비하고, 챗봇 gemma4:12b는 `chatbot-llm` 이미지에 포함합니다.

2. **README 216·440행 — CI가 digest를 Infra에 자동 전달하는 것처럼 읽힙니다.** `.github/workflows/genai-ci.yml:276-320`은 GenAI 이미지 발행과 digest를 Actions Summary에 기록합니다. Infra의 `k8s/components/ai-model-storage/README.md:112`는 그 digest를 배포 설정에 반영해야 하며 workflow가 YAML을 자동 변경하지 않는다고 명시합니다.
   - **제안:** `main 반영 시 CI가 SHA 태그 이미지와 digest를 ECR에 발행해 Actions Summary에 기록합니다. Stage는 Infra 저장소의 배포 설정에 해당 digest를 반영해 배포합니다.`

3. **README 167행 및 아키텍처 그림 — CloudFront 공개가 이미 적용된 사실처럼 단정합니다.** Backend `src/main/java/com/jangingmall/backend/content/application/GenerationService.java:44-47`는 `ai-generated/*`를 CloudFront에서 공개하려면 인프라 승인·적용이 필요하다고 명시합니다. S3 저장은 같은 파일 `:185-215`에서 확인됩니다.
   - **제안 문장:**
     > BE는 최종 PNG와 사진을 S3에 저장합니다. FE가 공개 URL로 조회하려면 CloudFront에서 `ai-generated/*` 경로를 노출해야 하며, 적용 상태는 Infra 설정으로 확인해야 합니다.

4. **README 380행 — Stage 비밀값의 CSI 마운트 완료 여부를 단정하기 어렵습니다.** Infra `k8s/overlays/stage/ai-sglang-secret-provider.yaml:11-12`는 SSM 경로를 제안값으로 표시하고 파라미터 등록과 IRSA 권한을 선행 조건으로 적었습니다. `ai-chatbot-secret-provider.yaml:11-12`도 실제 경로 확정과 권한 부여를 TODO로 둡니다.
   - **제안 문장:**
     > 챗봇 API는 `DB_PASSWORD_FILE`을 지원합니다. Stage에서 Secrets Store CSI로 파일을 제공하려면 SSM 파라미터 등록과 해당 IRSA 권한 적용을 먼저 확인해야 합니다.

5. **README 152행 — API가 기동 때 LLM 준비를 기다린다는 설명은 동작과 다릅니다.** `chat_bot/app/main.py:113-130`은 FastAPI 기동을 막지 않고 워밍업을 백그라운드로 시작합니다. `chat_bot/app/warmup_state.py:130-132`도 lifespan 기동을 막지 않는다고 설명하며, 준비 전 상태는 `/ai/ready`가 판정합니다.
   - **제안 문장:**
     > API는 기동을 막지 않고 백그라운드에서 LLM 연결과 워밍업을 재시도합니다. `/ai/ready`는 DB·임베딩·실제 로드된 LLM과 워밍업 상태를 확인합니다.

6. **README 69행 — `편집 가능한 React 문서`는 산출물 계약을 과장합니다.** `page_generation/README.md:169-180`의 `react_document`는 허용 컴포넌트로 FE가 렌더링하는 제한형 JSON AST이며 React 코드/JSX 문서가 아닙니다. 초안 문구 저장은 별도 draft API(`page_generation/README.md:156-160`) 계약입니다. FE 편집기가 AST 자체를 직접 편집한다는 사실은 GenAI 코드·계약에서 확인되지 않습니다.
   - **제안 문장:**
     > 결과에는 PNG와 FE가 허용된 컴포넌트로 렌더링하는 제한형 `react_document`(JSON AST)이 포함되며, 판매자가 수정한 문구는 draft API로 저장합니다.

7. **README 111-113행 — 판매자 작성 내용이 고객 문구에 남는다는 근거 처리 설명이 넓습니다.** `page_generation/src/detail_page_ai/validation.py:431-466`은 고객용 `features`와 `copy_sections`에서 `evidence=image-visible`만 통과시킵니다. `user_hints`는 `:444-458`에서 불확실성 경고가 판매자 제공 내용으로 확인되는지 판별하는 데 쓰입니다. 따라서 판매자 문구가 해당 allowlist를 통해 그대로 보존된다고 설명하면 코드 동작과 다릅니다.
   - **제안 문장:**
     > 고객용 `features`·`copy_sections`는 `evidence=image-visible` 항목만 통과합니다. 나머지는 판매자 제공 `user_hints`와 대조해 미확인일 때 경고로 남깁니다.

8. **README 134행 — GPU 메모리 50%를 고정한다는 표현은 환경 설정 가능성을 빠뜨립니다.** `page_generation/deploy/sglang/entrypoint.sh:7,47-52`에서 `TEXT_MEM_FRACTION` 기본값이 `0.50`이고 이를 `--mem-fraction-static`에 전달합니다. 운영 환경변수로 바꿀 수 있으므로 고정값은 아닙니다.
   - **제안 문장:**
     > 텍스트 SGLang의 `--mem-fraction-static` 기본값은 0.50이며, `TEXT_MEM_FRACTION`으로 조정할 수 있습니다.

9. **README 323-334행 — 상세페이지 AI의 새 클론 실행 순서가 실패합니다.** `.venv` 생성·활성화 전에 `.venv/bin/python`을 실행하므로 새 환경에는 해당 실행 파일이 없습니다. `page_generation/pyproject.toml:22-23`은 설치된 CLI 이름이 `serve-ai`임을 확인합니다.
   - **제안:** 설치 전에 `python3.13 -m venv .venv`와 `source .venv/bin/activate`를 추가하고, 활성화한 상태에서 `python -m pip install -e '.[dev]'` 및 `serve-ai`를 실행하도록 안내합니다.

10. **README 459행 — 검증 조합의 출처가 최근 CI와 다릅니다.** 문서의 조합은 `chat_bot/README-docker.md:48`에도 있지만, `chat_bot/requirements.txt:17-18`은 `sentence-transformers>=3.0`으로 버전을 고정하지 않습니다. 2026-10-05 main CI 로그는 `transformers==5.18.0`으로 설치해 통과했습니다. 5.17.0 조합이 별도로 검증된 것이라면 수동 검증임을 구분해야 합니다.
   - **제안 문장:**
     > CI 검증 조합은 `torch==2.6.0 / transformers==5.18.0 / sentence-transformers==6.1.0` (2026-10-05)입니다. 별도 수동 검증 조합을 유지한다면 실행 기록을 함께 링크합니다.

### 2. 중요한 누락·표현 보정

1. **README 91-92행 — 기존 판매 상품의 최초 적재(backfill)가 빠졌습니다.** 상세페이지로 새로 저장되는 상품의 동기화만 설명합니다. Backend `AiProductBulkSyncRunner.java:17-31`은 조건부 일회성 Job을 제공하고, `ContentService.java:651-666`은 기존 `ON_SALE` ID를 순회 동기화합니다. 검색 카탈로그 초기 구성에 필요한 절차이므로 한 줄 추가를 권합니다.
   - **제안 문장:**
     > 기존 ON_SALE 상품은 백엔드 일괄 동기화 Job이 전체 ID를 순회해 `/ai/products`에 초기 적재합니다.

2. **README 176행 — “무상태”와 세션 키 메모리 캐시의 관계를 분명히 하면 좋습니다.** 챗봇은 BE 소유의 세션·대화이력을 받지만 내부 후보 상태는 메모리에 보관합니다. `chat_bot/app/session_store.py:1-12,20-30`은 세션별 후보·필터·상품 ID·검색문장, TTL 30분, 최대 500개를 확인합니다.
   - **제안 문장:**
     > 세션·대화이력은 BE가 관리해 요청에 전달하고, 챗봇은 좁혀 가기용 후보·필터 상태만 `session_id` 키로 메모리에 최대 30분(최대 500개) 보관합니다.

3. **README 229행 — 테스트와 Docker 검증의 실행 출처를 나누어야 합니다.** 최신 main push #37259193933에서 상세페이지 536건, 챗봇 303건(+ 3건 제외)이 통과했지만 Docker validation job은 `skipped`였습니다. 별도 PR #37258549061에서 세 이미지 Docker 검증이 모두 통과했습니다. 현재 표의 “최근 CI 결과 / 3종 통과”만으로는 서로 다른 실행을 구분할 수 없습니다. `.github/workflows/genai-ci.yml:98-101`은 Docker 검증이 PR에서만 동작함을 명시합니다.
   - **제안 문장:**
     > 2026-10-05 main CI(#37259193933): page-generation 536 passed, chatbot-api 303 passed·3 deselected; 이미지 발행 3종 성공, Docker validation은 skipped. PR CI(#37258549061): linux/amd64 Docker validation 3종 통과.

4. **응답·세션 설명은 대부분 유지되어 있습니다.** README 81·84-86행에 응답 형식, BE 카드 조립, 빈 결과 정상 응답이 있고 175-176행에 세션·이력 담당도 있습니다. 이전 README의 응답 규약을 별도 복원할 필요는 없습니다. 91-92행의 backfill만 보충하면 상품 동기화 설명이 더 완결됩니다.

### 3. 링크·그림·형식

- 상대 Markdown 링크, 이미지 파일 경로, 내부 앵커는 모두 대상 사본에 존재합니다. GitHub Markdown 렌더링에서도 목차 앵커, `<p align="center">`, 배지 이미지·링크가 유지되는 것을 확인했습니다. 외부 배지 서버의 실시간 응답은 로컬 TLS 검증 문제로 확인하지 못했으므로 URL 문법과 렌더링만 검수했습니다.
- 아키텍처 그림의 FE/BE/AI 경계, 동기 챗봇·비동기 상세페이지, `/ai/products` 동기화 화살표는 본문과 일치합니다. S3 이후 CloudFront 제공은 1번 사실 오류 3항처럼 적용 여부를 조건부로 써야 합니다.
- 커버·배지·목차·핵심 문제·아키텍처·배포·품질·스택·프로젝트 구조·실행·API·협업을 포함해 참고 README의 구성은 충족합니다. 중대한 오타나 렌더 형식 문제는 찾지 못했습니다.

### 4. 공개 적합성

- README에서 AWS 자격 증명, 실제 비밀번호·토큰, 계정 번호, 사설 IP, 개인 정보는 찾지 못했습니다. 환경 변수명, EKS/Stage 구성, ECR 저장소 이름은 노출됩니다. GitHub API에서 `Jangingmall/GenAI` 저장소는 현재 private로 확인됩니다.
- **판정: 현 상태 그대로 공개하는 것은 보류하는 편이 좋습니다.** 위의 배포·모델·워밍업 사실을 고치고 CI 실행 출처를 분리한 뒤 공개하세요. 직접 비밀값은 발견하지 않았지만 Stage 인프라 구조와 이미지 저장소 이름을 공개할 의도가 맞는지도 확인이 필요합니다.

검수는 읽기 전용으로 수행했습니다. 새 README·코드·설정은 수정하지 않았고, 테스트 실행도 하지 않았습니다.
