# 상세페이지(page_generation) 문서 전수 조사 — Phase 1~4 분류 초안

## 배경

GenAI 저장소 `page_generation/docs/` 의 문서를 Notion 의 Phase 1~4 구조로 정리하려 한다.
GenAI main(`9de47e7`)의 `page_generation/docs/` 는 **이 저장소의 `docs/` 와 내용이 완전히 같다**
(149개, diff 없음). 그러니 **이 저장소의 `docs/` 를 읽으면 된다.**

Notion 쪽 Phase 정의는 아직 받지 못했다. 받으면 따로 보낸다. 그 전까지는 아래 **임시 정의**로 분류해라.

| Phase | 임시 정의 |
| --- | --- |
| 1 | 기획·요구사항 — 문제 정의, 범위, 초기 설계안 |
| 2 | 설계·데이터 — 아키텍처, 데이터 수집·라이선스·정제, 평가 지표 설계 |
| 3 | 구현·실험 — 구현 체크포인트, 에러 분석, 실험 리포트, 추론 API, BE/FE 인터페이스 |
| 4 | 평가·운영 — AI 기능 평가, 안전성 검증, 모델 카드, 운영·배포 가이드 |

## 할 일 — 읽기 전용

**파일을 하나도 수정하지 마라.** 조사와 분류만 한다.

1. `docs/` 아래 문서 149개를 전부 훑어라. `docs/deliverables/experiments/round-*/` 65개는
   차수별로 묶어서 한 줄씩(13줄)만 적어도 된다
2. 각 문서마다 이 표를 채워라

   | 경로 | 한 줄 요약 | 성격 | 작성일 | 추천 Phase | 근거 |

   - **성격**: `상시`(현재 상태를 설명, 갱신 대상) / `시점`(날짜 붙은 기록, 고치면 안 됨) / `보관`(폐기·대체됨)
   - **작성일**: 문서 본문이나 파일명에 적힌 날짜. 없으면 `git log --follow --format=%ad --date=short -1 -- <파일>` 의 최초 커밋일
   - **추천 Phase**: 1·2·3·4 / `공통`(여러 Phase 에 걸침) / `제외`(Notion 에 올릴 필요 없음 — 예: 오케스트레이션 운영, 리팩터링 진단)
   - **근거**: 왜 그 Phase 인지 한 줄. 날짜만으로 정하지 말고 **내용**으로 정해라
3. 이미 Phase 로 묶인 제출본이 있다 — `docs/deliverables/phase3/`(5종), `docs/deliverables/phase4/`(3종).
   **Phase 1·2 에 해당하는 제출본 묶음은 없다.** Phase 1·2 에 들어갈 만한 원천 문서를 따로 추려라
4. 서로 **겹치거나 모순되는** 문서, **오래돼서 현재와 다른** 상시 문서를 따로 목록으로 적어라. 근거와 함께

## 주의

- 사람 검수 점수는 이 프로젝트에 **존재하지 않는다.** 있는 것처럼 요약하지 마라
- 문서에 없는 내용을 추측으로 채우지 마라. 모르면 `확인 필요`
- 커밋 금지, 파일 수정 금지

## 결과

### 범위와 판정 기준

- `docs/`의 Markdown **149개**를 조사했다. 기타 파일 13개(로그·이미지·JSON·HTML·Excalidraw 등)는 문서 149개 집계에서 제외했다. 아래 표는 비실험 문서 84개를 개별 행으로, 실험 문서 65개를 차수별 13행으로 기록한다. 실험 차수 행의 `{01…05}.md`는 각 폴더의 `01-implementation-checkpoint.md`, `02-error-analysis.md`, `03-experiment-report.md`, `04-inference-api.md`, `05-be-fe-interface.md` 전부를 뜻한다.
- 날짜는 문서의 작성·검수·점검·실행 기준일 또는 파일명에 적힌 날짜를 우선했다. 그런 날짜가 없으면 지시된 `git log --follow --format=%ad --date=short -1 -- <파일>` 결과를 썼다. 따라서 날짜는 일률적인 최초 작성일이 아니며, 특히 `git -1` 값은 해당 경로의 최근 커밋일 수 있다. `상시`는 갱신 대상이라는 성격 분류이며, 아래에서 현행 사실까지 보증한다는 뜻은 아니다.
- 추천 Phase는 이 지시문의 **임시 정의**에 따른다. Notion의 정식 정의를 받으면 경계가 바뀔 수 있다. `제외`는 보관 자체가 불필요하다는 뜻이 아니라 Phase 제출 페이지의 본문으로 옮기지 말라는 추천이다. 사람 검수 **점수는 존재하지 않는다**. 사람 검수 가이드와 당시 육안 판정은 점수로 환산하지 않았다.

### 문서별 분류 — 안내·API·아키텍처·데이터

| 경로 | 한 줄 요약 | 성격 | 작성일 | 추천 Phase | 근거 |
| --- | --- | --- | --- | --- | --- |
| `docs/README.md` | 문서군과 정본·실험·Phase 산출물의 탐색 색인 | 상시 | 2026-09-23 | 공통 | 여러 Phase의 문서를 연결하는 진입점이다. |
| `docs/deliverables-audit.md` | 9월 16일 산출물 충족·미충족 상태 점검 | 시점 | 2026-09-16 | 공통 | 계약·데이터·평가·배포 준비를 함께 점검한 당시 판정이다. |
| `docs/api/ai-dto-contract.md` | BE↔AI 작업·상태·승인·결과 DTO 계약 | 상시 | 2026-09-23 | 3 | 구현 경계의 요청·응답 필드와 상태 전이를 정의한다. |
| `docs/api/ai-fe-io-spec.md` | FE 입력·화면 상태와 BE 경유 AI 호출 명세 | 상시 | 2026-09-17 | 3 | 실제 화면과 연동 입력·오류 표시 계약을 설명한다. |
| `docs/api/ai-product-content-generation-agreement.md` | `/ai/products` 등 이전 계약 폐기 안내 | 보관 | 2026-09-08 | 제외 | 본문이 활성 계약으로 사용하지 말라고 명시한다. |
| `docs/api/ai-worklist-2026-09-17.md` | 9월 17일 AI 팀 수정 항목과 보류 결정 | 시점 | 2026-09-17 | 3 | 연동 결함의 담당과 당시 구현 작업을 나눈 기록이다. |
| `docs/api/be-ai-integration-negotiation.md` | BE↔AI 최초 협의 쟁점과 요청 | 보관 | 2026-09-17 | 제외 | 본문이 BE 인계·AI 목록·합의 문서 3개로 분리됐다고 밝힌다. |
| `docs/api/be-fe-ai-integration-spec.md` | FE→BE→AI 흐름·API·draft·결과·화면 반영 통합 명세 | 상시 | 2026-09-23 | 3 | 서비스 경계와 실제/제안 엔드포인트를 구분하는 구현 계약이다. |
| `docs/api/be-handoff-2026-09-17.md` | BE 코드 수정 요청 BE-1~8 | 시점 | 2026-09-17 | 3 | 첫 연동 실패에 대한 BE 담당 조치 목록이다. |
| `docs/api/be-handoff-2026-09-18.md` | 재연동 후 해결·잔여 BE 요청 | 시점 | 2026-09-18 | 3 | 실제 E2E 재시험 뒤 계약·콜백 쟁점을 기록한다. |
| `docs/api/be-request-2026-09-17.md` | 3자 연동 실패 뒤 원래 BE 요청 전문 | 보관 | 2026-09-17 | 제외 | 본문이 주체별 세 문서로 분리됐다고 명시한 이력본이다. |
| `docs/api/be-request-2026-09-18-e2e.md` | 실제 BE API E2E 이후 승인·ID·첨부 제한 요청 | 시점 | 2026-09-18 | 3 | 테스트로 드러난 인터페이스 차단 항목을 열거한다. |
| `docs/api/open-decisions-2026-09-17.md` | `/ai/products` 의미·이미지 전달·인증·시간 합의 안건 | 시점 | 2026-09-17 | 3 | 당시 미합의 연동 계약을 결정 항목으로 정리한다. |
| `docs/api/react-json-output-contract.md` | 제한형 `react_document` AST와 자산·보안 검증 계약 | 상시 | 2026-09-08 | 3 | FE 전달 산출물의 스키마와 검증·렌더 책임을 정한다. |
| `docs/architecture/ai-architecture-and-safety.md` | 아키텍처·평가·안전성을 합친 통합 기준 | 상시 | 2026-09-16 | 공통 | 목표·설계부터 평가·운영 미검증 항목까지 여러 Phase를 포괄한다. |
| `docs/architecture/ai-architecture-design.md` | 모델·데이터 흐름·서빙·상태·보안 설계 | 상시 | 2026-09-16 | 2 | 구현과 설계의 차이를 밝히며 시스템 구조를 정의한다. |
| `docs/architecture/ai-evaluation-and-safety-policy.md` | 평가 데이터·지표·release gate·안전 정책 초안 | 상시 | 2026-09-08 | 2 | 측정 결과가 아닌 평가 방법과 안전 기준을 설계한다. |
| `docs/data/collection-license-cleaning-plan.md` | CMA 수집·권리 점검·정제·반출 계획 | 상시 | 2026-09-08 | 2 | 데이터 확보와 라이선스·provenance 절차를 설계한다. |

### 문서별 분류 — 제출본·실험 기록

| 경로 | 한 줄 요약 | 성격 | 작성일 | 추천 Phase | 근거 |
| --- | --- | --- | --- | --- | --- |
| `docs/deliverables/01-implementation-checkpoint.md` | 분석·카피 및 이미지·렌더링 1차 구현 점검 | 시점 | 2026-09-09 | 3 | 파일럿 6건 기반 구현 상태와 한계를 기록한다. |
| `docs/deliverables/02-error-analysis.md` | 파일럿·다양성 작업의 주요 장애 11건 분석 | 시점 | 2026-09-09 | 3 | 증상·원인·조치·재발 방지를 사건별로 남긴다. |
| `docs/deliverables/03-second-experiment-report.md` | 컷아웃·씬·파라미터·1~12차 실험 색인 | 시점 | 2026-09-17 | 3 | 가설과 실제 재실행 결과를 비교한 실험 보고서다. |
| `docs/deliverables/04-inference-api.md` | 9월 10일 코드 기준 서비스·MLX 추론 API | 시점 | 2026-09-10 | 3 | 당시 구현의 모델 호출·엔드포인트를 설명한다. |
| `docs/deliverables/05-be-fe-interface.md` | BE/FE 통합 명세 정본으로 가는 짧은 참조 | 상시 | 2026-09-17 | 3 | 제출 항목 ⑤의 정본 경로를 지정하는 스텁이다. |
| `docs/deliverables/experiments/round-01/{01…05}.md` (5개) | validation 블록 패딩 제거 실험과 API·인터페이스 영향 | 시점 | 2026-09-10 | 3 | 구현 변경·오류·Jaccard 재측정 및 계약 유지 기록이다. |
| `docs/deliverables/experiments/round-02/{01…05}.md` (5개) | 프롬프트 순서 신호 제거 실험 | 시점 | 2026-09-10 | 3 | 구조 반복 감소를 측정하고 잔여 수렴을 기록한다. |
| `docs/deliverables/experiments/round-03/{01…05}.md` (5개) | 블록별 근거·생략 조건 도입 실험 | 시점 | 2026-09-10 | 3 | 근거 없는 `statement` 등 차단 효과를 측정한다. |
| `docs/deliverables/experiments/round-04/{01…05}.md` (5개) | 레이아웃 원형 예시 주입 실험 | 시점 | 2026-09-10 | 3 | 순서 분산과 집합 다양성 악화를 함께 기록한다. |
| `docs/deliverables/experiments/round-05/{01…05}.md` (5개) | 코드가 원형을 정하고 모델이 카피를 쓰는 실험 | 시점 | 2026-09-10 | 3 | 해시 선택의 개선치와 충돌 한계를 기록한다. |
| `docs/deliverables/experiments/round-06/{01…05}.md` (5개) | variant 강제 배정 해제·CSS 4종 구현 | 시점 | 2026-09-10 | 3 | DTO 값이 화면에 반영되는지와 스타일 편중을 점검한다. |
| `docs/deliverables/experiments/round-07/{01…05}.md` (5개) | 원형 variant를 프롬프트로 전달 | 시점 | 2026-09-10 | 3 | 추론 지시 변경과 실패한 실행 옵션을 기록한다. |
| `docs/deliverables/experiments/round-08/{01…05}.md` (5개) | 카탈로그 빈도와 다양성 합격 기준 수정 | 시점 | 2026-09-10 | 3 | 달성 불가능한 기존 기준을 시뮬레이션으로 바로잡는다. |
| `docs/deliverables/experiments/round-09/{01…05}.md` (5개) | 상품 근거로 원형 후보를 선택하는 실험 | 시점 | 2026-09-10 | 3 | 후보 4종·모델 선택의 구조 효과와 라벨 결함을 기록한다. |
| `docs/deliverables/experiments/round-10/{01…05}.md` (5개) | 당시 생성컷 라벨 계약 수정과 60건 1차 실행 | 시점 | 2026-09-11 | 3 | 60건 실행·라벨 검증·컷아웃 지표를 측정한 구현 실험이다. |
| `docs/deliverables/experiments/round-11/{01…05}.md` (5개) | 컷아웃 게이트 감사 채택·추출기 수정 되돌림 | 시점 | 2026-09-11 | 3 | 51/60 폴백을 드러낸 검증 결함과 반려 이력을 남긴다. |
| `docs/deliverables/experiments/round-12/{01…05}.md` (5개) | hero 원본 고정·rembg 채택·화면 라벨 제거 | 시점 | 2026-09-14 | 3 | 합성 시도 반려와 `source_original` 계약 변화를 기록한다. |
| `docs/deliverables/experiments/round-13/{01…05}.md` (5개) | 생성컷 자리 확보·다양성 기준선 정정 | 시점 | 2026-09-18 | 3 | 후보 원형·`usage_scene` 사용과 측정 기준 수정을 검증한다. |
| `docs/deliverables/phase3/01-implementation-checkpoint.md` | 1차 구현 체크포인트의 Phase 3 제출 복사본 | 시점 | 2026-09-09 | 3 | 제출용 5종 중 구현 증거다. |
| `docs/deliverables/phase3/02-error-analysis.md` | 장애 11건 분석의 Phase 3 제출 복사본 | 시점 | 2026-09-09 | 3 | 제출용 원인·조치 기록이다. |
| `docs/deliverables/phase3/03-second-experiment-report.md` | 2차 실험·차수 색인의 Phase 3 제출 복사본 | 시점 | 2026-09-17 | 3 | 제출용 실험 비교표다. |
| `docs/deliverables/phase3/04-inference-api.md` | 당시 MLX 추론 API의 Phase 3 제출 복사본 | 시점 | 2026-09-10 | 3 | 제출용 구현 API 기록이다. |
| `docs/deliverables/phase3/05-be-fe-interface.md` | 스텁 뒤에 통합 BE/FE 명세를 실은 제출본 | 시점 | 2026-09-17 | 3 | 제출용 인터페이스 전문이며 원본 스텁보다 길다. |
| `docs/deliverables/phase3/README.md` | Phase 3 제출 5종 색인·원본 연결 | 상시 | 2026-09-17 | 3 | 제출본의 구조와 출처를 설명한다. |
| `docs/deliverables/phase4/01-ai-evaluation-report.md` | 자동 평가·정성 관찰·비교표의 기능 평가 보고 | 시점 | 2026-09-22 | 4 | 측정치와 한계를 제시하며 사람 점수가 없음을 명시한다. |
| `docs/deliverables/phase4/02-ai-safety-report.md` | 9월 21일 안전성 검증의 제출 복사본 | 시점 | 2026-09-21 | 4 | 환각·주입·편향의 실측 판정이다. |
| `docs/deliverables/phase4/03-model-card-and-operations.md` | 모델 카드와 배포·운영 가이드 | 시점 | 2026-09-22 | 4 | 모델 출처·제약·운영 절차를 제출형으로 정리한다. |
| `docs/deliverables/phase4/README.md` | Phase 4 제출 3종 색인과 9월 23일 후속 사실 | 상시 | 2026-09-23 | 4 | 제출본 해석·미검증 항목·새 평가 결과를 안내한다. |

### 문서별 분류 — 평가·검증

| 경로 | 한 줄 요약 | 성격 | 작성일 | 추천 Phase | 근거 |
| --- | --- | --- | --- | --- | --- |
| `docs/evaluation/ai-review-2026-09-10.md` | AI 참고 검수와 당시 미수정 결함 | 시점 | 2026-09-10 | 4 | AI 점수는 참고치이고 공식 사람 점수가 아니라고 명시한다. |
| `docs/evaluation/ai-safety-report-2026-09-21.md` | 105건 안전성 검증: 환각 미흡·주입/편향 통과 | 시점 | 2026-09-21 | 4 | 실제 공격·편향·환각 실험의 방법과 판정을 담는다. |
| `docs/evaluation/be-ai-integration-test-2026-09-21.md` | BE↔AI 재연동: 요청 연결, 콜백·렌더 한계 | 시점 | 2026-09-21 | 3 | BE와 AI의 실제 상태 전이·실패 지점을 검증한다. |
| `docs/evaluation/be-integration-test-2026-09-17.md` | BE 양방향 호출 1·2차 실패 기록 | 시점 | 2026-09-17 | 3 | 당시 HTTP 계약 불일치와 실행 결과를 남긴다. |
| `docs/evaluation/celadon-run-2026-09-23.md` | 청자 찻잔에서 생성컷 미사용 재현 | 시점 | 2026-09-23 | 4 | 실제 산출물의 생성 사진 사용 여부를 평가한다. |
| `docs/evaluation/container-integration-test-2026-09-17.md` | 컨테이너 BE 연동·`@Async` 문제 확인 | 시점 | 2026-09-17 | 3 | 컨테이너 환경의 구현 연동 결함을 검증한다. |
| `docs/evaluation/copy-analysis-2026-09-09.md` | 6건 카피의 사실성·문구 문제와 프롬프트 후보 | 시점 | 2026-09-09 | 4 | 파일럿 산출물의 내용 품질을 분석하며 점수화하지 않는다. |
| `docs/evaluation/cutout-ground-truth.md` | 냉동 60건의 침식·배경 잔존 정답 집합 | 시점 | 2026-09-11 | 4 | 특정 산출물에 대한 독립 품질 감사다. |
| `docs/evaluation/cutout-regression-baseline.md` | 컷아웃 9건 성공·51건 폴백 회귀 기준 | 시점 | 2026-09-11 | 4 | 추출·거부·침식 지표의 당시 기준선을 제시한다. |
| `docs/evaluation/deliverables-review-2026-09-16.md` | 산출물 치명·불일치·사소 항목 최종 판정 | 시점 | 2026-09-16 | 공통 | 계약·운영·실험 산출물을 가로질러 검수한다. |
| `docs/evaluation/full60-runs.md` | 60건 두 실행의 보존·되돌림 근거 | 시점 | 2026-09-11 | 4 | 동일 입력의 컷아웃 결과와 게이트 판정을 비교한다. |
| `docs/evaluation/generated-photo-usage-2026-09-23.md` | 합죽선 2회에서 생성컷 사용·PNG/AST 불일치 관찰 | 시점 | 2026-09-23 | 4 | 새 상품의 실제 출력에서 생성컷 사용 실패를 측정한다. |
| `docs/evaluation/human-review-guide.md` | 사람 검수 4축·절차·배포 차단 기준 초안 | 상시 | 2026-09-09 | 2 | 평가 방법의 설계 문서이며 채점 결과가 아니다. |
| `docs/evaluation/logs/README.md` | 9월 17일 3자 연동 원시 로그 색인 | 시점 | 2026-09-17 | 3 | BE·챗봇·상세페이지 호출 증거 파일을 안내한다. |
| `docs/evaluation/metrics-definition.md` | 분석·렌더링 자동 지표와 사람 검수 통계 정의 | 상시 | 2026-09-09 | 2 | 측정값이 아닌 평가 분모·판정법을 정의한다. |
| `docs/evaluation/pilot-report-2026-09-09.md` | 6건 첫 파일럿과 컷아웃 소실 결함 | 시점 | 2026-09-09 | 4 | 실행 결과와 자동 게이트 한계를 기록한다. |
| `docs/evaluation/pipeline-run-2026-09-17.md` | 제공 사진 우선 배정 포함 파이프라인 종단 실행 | 시점 | 2026-09-17 | 3 | BE 유사 입력으로 구현 흐름을 실행 확인했다. |
| `docs/evaluation/reintegration-test-2026-09-18.md` | BE 대응 뒤 최초 전 구간 연결과 수동 콜백 | 시점 | 2026-09-18 | 3 | 연동 회귀 결과와 남은 콜백 문제를 기록한다. |
| `docs/evaluation/three-service-integration-test-2026-09-17.md` | BE·챗봇·상세페이지 3자 연결 실패 원인 | 시점 | 2026-09-17 | 3 | HTTP 본문 미전달 등 실제 통합 결함을 재현한다. |

### 문서별 분류 — 운영·전달

| 경로 | 한 줄 요약 | 성격 | 작성일 | 추천 Phase | 근거 |
| --- | --- | --- | --- | --- | --- |
| `docs/operations/aws-deploy-inventory.md` | AWS 반입 이미지·가중치·PVC·시크릿 목록 | 상시 | 2026-09-17 | 4 | 배포 준비물과 검증 상태를 관리한다. |
| `docs/operations/aws-deployment.md` | AWS 이관 경로·GPU 제약·품질 게이트 가이드 | 상시 | 2026-09-10 | 4 | 운영 환경의 배포·검증 절차와 미검증 항목을 설명한다. |
| `docs/operations/aws-migration-checklist.md` | AWS 이전의 단계·의존성·확인 명령 | 상시 | 2026-09-10 | 4 | 실제 인프라 이관을 위한 작업 순서다. |
| `docs/operations/be-handoff-2026-09-18b.md` | BE 회신: status 스키마·콜백·승인 결정 | 시점 | 2026-09-18 | 3 | 당시 BE↔AI 인터페이스 쟁점을 전달한다. |
| `docs/operations/be-handoff-2026-09-21.md` | BE 연결 성공 뒤 S3 콜백·설정 오류 요청 | 시점 | 2026-09-21 | 3 | 연동 시험에서 남은 BE 계약 문제를 전달한다. |
| `docs/operations/be-handoff-2026-09-22.md` | BE-11 승인·콜백 시점의 A/B/C 결정 요청 | 시점 | 2026-09-22 | 3 | draft와 완료 상태의 주체·타이밍 합의를 요구한다. |
| `docs/operations/ecr-review-2026-09-17.md` | ECR 이미지 네이밍·CI 차단 항목 회신 | 시점 | 2026-09-17 | 4 | 인프라 배포 준비에 대한 당시 검토 의견이다. |
| `docs/operations/eks-workload-spec.md` | EKS 컨테이너·자원·헬스·시크릿 요구사항 | 상시 | 2026-09-16 | 4 | 인프라팀의 배포 워크로드 입력 사양이다. |
| `docs/operations/infra-handoff-2026-09-21.md` | Actions/ECR 푸시 실패와 러너·OIDC 원인 | 시점 | 2026-09-21 | 4 | 배포 파이프라인의 실측 실패를 전달한다. |
| `docs/operations/infra-handoff-2026-09-22.md` | CodeBuild·모델 업로드·GPU 공동 검증 요청 | 시점 | 2026-09-22 | 4 | 이미지 발행·권한·모델 준비의 당시 상태를 기록한다. |
| `docs/operations/infra-handoff-2026-09-23.md` | 모델 3종 S3 업로드·해시·라이선스 회신 | 시점 | 2026-09-23 | 4 | 운영 모델 자산의 전달·검증 증거다. |
| `docs/operations/infra-handoff-2026-09-23b.md` | Stage EKS 기동 오류와 동시 로딩 문제 회신 | 시점 | 2026-09-23 | 4 | 실제 배포 시도에서 확인한 장애를 기록한다. |
| `docs/operations/local-generation-test-report.md` | 9월 7일 로컬 smoke test 실행·한계 | 시점 | 2026-09-08 | 3 | 로컬 구현 경로의 엔드포인트 동작 기록이다. |
| `docs/operations/local-llm.md` | Mac MLX 모델 경로·실행법·생성 정책 | 상시 | 2026-09-17 | 4 | 개발 환경의 모델 서빙 운영 가이드다. |
| `docs/operations/orchestration.md` | cmux 다중 에이전트 작업·인계 규약 | 상시 | 2026-09-10 | 제외 | 제품 Phase가 아니라 저장소 작업 운영 절차다. |
| `docs/operations/server-memory-estimate.md` | Apple Silicon 로컬 통합 메모리 추정 | 상시 | 2026-09-08 | 4 | 로컬 서빙 장비의 자원 계획이다. |
| `docs/operations/sglang-serving-research.md` | 서버 Qwen/FLUX 가중치·라이선스·공존 조사 | 시점 | 2026-09-14 | 4 | 배포 모델 선택의 조사 근거와 미실측 가정이다. |
| `docs/operations/sglang-vllm-fit.md` | SGLang 확정 전 MLX 서빙 검토 | 보관 | 2026-09-08 | 제외 | 본문이 현행 서버 운영 기준이 아니라고 표시한다. |
| `docs/operations/ubuntu-deployment.md` | Ubuntu 단일 GPU의 3서비스 Compose 배포법 | 상시 | 2026-09-17 | 4 | 추론 서버 기동·환경값·검증 절차를 안내한다. |

### 문서별 분류 — 내부 진단·참고·설계 이력

| 경로 | 한 줄 요약 | 성격 | 작성일 | 추천 Phase | 근거 |
| --- | --- | --- | --- | --- | --- |
| `docs/refactoring/cleanup-diagnosis-agy.md` | 코드 정리 교차 진단 B의 필요·불필요 항목 | 시점 | 2026-09-14 | 제외 | 내부 코드 청소 판단이며 제품 Phase 제출물이 아니다. |
| `docs/refactoring/cleanup-diagnosis-codex.md` | 코드 정리 교차 진단 A와 실행 목록 | 시점 | 2026-09-14 | 제외 | 내부 유지보수 진단이다. |
| `docs/refactoring/diagnosis-agy.md` | 책임 혼재·순환 의존 등 구조 진단 B | 시점 | 2026-09-10 | 제외 | 리팩터링 전제의 당시 코드 감사다. |
| `docs/refactoring/diagnosis-codex.md` | 파이프라인 책임·사진 정책 경계 진단 A | 시점 | 2026-09-11 | 제외 | 내부 구조 개선 제안이다. |
| `docs/refactoring/refactoring-plan.md` | 구조 리팩터링 계획 및 9월 14일 실행 보류 | 보관 | 2026-09-14 | 제외 | 본문이 전체 실행 보류와 전제 무효화를 명시한다. |
| `docs/references/product-photography.md` | 촬영 구도·조명·컷 유형의 일반 참고 자료 | 보관 | 2026-09-08 | 제외 | `inference.sh` 예시는 현재 서비스 운영 호출 경로가 아니다. |
| `docs/superpowers/plans/2026-08-26-image-detail-page-ai-fe-be.md` | 제품 전체 이미지 생성 중심의 첫 구현안 | 보관 | 2026-08-26 | 제외 | 원본 보존 설계가 이를 대체했다고 문서에 명시한다. |
| `docs/superpowers/plans/2026-08-27-source-preserving-detail-page-implementation.md` | 원본 보존형 파이프라인 구현 계획 이력 | 시점 | 2026-08-27 | 제외 | Bedrock 등 당시 구현 단계의 작업 지시이며 현행 계약은 별도 정본이다. |
| `docs/superpowers/plans/2026-08-31-detail-page-flow-hardening.md` | draft→PNG 흐름 개선 구현 계획 이력 | 시점 | 2026-08-31 | 제외 | 당시 HTML draft 표현·provider 가정을 회고 메모가 정정한다. |
| `docs/superpowers/plans/2026-08-31-fe-be-ai-be-fe-implementation.md` | BE 게이트웨이·multipart·상태 계약 구현 계획 | 시점 | 2026-08-31 | 제외 | 실행 순서를 위한 내부 계획이며 현행 계약은 API 문서다. |
| `docs/superpowers/plans/2026-09-10-round-01-05-documentation.md` | 1~5차 5종 문서화·색인 복원 계획 | 시점 | 2026-09-10 | 제외 | 문서 정리 작업 계획이지 제품 산출물 내용은 아니다. |
| `docs/superpowers/specs/2026-08-26-image-driven-detail-page-design.md` | 최종 이미지를 통째로 생성하는 최초 설계 | 보관 | 2026-08-26 | 제외 | 8월 27일 원본 보존형 설계로 대체됐다고 밝힌다. |
| `docs/superpowers/specs/2026-08-27-source-preserving-detail-page-design.md` | 원본 보존 목표·성공 기준·데이터 흐름·컴포넌트 설계 | 상시 | 2026-08-27 | 공통 | 1절·2절은 Phase 1 범위, 3~7절은 Phase 2 설계의 원천이다. |

### Phase 1·2 제출본을 만들 때 쓸 원천

`docs/deliverables/phase3/`에는 제출본 5종, `docs/deliverables/phase4/`에는 제출본 3종이 있으나 **Phase 1·2 제출본 폴더나 해당 이름의 묶음은 없다**. 따라서 아래는 제출본이 아니라 원천 문서다.

| 추천 | 원천 문서와 사용할 부분 | 이유·주의 |
| --- | --- | --- |
| Phase 1 | `docs/superpowers/specs/2026-08-27-source-preserving-detail-page-design.md` 1·2·14절 | 원본 제품을 보존해야 하는 목적, 성공 기준, 범위 경계를 직접 기술한다. 본문에 남은 당시 Bedrock·Gemma 예시는 현행 구현으로 옮기지 말고 최신 계약과 대조해야 한다. |
| Phase 1 | `docs/architecture/ai-architecture-and-safety.md` 1·2절; `docs/architecture/ai-architecture-design.md` 1·3절 | 제품 원본 보존·근거 분리·승인 전후 구분 및 목표/비목표를 Phase 1 기획 서술로 추릴 수 있다. 두 문서의 중복 진술을 합쳐 하나의 범위로 정리해야 한다. |
| Phase 2 | `docs/architecture/ai-architecture-design.md` 4~10절; `docs/architecture/ai-architecture-and-safety.md` 3~8절 | 컴포넌트·모델·데이터 흐름·상태·서빙·안전 설계의 중심 자료다. 후자는 평가·안전까지 걸치므로 중복을 정리해야 한다. |
| Phase 2 | `docs/data/collection-license-cleaning-plan.md` | 수집 단위·권리 점검대장·정제·반출 조건을 직접 제공한다. 권리 최종 승인 사실은 이 문서에 없다. |
| Phase 2 | `docs/evaluation/metrics-definition.md`; `docs/architecture/ai-evaluation-and-safety-policy.md`; `docs/evaluation/human-review-guide.md` | 지표 분모·골든셋·사람 검수 절차·안전 게이트의 설계 원천이다. 가이드가 있다고 점수가 존재하는 것은 아니다. 아래의 오래된 실행 상태 문구는 갱신 또는 시점 주석이 필요하다. |

8월 26일의 `docs/superpowers/specs/2026-08-26-image-driven-detail-page-design.md`와 짝 구현 계획은 **폐기된 초기안**이라 현행 Phase 1·2 본문에는 추천하지 않는다. 변경 배경을 설명할 때만 이력 출처로 쓸 수 있다. Phase 1의 문제 정의가 더 필요하다면 별도 근거 확인이 필요하며, 현 문서에 없는 요구사항은 `확인 필요`로 남겨야 한다.

### 중복·모순·현재와 다른 문서

| 문서 | 관찰·근거 | 정리할 때의 처리 |
| --- | --- | --- |
| `docs/deliverables/01…04` ↔ `docs/deliverables/phase3/01…04`; `docs/deliverables/05-be-fe-interface.md` ↔ `docs/deliverables/phase3/05-be-fe-interface.md` ↔ `docs/api/be-fe-ai-integration-spec.md` | Phase 3의 01~04는 원본 내용의 제출 복사본이다. 05는 원본이 9줄 참조 스텁이고 Phase 3 파일은 BE/FE 통합 명세 전문까지 실어 620줄이다. Phase 3 README의 “원본을 그대로 옮긴 복사본” 설명은 05의 형태를 충분히 설명하지 않는다. API 정본은 별도 파일이다. | Phase 3에서는 제출본 5종을 사용하고, 실시간 계약 변경은 API 정본에서 확인한다. 같은 내용을 중복 페이지로 게시하지 않는다. |
| `docs/evaluation/ai-safety-report-2026-09-21.md` ↔ `docs/deliverables/phase4/02-ai-safety-report.md` | 후자는 전자의 제출 복사본으로, 상단에서도 링크 보정 외 내용 동일이라고 설명한다. | Phase 4에는 제출본을 한 번만 싣고 원자료 링크를 둔다. |
| `docs/api/be-ai-integration-negotiation.md`, `docs/api/be-request-2026-09-17.md` ↔ `docs/api/be-handoff-2026-09-17.md`, `docs/api/ai-worklist-2026-09-17.md`, `docs/api/open-decisions-2026-09-17.md` | 앞의 두 문서는 스스로 뒤의 주체별 3문서로 분리됐다고 밝힌다. | 앞의 두 문서는 당시 협의 이력으로만 연결하고 담당별 목록은 분리본을 읽는다. |
| `docs/architecture/ai-architecture-and-safety.md` ↔ `docs/architecture/ai-architecture-design.md` ↔ `docs/architecture/ai-evaluation-and-safety-policy.md` ↔ `docs/evaluation/metrics-definition.md` | 통합 기준·세부 설계·평가 정책 초안·지표 정의가 목표와 안전·평가 설명을 중복한다. 통합 기준은 세부 아키텍처를 설계 문서로, 지표 계산은 지표 정의서로 넘긴다고 명시한다. | Phase 2 합본에서는 역할별로 출처를 정하고 같은 기준을 두 번 적지 않는다. |
| `docs/deliverables/experiments/round-10/` ↔ `round-12/`; `docs/evaluation/ai-review-2026-09-10.md` | 10차는 생성 컷의 화면 `참고용` 라벨을 추가·검증했으나 12차 관리자 결정으로 화면 표시와 게이트를 제거했다. 9월 10일 AI 참고 검수와 Phase 3 오류 분석에는 당시 “라벨 누락” 결함이 남아 있다. | 기록은 고치지 않는다. 현행 표현은 `product_generated`·provenance 구분이며, 과거 라벨 결함을 현재 배포 차단으로 옮기지 않는다. |
| `docs/deliverables/phase4/01-ai-evaluation-report.md` 3-4절 ↔ `docs/deliverables/phase4/README.md`의 9월 23일 추가 ↔ `docs/evaluation/generated-photo-usage-2026-09-23.md`·`celadon-run-2026-09-23.md` | 13차의 한 실행에서는 생성컷 사용이 0장에서 5장으로 늘었지만 다른 두 품목에서는 생성컷 5장이 다시 미사용됐다. Phase 4 README가 이 일반화 한계를 명시하며, 이후 갤러리 사진을 코드가 정하도록 한 수정을 기록한다. | “13차가 모든 상품의 생성컷 사용을 해결했다”라고 요약하지 않는다. 실험 대상과 후속 결과를 함께 쓴다. |
| `docs/superpowers/specs/2026-08-26-…`·`plans/2026-08-26-…` ↔ 8월 27일 원본 보존 설계·계획 | 최초안은 제품 전체 이미지 생성과 Gemini/Bedrock 경로를 가정한다. 두 파일 모두 8월 27일 원본 보존 설계로 대체됐다고 명시한다. | 초기안은 보관 이력으로만 다룬다. |
| `docs/operations/sglang-vllm-fit.md` ↔ `docs/operations/ubuntu-deployment.md`·`sglang-serving-research.md` | 전자는 SGLang 확정 전 로컬 MLX 검토이며 본문이 현재 서버 운영 기준이 아니라고 명시한다. 후자는 SGLang 서버 구성·모델을 설명한다. | 서버 운영 절차에 옛 MLX 검토 결론을 섞지 않는다. |
| `docs/deliverables/04-inference-api.md`·Phase 3 복사본 ↔ 현행 운영 가이드 | 제출본은 9월 10일 MLX Serve 코드 대조를 다루고, 운영 가이드는 서버 SGLang 추론을 다룬다. 환경·시점이 다르다. | MLX 기록을 서버 운영의 현행 추론 API라고 소개하지 않는다. |

**갱신이 필요한 상시 문서:**

| 문서 | 오래된 진술과 대조 증거 |
| --- | --- |
| `docs/evaluation/metrics-definition.md` 1절·5절 | “60건 전체 평가 미실행”, “실제 Gemma/Flux 실행 필요”가 남아 있다. `docs/deliverables/experiments/round-10/`은 60건 실행을 기록하고 Phase 4 평가 보고서는 후속 60건 실측을 제시한다. 지표 **정의**와 실행 **현황**을 분리해 갱신해야 한다. |
| `docs/architecture/ai-evaluation-and-safety-policy.md` 데이터셋 현황표; `docs/architecture/ai-architecture-and-safety.md` 평가 데이터셋 절 | `cma_real_v1` 모델 실행 대기라고 쓰여 있지만 10차 60건 실행과 Phase 4 평가가 뒤따랐다. 권리 최종 확인·사람 라벨/점수 대기와 모델 실행 완료는 각각 다른 상태이므로 구분해야 한다. |
| `docs/operations/ubuntu-deployment.md` 상단 검증 상태 | “이미지도 아직 빌드하지 않았다”는 문구가 남아 있다. `docs/operations/eks-workload-spec.md`는 9월 18일 amd64 이미지 빌드 실측을, `docs/operations/infra-handoff-2026-09-23b.md`는 Stage EKS 기동 오류를 기록한다. 빌드·기동 시도·GPU 완주 여부를 각각 갱신해야 한다. |
| `docs/operations/aws-deployment.md` EKS 전환/검증 상태 | Compose를 확정 운영 경로로, EKS를 미결정 설계안으로 설명한다. 9월 23일 인프라 회신에는 Stage EKS 실기동 오류가 있다. 실제 Stage 시도와 운영 채택 여부는 별도로 확인해 현황을 갱신해야 한다. GPU 추론 **성공**은 그 회신에서도 확인되지 않는다. |
| `docs/superpowers/specs/2026-08-27-source-preserving-detail-page-design.md` 상단 구현 메모 | 여전히 “현재 실행 경로는 로컬 Gemma + Flux2 MLX Serve”라고 쓰지만 `docs/operations/local-llm.md`와 `docs/README.md`는 로컬 기본 분석 모델을 Qwen3.8-27B라고 명시한다. Phase 1·2로 옮길 때 모델 현황을 그대로 복제하지 않아야 한다. |

그 밖에 날짜가 붙은 연동 요청·시험·차수 보고서의 불일치(예: 9월 17일 “연결 불가”와 9월 18일 “수동 콜백까지 연결”)는 같은 시점의 모순이 아니라 **시간이 흐르며 바뀐 실행 결과**다. 원문을 수정하지 않고 날짜와 대상 커밋을 함께 표기해야 한다. 현행 BE 승인·콜백 결정의 최종 합의 여부는 이 문서군만으로 `확인 필요`다.
