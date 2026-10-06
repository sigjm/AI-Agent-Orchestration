# BE 흐름 수정 후속 2건 — 판매자 문장 포함 경고 거르기 · 분석 프롬프트 1줄 되돌리기

앞 작업 `20261001-be-flow-fixes-3-7.md` 의 후속이다. 수정된 코드로 BE 흐름을 다시 돌려 본 결과 두 가지가 남았다.
작업 트리에는 앞 작업의 미커밋 변경이 그대로 있다. 그 위에서 고친다.

## 1. 판매자 문장을 바꿔 쓴 경고도 거르기 (`src/detail_page_ai/validation.py`)

### 실제로 남은 경우

- 판매자 관리 방법(care_guide): `펼칠 때는 아래에서 위로 천천히 펴 주세요. 사용 후에는 …`
- 모델이 낸 `safety_notes`: `부채를 펼칠 때는 아래에서 위로 천천히 펴 주세요.`
- 현재 `sanitize_profile_for_render` 의 `unconfirmed()` 는 **정규화한 문장이 완전히 같을 때만** 거른다. 앞에 `부채를 ` 이 붙어 못 걸렀고, 그대로 초안 경고에 나왔다 (2회 실행 모두)

### 고칠 것

경고 문장(나눈 각 문장)이 **판매자 문장을 그대로 포함하고, 판매자 문장 말고는 짧은 주어 정도만 덧붙은 경우**도 확인된 것으로 보고 거른다.

반드시 지킬 조건 (테스트로 고정):

| 경고 | 판매자 입력 | 기대 |
| --- | --- | --- |
| `부채를 펼칠 때는 아래에서 위로 천천히 펴 주세요.` | care_guide 에 `펼칠 때는 아래에서 위로 천천히 펴 주세요.` | **제거** (실제 사례) |
| `매화선의 정확한 크기는 확인이 필요합니다.` | product_name `매화선` | **유지** — 상품명처럼 짧은 값이 들어 있다고 지우면 안 된다 |
| `직사광선과 습기를 피해 보관해 주세요 그렇지 않으면 선면이 휘어질 수 있어 확인이 필요합니다.` | care_guide 에 `직사광선과 습기를 피해 보관해 주세요.` | **유지** — 판매자 문장 뒤에 확인되지 않은 내용이 붙으면 지우면 안 된다 |
| 기존 `test_confirmed_seller_sentences_are_removed_from_both_warning_sources`, `test_warnings_without_seller_confirmation_are_retained` | — | 그대로 통과 |

- 포함 비교는 **문장 단위 판매자 입력(making_method · care_guide 를 나눈 문장)** 에만 쓴다. product_name 은 지금처럼 완전 일치만
- "짧은 주어만 덧붙음"의 기준(덧붙은 글자 수 또는 비율)은 정하되, 정한 값과 이유를 결과에 적는다. 위 표의 세 경우가 모두 맞게 나와야 한다
- `uncertain_information` · `safety_notes` 두 필드 모두 같은 규칙 (지금 구조 그대로)

## 2. 분석 프롬프트에서 1줄 되돌리기 (`src/detail_page_ai/prompts.py`)

앞 작업에서 CARE DATA GATE 에 추가한 아래 두 줄을 **지운다** (앞 작업 전 상태로).

```
  Do not repeat supplied care guidance in uncertain_information or safety_notes; it is
  confirmed seller data and belongs in the care notice, not the confirmation warnings.
```

- 이유: 이 줄을 넣은 뒤 실행 2번 모두 사용 장면(usage_scene) 문구가 나빠졌다. 1번은 밋밋한 문장, 1번은 관리 방법 문장을 그대로 사용 장면에 넣었다. 같은 판매자 입력에서 이 줄이 없던 어제 실행은 정상이었다. 판매자 문장 거르기는 1번 코드 처리로 맡긴다
- **같은 작업에서 추가한 recommendation 관련 줄은 그대로 둔다.** 위 두 줄만 지운다
- 이 두 줄을 확인하는 테스트가 있으면 그 단언만 지운다. 다른 프롬프트 테스트는 건드리지 않는다

## 확인

- `uv run pytest` 전체 통과 (현재 502 passed 기준). 결과 숫자를 적는다
- 테스트를 약하게 만들거나 기존 단언을 지우지 않는다 (2번의 해당 단언 제외)

## 하지 말 것

- **git 상태 변경 금지** (commit/checkout/reset/stash/restore/switch/add)
- 위 두 파일과 테스트 외 파일 수정 금지
- 모델 서버·AI 서비스를 띄우지 않는다. 실제 흐름 재실행은 관리자가 한다

## 보고 — 이 파일 하단 `## 결과`

- 바꾼 함수와 기준값(덧붙은 길이 기준)과 그 이유
- 추가한 테스트 이름
- 전체 테스트 결과

## 결과

### 1. 판매자 문장에 짧은 주어가 붙은 경고 처리

- `src/detail_page_ai/validation.py`의 `sanitize_profile_for_render` 내 문장 판정과 `_seller_confirmed_statements`를 수정하고, `_seller_instruction_statements`, `_has_seller_subject_prefix`를 추가했다. `uncertain_information`과 `safety_notes`에 같은 판정을 적용한다.
- 기존 정규화·완전 일치 판정은 유지했다. 포함 비교 후보는 **making_method와 care_guide를 나눈 개별 문장**만 사용한다. product_name은 전체 값의 정규화된 완전 일치만 인정하며, 이름에 마침표가 있어도 분할하지 않는다.
- 포함 비교는 정규화한 판매자 문장이 경고 문장의 **끝에 그대로 있을 때만** 허용한다. 그 앞의 추가 부분은 공백으로 분리되고, `은·는·이·가·을·를`로 끝나는 단순 주어/목적어 형태이며, **공백을 제외하여 조사까지 최대 8자**여야 한다(`_MAX_SELLER_SUBJECT_PREFIX_CHARS = 8`).
- **기준의 이유:** 실제 사례의 `부채를`은 3자, 흔한 `이 제품은`은 공백 제외 4자다. 8자는 짧은 제품명과 조사까지 수용하면서 길게 덧붙인 설명은 경고에 남기는 보수적인 상한이다. 8자/9자 경계 테스트로 고정했다. `확인 필요:`처럼 짧더라도 주어가 아닌 표현은 인정하지 않는다.
- 판매자 문장 뒤에 새 내용이 있으면 길이에 관계없이 유지한다. 경고가 여러 문장일 때도 **모든 문장이 확인된 경우에만** 제거하며, 확인되지 않은 문장이 하나라도 있으면 원래 경고 전체를 남긴다.
- 요구한 실제 문구 `부채를 펼칠 때는 아래에서 위로 천천히 펴 주세요.`는 제거된다. `매화선의 정확한 크기는 확인이 필요합니다.`와 보관 문장 뒤에 선면 휨 주장이 붙은 경고는 유지된다. 두 경고 필드 모두 검증했다.

### 2. CARE DATA GATE 두 줄 되돌리기

- `src/detail_page_ai/prompts.py::build_analysis_prompt`의 CARE DATA GATE에서 지정된 두 줄만 삭제했다. recommendation 지시 및 나머지 프롬프트는 그대로 두었다.
- 수정 직전 프롬프트에서 해당 두 줄만 제거해 계산한 SHA-256과 수정 후 파일의 SHA-256이 일치했다. 해당 두 줄을 직접 확인하는 기존 테스트 단언은 없었으므로 프롬프트 테스트를 변경하지 않았다.

### 추가한 테스트

`tests/test_be_flow_fixes.py`에 다음 4개 테스트 함수, 매개변수를 포함해 **20개 사례**를 추가했다.

- `test_seller_instruction_with_short_subject_prefix_is_confirmed`: 실제 care_guide 사례와 making_method의 짧은 제품 주어, 판매자 입력의 문장 분할, 두 경고 필드.
- `test_product_name_only_matches_the_entire_warning`: 상품명이 포함된 크기 경고 유지, 마침표가 있는 상품명의 일부만 일치하는 경우 유지.
- `test_seller_instruction_with_added_claim_is_retained`: 같은 문장 안의 추가 주장, 마침표로 나눈 추가 주장, 짧게 덧붙인 내용도 유지.
- `test_seller_instruction_prefix_is_bounded_and_subject_only`: 추가 주어 8자 허용/9자 유지, 짧은 확인 필요 표기는 유지, 두 경고 필드.

기존 `test_confirmed_seller_sentences_are_removed_from_both_warning_sources`, `test_warnings_without_seller_confirmation_are_retained` 및 다른 기존 테스트·단언은 변경하지 않았다.

### 검증 결과

- 수정 전 신규 회귀 테스트: **8 failed, 12 passed**. 접두 주어가 붙은 문장이 제거되지 않는 문제와 상품명을 문장으로 분할하던 문제를 재현했다.
- 수정 후 `uv run pytest -q tests/test_be_flow_fixes.py tests/test_prompts.py`: **114 passed**.
- 요청한 전체 **`uv run pytest` → 522 passed, 2 warnings in 22.09s**. 기존 Starlette/httpx 및 anyio 사용 중단 경고 2건이다. 현재 기준 502개에 신규 20개 사례가 추가됐다.
- `git --no-optional-locks diff --check` 통과. 금지된 git 변경 명령은 실행하지 않았다. 이번 수정은 지정된 두 Python 파일, 위 테스트 파일, 이 결과 보고에 한정했다.
- 모델 서버·AI 서비스를 띄우거나 실제 BE 흐름을 재실행하지 않았다. 실제 모델의 사용 장면 개선 여부는 관리자 재실행으로 확인할 사항이다. 이번 포함 비교는 의미를 바꾼 의역이나 9자 이상의 제품 주어까지 제거하지 않으며, 그런 경우 경고를 보존한다.
