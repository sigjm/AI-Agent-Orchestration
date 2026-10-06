# 추가 검수 보고서: 미검수 영역 (리팩터링·스펙·스크립트·웹·EKS 대외 서술)

- **검수자 (워커)**: agy
- **검수일시**: 2026-09-16
- **대조 대상 범위**:
  - `docs/refactoring/*.md` (5개)
  - `docs/superpowers/plans/*.md`, `docs/superpowers/specs/*.md` (7개)
  - `docs/data/*.md`, `docs/references/*.md` (2개)
  - `scripts/` 디렉터리 전체 (22개 스크립트)
  - `web/` 디렉터리 전체 (8개 파일)
  - `docs/operations/eks-workload-spec.md` (인프라팀 대외 전달용 원본 검토)

---

## 총평 및 요약

- **총 발견 건수**: 10건
  - **치명 (Fatal)**: 3건 (인프라팀 배포 반려 위험, 고립된 대형 데드 스크립트 등)
  - **불일치 (Inconsistency)**: 3건 (과거 삭제/이동 파일의 현재형 참조, 로컬 작업환경 노출)
  - **사소 (Trivial)**: 4건 (비활성 스크립트, 미서빙 정적 파일 번들링, 대외 문서 문체)
- **스크립트 실행성 (Syntax & Import)**:
  - `scripts/` 내 모든 Python 파일(16개)은 문법 및 임포트 로딩 정상(`[OK SYNTAX]`, `[OK IMPORT]`).
  - `scripts/browser/` 및 `scripts/runtime/` 내 모든 JavaScript/Node 파일(5개)은 문법 검사 정상(`node -c` 통과).
  - `scripts/orchestration/orc` bash 스크립트 문법 검사 정상(`bash -n` 통과).
- **시점 기록 문서의 정상 상태 확인**:
  - `docs/superpowers/plans/` 및 `docs/superpowers/specs/` 내의 미구현 모듈 제안이나 초기안은 상단에 회고/보관용 안내문(banner)이 정확히 배치되어 있어 의도된 시점 기록(이상 없음)으로 판정했습니다.

---

## 상세 발견 사항 목록

### 1. 치명 (3건)

#### [치명-01] 인프라팀 전달 문서 내 'Dockerfile 미빌드/빌드 성공 여부 미확인' 서술
- **대상 파일**: `docs/operations/eks-workload-spec.md:7`
- **내용**: `다만 이 Dockerfile 은 아직 빌드하지 않았고, GPU 에서도 한 번도 실행하지 않았습니다. 이미지 빌드 성공 여부, 두 모델이 L40S 한 장에 실제로 올라가는지, 생성·편집 품질과 처리 시간은 첫 배포에서 확인해야 합니다.`
- **대조 근거 [확인]**:
  - `docs/operations/eks-workload-spec.md`는 인프라팀에 전달하기 위해 작성된 공식 답변 문서입니다.
  - 내부 회고/과장 금지 원칙상 사실을 명시하는 것은 필요하나, "Dockerfile을 아직 한 번도 빌드해보지 않아서 이미지 빌드가 성공할지 여부조차 알 수 없다"는 서술을 그대로 인프라팀에 넘기면, **"개발팀에서 빌드 성공 여부조차 확인하지 않은 Dockerfile을 인프라팀에 전달하여 빌드 오류를 떠넘기려 한다"**는 이유로 인프라팀의 즉각적인 작업 거부나 심각한 책임 공방을 유발할 수 있습니다.
- **제안 조치**: "내부 로컬 개발 환경(Apple Silicon) 제약으로 인해 `linux/amd64` GPU 이미지 빌드 및 실기동 실측을 인프라 배포 단계에서 협력하여 진행하고자 합니다" 등 전문적이고 협업 지향적인 문장으로 정제해야 합니다.

#### [치명-02] 인프라팀 전달 문서 내 FLUX 라이선스 미해결 상태 노출로 인한 배포 반려 위험
- **대상 파일**: `docs/operations/eks-workload-spec.md:153`
- **내용**: `3. 이미지 모델 라이선스. 현재 이미지 모델은 FLUX Non-Commercial License 원본을 커뮤니티가 4bit 로 양자화한 가중치를 사용합니다. 상업 운영 전에 라이선스 확인이 필요하다는 점을 기록해 둡니다.`
- **대조 근거 [확인]**:
  - 원본 `black-forest-labs/FLUX.2-klein-9B`는 비상업용(Non-Commercial) 라이선스입니다.
  - 관리자 결정으로 커뮤니티 4bit 본을 채택한 내부 사정은 이해되나, 이를 인프라팀 대외 전달 문서에 "상업 운영 전 라이선스 확인이 필요하다는 점을 기록해 둡니다"라고 명시하여 전달하면, 기업 환경에서 인프라팀이나 컴플라이언스/보안 부서가 라이선스 리스크를 이유로 EKS 배포 승인을 즉각 보류(Block)할 가능성이 매우 높습니다.
- **제안 조치**: 공식 오픈 대안인 `black-forest-labs/FLUX.2-klein-4B` (Apache 2.0 라이선스)를 기본으로 제시하거나, 라이선스 법무 확인 완료 후 배포 스펙에 포함하도록 대외 문서를 분리해야 합니다.

#### [치명-03] `scripts/build_review_page.py` (1,872줄) 완전 고립 데드 스크립트 방치
- **대상 파일**: `scripts/build_review_page.py:1-1872`
- **내용**: 파일 크기 55KB, 1,872줄에 달하는 대형 스크립트.
- **대조 근거 [확인]**:
  - 저장소 전체(`src/`, `tests/`, `docs/`, `scripts/`, `package.json`)에서 `build_review_page.py` 또는 `build_review_page`를 참조하거나 호출하는 곳이 **단 1곳도 없음 (0 references)**.
  - 실제 리뷰 아티팩트 생성은 `scripts/build_review_artifact.py` (310줄)와 `scripts/build_review_sheet.py`가 담당하고 있으며 문서에서도 이들만 안내되고 있습니다.
- **영향**: 과거에 작성되었다가 `build_review_artifact.py`로 대체된 후 삭제되지 않고 남아 있는 고립된 데드 코드(dead code)입니다. 유지보수 부담 및 혼선을 초래하므로 삭제 또는 아카이빙이 필요합니다.

---

### 2. 불일치 (3건)

#### [불일치-01] 리팩터링 문서 내 삭제/이름 변경된 `generate_attached_detail_page.py` 현재형 참조
- **대상 파일**:
  - `docs/refactoring/refactoring-plan.md:255`: `training_augmentation.py, pipeline.py, factory.py, runner.py, generate_attached_detail_page.py와 테스트가 기존 import 경로로 계속 동작하는지 확인한다.`
  - `docs/refactoring/diagnosis-codex.md:71`: `생성기 construction은 실행 코드에 3곳(..., scripts/runtime/generate_attached_detail_page.py)이고...`
  - `docs/refactoring/diagnosis-codex.md:131`: `build_detail_page_html의 실행 호출은 3곳이다: ..., scripts/runtime/generate_attached_detail_page.py, ...`
  - `docs/refactoring/diagnosis-agy.md:84`: `SourcePreservingProductPhotoGenerator: 외부 3곳 (factory.py, runner.py, generate_attached_detail_page.py)`
- **대조 근거 [확인]**:
  - `scripts/runtime/generate_attached_detail_page.py` 파일은 실제로 존재하지 않습니다.
  - 해당 스크립트는 하드코딩 부채 데모의 오해를 방지하기 위해 `scripts/runtime/demo_fixed_profile_render.py`로 이름이 변경되었으며, `docs/api/be-fe-ai-integration-spec.md:563`에서도 새 이름으로 갱신되었습니다.
- **설명**: 시점 기록 문서이긴 하나, `refactoring-plan.md`의 실행 체크리스트 등에서 존재하지 않는 과거 파일명을 현재형 점검 대상으로 지시하고 있어 불일치합니다.

#### [불일치-02] 리팩터링 진단서 내 삭제된 `check_reference_label.py` 현재형 참조
- **대상 파일**: `docs/refactoring/diagnosis-agy.md:314`
- **내용**: `3. check_reference_label.py: '참고용' 라벨 도달 및 원본 오표기 판정 불변 확인`
- **대조 근거 [확인]**:
  - `scripts/check_reference_label.py`는 커밋 `cfd60bb`에서 '참고용' 라벨 영구 제거 정책에 따라 완전 삭제된 파일입니다.
  - `cleanup-diagnosis-agy.md:61-66` 및 `refactoring-plan.md:5, 345`에는 삭제 사실이 반영되어 있으나, `diagnosis-agy.md:314`에는 삭제 전 서술이 남아 있어 존재하지 않는 스크립트를 가리키고 있습니다.

#### [불일치-03] 인프라팀 전달 문서 내 작업자 로컬 git 환경 사정 노출
- **대상 파일**: `docs/operations/eks-workload-spec.md:142`
- **내용**: `1. 현재 이 저장소에는 원격(remote)이 없습니다. 배포용 원격 저장소를 먼저 정해 주셔야 하고, 지금 작업물은 deploy/ubuntu 브랜치에 있습니다. main 발행을 쓰려면 이 브랜치를 main 에 병합해야 합니다.`
- **대조 근거 [확인]**:
  - "원격(remote)이 없다"는 서술은 작업자의 현재 로컬 개발 머신 상태(git remote 미등록, Xcode 라이선스 미동의 등)를 뜻합니다.
  - 공식적인 인프라 배포 문서에 "이 저장소는 원격이 없다"고 전달하면 인프라팀 입장에서 저장소의 형상 관리 체계 자체를 의심하게 만들 수 있습니다.
- **제안 조치**: "배포 파이프라인(CI/CD) 연동을 위한 공식 원격 Git 저장소 설정 및 `deploy/ubuntu` 브랜치의 `main` 병합 필요"로 객관화된 표현을 사용해야 합니다.

---

### 3. 사소 (4건)

#### [사소-01] 인프라팀 전달 문서 내 구어체 및 비격식 요청조 문체
- **대상 파일**:
  - `docs/operations/eks-workload-spec.md:24`: `**멀티컨테이너로 나누지 말아 주세요.** 우리 파이프라인은 SGLang 서버가 두 개...`
  - `docs/operations/eks-workload-spec.md:60`: `**liveness 를 /health/ready 로 잡지 말아 주세요.**`
  - `docs/operations/eks-workload-spec.md:61`: `...잡아 주시면 좋겠습니다.`
- **대조 근거 [확인]**:
  - 기술적 사유(GPU 배타 할당 제약, 모델 로딩 중 무한 재시작 방지)는 완벽히 타당하나, 문서 표현이 메신저 대화체의 요청조(~말아 주세요, ~좋겠습니다)로 작성되어 있습니다.
- **제안 조치**: "단일 파드 내 멀티컨테이너 분할 불가 (사유: NVIDIA Device Plugin 컨테이너 단위 GPU 배타 할당)", "Liveness Probe 설정 시 `/health/ready` 사용 금지 (사유: 모델 로딩 중 재시작 루프 발생)" 등으로 격식 있는 기술 규격 문체로 전환 권장.

#### [사소-02] 인프라팀 전달 문서 내 방어적 응답 문체
- **대상 파일**: `docs/operations/eks-workload-spec.md:34`
- **내용**: `Ollama Dockerfile | 작성하지 않았습니다. 우리는 L40S 한 장만 사용합니다. 필요하시면 추가 작성 가능합니다`
- **대조 근거 [확인]**:
  - "작성하지 않았습니다"라는 표현은 질의응답 시 다소 퉁명스럽게 받아들여질 수 있습니다.
  - "L40S 단일 워크로드로 확정되어 Ollama Dockerfile은 작성 대상에서 제외 (단일 GPU 공존 구조 채택)"으로 정제 권장.

#### [사소-03] `web/` 내 데모/테스트용 UI 파일의 프로덕션 컨테이너 번들링
- **대상 파일**:
  - `web/ai_input.html`, `web/ai_input.css`, `web/ai_input.js` (3개 파일)
  - `web/ai_draft_preview.html`, `web/ai_draft_preview.css`, `web/ai_draft_preview.js` (3개 파일)
- **대조 근거 [확인]**:
  - `src/detail_page_ai/app.py`에는 `web/`을 정적 파일(`StaticFiles`)로 마운트하거나 서빙하는 라우트가 전혀 없음.
  - `src/detail_page_ai/html_renderer.py`는 오직 `web/detail_page.html`과 `web/detail_page.css` 2개 파일만 렌더링 템플릿으로 읽음.
  - 위 6개 파일은 `scripts/browser/`의 Playwright 브라우저 테스트(`test_input_page.mjs`, `test_draft_preview.mjs`)에서만 로컬 파일(`file://` 또는 로컬 서버)로 열어보는 용도임.
  - 그럼에도 불구하고 `Dockerfile:34` 및 `sglang/Dockerfile:86`에서 `COPY web ./web`으로 프로덕션 컨테이너 이미지 전체에 번들링되고 있음.

#### [사소-04] `scripts/dataset/` 내 사실상 비활성화된 보관용 스크립트
- **대상 파일**:
  - `scripts/dataset/build_flux2_product_scene_50.py`
  - `scripts/dataset/build_training_dataset.py`
- **대조 근거 [확인]**:
  - 문법 및 실행(`--help`)은 정상 동작함.
  - 그러나 현재 어떤 운영 문서, 평가 파이프라인, CI에서도 호출되지 않으며, 오직 `tests/test_project_layout.py:62-63`에서 "과거 루트 경로에 남아있지 않은지" 확인하는 삭제 검증 assertion 목록에만 이름이 등장함.
  - 실제 파이프라인과 분리된 과거 데이터셋 생성 스크립트로 파악됨.

---

## 항목별 검증 요약 매트릭스

| 검증 영역 | 판정 | 주요 내용 |
|---|:---:|---|
| **1. 죽은 참조** | **불일치** | `docs/refactoring/` 내에서 `generate_attached_detail_page.py`(demo_fixed_profile_render로 변경됨)와 `check_reference_label.py`(삭제됨)를 현재형으로 가리키는 서술 발견. `docs/superpowers/`, `docs/data/`, `docs/references/`는 이상 없음. |
| **2. scripts/ 죽은 스크립트** | **치명** | 22개 스크립트 전원 문법/임포트 로딩 통과. 그러나 `scripts/build_review_page.py`(1,872줄)는 저장소 전체에서 0회 참조되는 완전한 데드 스크립트임. `build_flux2_product_scene_50.py`, `build_training_dataset.py`는 사실상 비활성 상태. |
| **3. web/ 참조 여부** | **사소** | `web/detail_page.html`, `detail_page.css`는 렌더러에서 실제 사용. 나머지 6개 파일(`ai_input.*`, `ai_draft_preview.*`)은 FastAPI 앱에서 서빙되지 않고 브라우저 테스트에서만 사용되나 도커 이미지에 함께 번들링됨. |
| **4. EKS 대외 노출 서술** | **치명** | `docs/operations/eks-workload-spec.md`에서 인프라팀 전달 시 배포 반려를 부를 수 있는 서술 3건(Dockerfile 미빌드 고백, FLUX 비상업 라이선스 미해결 노출, git remote 부재 노출) 및 비격식 구어체 표현 2건 발견. |
