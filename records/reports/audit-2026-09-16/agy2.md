# 5종 산출물·차수 기록 감사 보고서

- 감사일: 2026-09-16
- 범위: 상위 산출물 5개, `round-01`~`round-12`의 Markdown 60개, `docs/evaluation/*.md` 8개, `docs/deliverables-audit.md`, `docs/README.md`
- 방법: 60개 차수 로그를 전부 열어 헤더·문장·수치를 대조하고, 색인 및 감사 문서의 상태를 후속 산출물·코드 경로와 교차 확인했다.
- 심각도: `치명`은 사실이 아닌 내용, `불일치`는 문서 간 값/정의 차이, `사소`는 기록 형식 또는 추적성 문제다.

## 검증 결과 — 이상 없음

- [확인] **차수별 문서 완전성**: `docs/deliverables/experiments/round-01`~`round-12`에 각 `01`~`05` 문서가 모두 있어 12×5=60개다. 예: `docs/deliverables/experiments/round-01/01-implementation-checkpoint.md:1`, `docs/deliverables/experiments/round-12/05-be-fe-interface.md:1`. 누락 목록은 없다.
- [확인] **차수 로그 헤더**: 60개 모두 `차수`, `파일럿 디렉터리`, `이미지 재생성`, `기록 시각` 4요소를 갖는다. 예: `docs/deliverables/experiments/round-01/01-implementation-checkpoint.md:3`, `docs/deliverables/experiments/round-01/01-implementation-checkpoint.md:5`, `docs/deliverables/experiments/round-01/01-implementation-checkpoint.md:6`, `docs/deliverables/experiments/round-01/01-implementation-checkpoint.md:8`; 최신 로그도 `docs/deliverables/experiments/round-12/05-be-fe-interface.md:3`, `docs/deliverables/experiments/round-12/05-be-fe-interface.md:5`, `docs/deliverables/experiments/round-12/05-be-fe-interface.md:6`, `docs/deliverables/experiments/round-12/05-be-fe-interface.md:8`에 있다. 빠진 차수 로그는 없다.
- [확인] **색인 행 수와 차수 수치**: `docs/deliverables/03-second-experiment-report.md:132`~`:143`에 1~12차가 모두 있다. 1~9차의 Jaccard·유효 공통·완전 일치 값은 각 차수 실험 리포트와 일치하고, 10차·11차도 각 리포트의 52.3%·0종·0쌍과 일치한다(`docs/deliverables/experiments/round-10/03-experiment-report.md:48`, `docs/deliverables/experiments/round-11/03-experiment-report.md:62`). 12차의 `확인 필요` 5개 지표도 해당 차수 문서의 기록과 같다(`docs/deliverables/experiments/round-12/03-experiment-report.md:121`).
- [확인] **사람 검수 가이드**: `human-review-guide.md`는 1~5점의 평가 기준과 절차만 담고 실제 케이스 점수를 담지 않는다(`docs/evaluation/human-review-guide.md:23`, `docs/evaluation/human-review-guide.md:178`). 이는 가이드 문서로서 이상 없음.
- [확인] **AI 수치의 라벨링**: AI 2개 모델의 4·5점 값은 공식 사람 점수가 아닌 AI 참고치라고 명시되어 있다(`docs/evaluation/ai-review-2026-09-10.md:7`, `docs/evaluation/ai-review-2026-09-10.md:20`, `docs/evaluation/ai-review-2026-09-10.md:23`). 이를 사람 평가 점수로 세지 않았다.

## 발견 사항

### 발견 1 — [사소] 권고·향후 계획 문장이 차수 로그에 남아 있음

프로젝트 규칙은 차수 문서를 과거형 사실 로그로만 작성하고 권고·향후 계획을 넣지 않도록 한다. 다음 10개 로그에는 규칙 위반 문장이 확인됐다.

- `docs/deliverables/experiments/round-02/02-error-analysis.md:31` — 다음 차수에서 별도 처리하도록 남겼다는 향후 계획.
- `docs/deliverables/experiments/round-06/02-error-analysis.md:25` — Round 07에서 경로를 개방하기로 결정했다는 계획.
- `docs/deliverables/experiments/round-06/04-inference-api.md:27`, `docs/deliverables/experiments/round-06/04-inference-api.md:28` — `차기 개선 필요 사항`, 계약을 확장해야 한다는 권고.
- `docs/deliverables/experiments/round-07/02-error-analysis.md:44` — 자동 truncate 로직 검토가 필요하다는 권고.
- `docs/deliverables/experiments/round-07/03-experiment-report.md:66` — 카탈로그와 알고리즘을 손보아야 한다는 권고.
- `docs/deliverables/experiments/round-08/02-error-analysis.md:27`, `docs/deliverables/experiments/round-08/02-error-analysis.md:45`, `docs/deliverables/experiments/round-08/02-error-analysis.md:48` — 사전 시뮬레이션 필요, 9차 전환 결정, 회피하지 말아야 한다는 문장.
- `docs/deliverables/experiments/round-08/03-experiment-report.md:46` — AI 생성물 판정이 아님에 유의해야 한다는 지시형 문장.
- `docs/deliverables/experiments/round-09/02-error-analysis.md:29` — 계약 테스트를 보강해야 한다는 재발 방지 권고.
- `docs/deliverables/experiments/round-11/02-error-analysis.md:32`, `docs/deliverables/experiments/round-11/02-error-analysis.md:55`, `docs/deliverables/experiments/round-11/02-error-analysis.md:78`, `docs/deliverables/experiments/round-11/02-error-analysis.md:117`, `docs/deliverables/experiments/round-11/02-error-analysis.md:148` — 게이트·병목·목적함수·잔여 오탐·추가 규명에 대한 의무/권고.
- `docs/deliverables/experiments/round-11/03-experiment-report.md:99` — 관리자의 판단 근거를 수집·분석해야 한다는 후속 조치.

가설의 조건문과 단순한 `확인 필요` 상태 표기는 향후 작업 지시로 세지 않았고, 위의 명시적 권고·계획만 발견 건으로 집계했다.

### 발견 2 — [치명] 1~9차 컷아웃 `6/6 OK` 기록이 후속 전수 조사와 충돌함

- [확인] 초기 로그들은 컷아웃 게이트를 전건 정상으로 기록했다. 예를 들어 `docs/deliverables/experiments/round-01/03-experiment-report.md:42`와 `docs/deliverables/experiments/round-09/03-experiment-report.md:48`은 각각 `OK 6건, 부분 손실 0, 심각 손실 0`으로 적었다.
- [확인] 실제 1차 파일럿 산출물 조사에서는 `textile` 보존율 26.2%와 `ceramic` 보존율 3.2%가 측정됐다(`docs/evaluation/pilot-report-2026-09-09.md:76`, `docs/evaluation/pilot-report-2026-09-09.md:79`).
- [확인] 후속 전수 조사도 1~9차 보고서의 `컷아웃 6/6 OK`가 폴백을 정상 작업으로 오인한 허위 통과였다고 명시한다(`docs/deliverables/experiments/round-11/02-error-analysis.md:20`, `docs/deliverables/experiments/round-11/02-error-analysis.md:22`, `docs/deliverables/experiments/round-11/02-error-analysis.md:23`, `docs/deliverables/experiments/round-11/02-error-analysis.md:26`).

이는 과거 게이트 버전의 실행 결과라는 시간 맥락은 있으나, 로그가 `OK`를 실제 컷아웃 성공·제품 보존으로 설명한 점은 후속 ground truth와 양립하지 않는다.

### 발견 3 — [불일치] 같은 60건 1차 실행의 컷아웃 게이트 값이 55·3으로 다름

- `docs/deliverables/experiments/round-10/03-experiment-report.md:53`은 `OK 55건 / 부분 손실 5건`으로 기록한다.
- 같은 `generated/evaluation/full60-20260910-204433` 실행을 보존한 문서는 `게이트 OK 3`, 부분 손실 4, 배경 잔존 2로 적는다(`docs/evaluation/full60-runs.md:12`, `docs/evaluation/full60-runs.md:23`, `docs/evaluation/full60-runs.md:25`, `docs/evaluation/full60-runs.md:26`, `docs/evaluation/full60-runs.md:28`).
- Round 11의 비교표는 1차를 구 게이트 55건, 2차를 새 게이트 13건으로 구분한다(`docs/deliverables/experiments/round-11/03-experiment-report.md:56`).

[추정] 게이트 개정 전·후 또는 `OK`와 ground-truth 정상의 정의가 달라진 것이 원인으로 보인다. 그러나 문서 전체에서 동일 지표명이 버전별로 혼용되어 어느 값이 정본인지 판별할 수 없다.

### 발견 4 — [불일치] Round 11의 “깨끗한 컷아웃” 건수가 12와 13으로 갈림

- [확인] 추출기 1차 수정 결과는 깨끗한 컷아웃 12건, 2차도 동일한 12건이라고 적는다(`docs/deliverables/experiments/round-11/01-implementation-checkpoint.md:54`, `docs/deliverables/experiments/round-11/01-implementation-checkpoint.md:58`).
- [확인] 같은 차수의 최종 판정은 자동 지표가 깨끗한 컷아웃을 3건에서 13건으로 늘렸다고 적는다(`docs/deliverables/experiments/round-11/03-experiment-report.md:71`, `docs/deliverables/experiments/round-11/03-experiment-report.md:86`).
- Round 11 에러 분석의 상세 수치도 12건으로 적는다(`docs/deliverables/experiments/round-11/02-error-analysis.md:69`).

[추정] 12건은 수동/합성 품질 기준이고 13건은 개정 게이트 `OK` 수일 가능성이 있지만, 문서에서 두 분모·판정 기준을 분리하지 않았다.

### 발견 5 — [치명] 12차까지 갱신된 상위 색인·감사 문서에 후속 사실이 반영되지 않음

- [확인] 색인은 12차 행까지 포함하고도 전체 결론에서 “최종 9차”라고 적는다(`docs/deliverables/03-second-experiment-report.md:140`, `docs/deliverables/03-second-experiment-report.md:166`).
- [확인] 같은 색인의 미해결 목록은 60건 전체 평가가 수행되지 않았다고 적지만, 10차 로그에는 `--all`로 60/60 성공이 명시되어 있다(`docs/deliverables/03-second-experiment-report.md:175`, `docs/deliverables/experiments/round-10/03-experiment-report.md:45`, `docs/deliverables/experiments/round-10/03-experiment-report.md:60`, `docs/evaluation/full60-runs.md:15`).
- [확인] 색인은 생성 자산의 `참고용` 라벨이 `react_document`와 캔버스에 없다고 적지만, 10차에는 라벨 게이트 60/60 PASS가 기록됐고 12차에는 해당 표시를 정책적으로 제거했다고 기록한다(`docs/deliverables/03-second-experiment-report.md:176`, `docs/deliverables/experiments/round-10/03-experiment-report.md:47`, `docs/deliverables/experiments/round-12/01-implementation-checkpoint.md:17`, `docs/deliverables/experiments/round-12/01-implementation-checkpoint.md:19`, `docs/deliverables/experiments/round-12/01-implementation-checkpoint.md:43`, `docs/deliverables/experiments/round-12/01-implementation-checkpoint.md:49`).
- [확인] 2026-09-16 감사 문서도 `cma_real_v1` 60건 전체 모델 실행이 아직 없다고 적지만, 위 10차·전수 보존 기록과 충돌한다(`docs/deliverables-audit.md:14`, `docs/deliverables-audit.md:27`, `docs/evaluation/full60-runs.md:15`, `docs/evaluation/full60-runs.md:23`). 60건 전체 실행 자체는 해결됐고, 사람 검수와 API·상태·안전 전용 평가셋은 여전히 미완료다.

9월 9일자로 명시된 `metrics-definition.md`의 당시 미실행 기록은 시점 기록으로 처리하여 이 발견에 중복 집계하지 않았다(`docs/evaluation/metrics-definition.md:3`, `docs/evaluation/metrics-definition.md:5`).

### 발견 6 — [사소] 사람의 질적 판단·일치율 기록은 있으나 공식 사람 점수/설문은 없음

- [확인] 공식 1~5점 사람 검수나 설문 결과는 발견되지 않았다. 파일럿 보고서는 점수 시트가 pending이라고 적고(`docs/evaluation/pilot-report-2026-09-09.md:128`, `docs/evaluation/pilot-report-2026-09-09.md:129`), Round 11도 정량화된 사람 품질 점수가 없다고 명시한다(`docs/deliverables/experiments/round-11/03-experiment-report.md:102`, `docs/deliverables/experiments/round-11/03-experiment-report.md:103`).
- [확인] 다만 관리자의 질적 판단 문장은 존재한다: 60건 A/B 결과에서 “이전이 나은 것 같다”(`docs/deliverables/experiments/round-11/01-implementation-checkpoint.md:62`, `docs/deliverables/experiments/round-11/03-experiment-report.md:75`), rembg 결과의 “잘땄네”(`docs/deliverables/experiments/round-12/03-experiment-report.md:47`), 독립 정답 문서의 `관리자 육안 검증 5건 일치율: 5/5 (100%)`(`docs/evaluation/cutout-ground-truth.md:8`)가 있다.
- 위 기록은 사람 품질 점수나 설문 결과로 둔갑하지 않았고, `AI 참고치`와도 구분되어 있다. 따라서 존재하지 않는 사람 점수를 발견한 것은 아니며, 작업 지시가 요구한 사람 판단 문장 목록으로만 보고한다.

## `docs/deliverables-audit.md` 미해결 항목의 실제 상태

### 실제로 해결된 것

- [확인] `cma_real_v1` 60건 전체 모델 실행 자체: 10차 `--all` 실행이 60/60 성공했다(`docs/deliverables/experiments/round-10/03-experiment-report.md:45`, `docs/deliverables/experiments/round-10/03-experiment-report.md:60`). 현재·대조용 산출물과 `run_index.json`도 보존되어 있다(`docs/evaluation/full60-runs.md:12`, `docs/evaluation/full60-runs.md:13`, `docs/evaluation/full60-runs.md:15`). 감사표의 “60건 전체 실행 없음”은 열림 항목이 아니라 문서 불일치다.
- [확인] 생성 참고 자산의 provenance 구분은 `product_generated`로 구현·보존됐다(`docs/deliverables/experiments/round-12/05-be-fe-interface.md:29`, `docs/deliverables/experiments/round-12/05-be-fe-interface.md:31`, `docs/deliverables/experiments/round-12/05-be-fe-interface.md:36`, `docs/deliverables/experiments/round-12/05-be-fe-interface.md:37`). 과거 `참고용` 표시 누락 게이트는 10차에 60/60 PASS였고, 12차에는 관리자 결정으로 표시와 게이트 자체를 제거했다(`docs/deliverables/experiments/round-10/05-be-fe-interface.md:48`, `docs/deliverables/experiments/round-12/01-implementation-checkpoint.md:43`, `docs/deliverables/experiments/round-12/01-implementation-checkpoint.md:48`).
- [확인] hero 원본 고정·`source_original`·rembg 버전 고정은 채택 상태다(`docs/deliverables/experiments/round-12/01-implementation-checkpoint.md:17`, `docs/deliverables/experiments/round-12/01-implementation-checkpoint.md:18`, `docs/deliverables/experiments/round-12/01-implementation-checkpoint.md:29`, `docs/deliverables/experiments/round-12/01-implementation-checkpoint.md:41`). 제한형 React JSON AST 및 자동 계약 게이트도 구현·기록됐다(`docs/deliverables-audit.md:11`, `docs/deliverables-audit.md:31`).
- [확인] CMA 원본 60건의 파일·decode·hash·license 표시 검증과 서버/로컬 아키텍처 문서화는 완료로 기록되어 있다(`docs/deliverables-audit.md:16`, `docs/deliverables-audit.md:27`). 단, 권리 범위와 GPU 실기동은 아래 열린 항목이다.

### 여전히 열려 있는 것

- [확인] 상품 BE 공개 URL·인증·실제 사용자 흐름의 합의/검증: 현재 앱은 인증 없는 로컬 legacy `/api/v1/ai/...`와 `X-AI-Internal-Token` 기반 `/internal/v1/ai/...`를 구분하며(`src/detail_page_ai/app.py:214`, `src/detail_page_ai/app.py:229`, `src/detail_page_ai/app.py:325`, `src/detail_page_ai/app.py:334`, `src/detail_page_ai/app.py:339`), 공개 상품 BE 경로는 제안 상태다(`docs/api/be-fe-ai-integration-spec.md:12`, `docs/deliverables-audit.md:8`).
- [확인] 서버 GPU에서 SGLang 텍스트·이미지 2프로세스 동시 적재, 4bit 로딩, 편집 품질·처리 시간·peak VRAM 검증: 미실행으로 남아 있다(`docs/deliverables-audit.md:9`, `docs/deliverables-audit.md:26`, `docs/deliverables-audit.md:60`).
- [확인] 직접 제공 자산의 권리 범위 증빙 및 CMA 라벨/시각 사실의 2인 gold 승인: 미완료다(`docs/deliverables-audit.md:12`, `docs/deliverables-audit.md:13`, `docs/deliverables-audit.md:56`, `docs/deliverables-audit.md:57`).
- [확인] 사람 2인 품질 검수, numerator/denominator·실패·사람 점수의 정량 기록: 미완료다(`docs/deliverables-audit.md:15`, `docs/deliverables-audit.md:23`, `docs/deliverables-audit.md:27`, `docs/deliverables-audit.md:59`, `docs/evaluation/ai-review-2026-09-10.md:14`).
- [확인] API·상태·안전 전용 고유 요청 50건 이상 평가셋: 기존 fixture는 3상품 반복이며 전용 set이 없다(`docs/deliverables-audit.md:14`, `docs/deliverables-audit.md:49`, `docs/evaluation/metrics-definition.md:16`, `docs/evaluation/metrics-definition.md:90`).
- [확인] FE renderer와 상품 BE 저장 schema/자산 manifest의 실제 연동 검증, `page_plan` 하위 호환 종료 시점 합의: 남은 조건이다(`docs/deliverables-audit.md:11`, `docs/deliverables-audit.md:61`, `docs/deliverables/experiments/round-12/05-be-fe-interface.md:48`, `docs/deliverables/experiments/round-12/05-be-fe-interface.md:58`).

## 작업 파일 보고

- 변경 파일: `.orchestration/reports/audit-2026-09-16/agy2.md`를 새로 작성했다. 기존 산출물·차수 로그·평가 문서는 수정하지 않았다.
- 검증 방법: 60개 차수 Markdown 전체 열람, `rg --files` 기반 파일 수 확인, 헤더·금지 문장·human/score 키워드 정적 검색, 색인 수치와 각 차수 `03` 문서 대조, 후속 60건 산출물·코드 라우트 교차 확인.
- 미해결 이슈: 위 발견 1~6 및 `여전히 열려 있는 것` 목록에 남겼다.

완료: .orchestration/reports/audit-2026-09-16/agy2.md, 발견 6건
