# 섹션 시퀀스 고정 원인 진단과 프롬프트 최소 개정안

- 작성자: 워커 agy
- 작성일시: 2026-09-10 11:00:00
- 대상 파일: `src/detail_page_ai/prompts.py` (`build_analysis_prompt`)

---

## 1. 진단 (Diagnosis)

### 1.1 현상 실측 및 문제 배경
- **수정 전 (`pilot-20260909-224737`)**: 6건 중 5건이 10블록 동일 (`hero → statement → feature_grid → detail_split → usage_scene → gallery → recommendation → info_table → notice → closing`), `jewelry` 1건만 9블록 (`statement` 제외).
- **수정 후 (`pilot-20260910-102346`)**: `validation.py`의 `ensure_editorial_page_plan()`에서 누락 블록 임의 삽입 로직을 제거하고 `len(middle) >= 6`일 때 모델의 중간 시퀀스를 100% 보존하도록 수정하였음.
- **실측 결과**: 파이프라인 코드가 블록 순서 강제를 멈췄음에도, 모델 순수 출력 결과는 여전히 5건이 동일한 9블록(`recommendation`만 빠진 동일 순서)이며, `jewelry` 1건만 8블록(`statement` 제외)으로 나타남.
- **결론**: 시퀀스 고정의 원인은 파이프라인 파이썬 코드가 아니라, **LLM 프롬프트 입력 자체에 강력한 고정 시퀀스 유도 기제가 존재하기 때문**임.

---

### 1.2 핵심 원인 분석

#### 원인 1: 시계열적 절차 레시피 어조의 불릿 목록 (가장 결정적 원인)
`src/detail_page_ai/prompts.py` 160~177행의 `Reference-inspired composition rules`는 개별 블록의 규칙을 설명하면서 **시계열적 순서 접속어(Chronological Procedural Verbs)**를 직접 사용하고 있습니다:

> **[원문 인용] (`src/detail_page_ai/prompts.py:160-177`)**
> ```text
> - Open with an editorial hero using the complete source view and generous copy space.
> - Follow with a light statement or feature_grid that summarizes visible form, surface, color,
>   and components without inventing material or performance claims.
> - Include at least one dark detail_split using a real detail photo_id. Alternate image placement
>   only when another visible feature deserves its own section.
> - Include one full-bleed usage_scene with photo_id lifestyle. The copy must describe a plausible
>   setting as a styling suggestion, never as proof of actual performance.
> - Always include exactly one gallery with eyebrow PRODUCT GALLERY and photo_ids
>   ["detail", "detail-02", "detail-03", "detail-04", "detail-05"]. The renderer uses available
>   distinct assets in a 3-up then 2-up arrangement; never promise five original photographs.
>   A palette is optional and must never replace the gallery. If generated cuts are included,
>   describe the gallery as original detail plus AI styling references, not all original views.
> - Include recommendation as clearly labeled styling suggestions, not product facts.
> - Include info_table with image-visible or creator-provided fields; use "확인 필요" instead
>   of inventing missing dimensions, materials, price, maker, or origin.
> - Include a dark notice block for supplied careTips or concise verification notes. Supplied
>   careTips are the product's declared care guidance and should be retained when present.
> - Finish with a restrained closing statement. Closing must be last.
> ```

- **산출물 연결**:
  - `Open with...` (hero)
  - `Follow with...` (statement, feature_grid)
  - `Include at least one...` (detail_split)
  - `Include one...` (usage_scene)
  - `Always include...` (gallery)
  - `Include info_table...` (info_table)
  - `Include a dark notice...` (notice)
  - `Finish with... Closing must be last.` (closing)
  
  LLM(특히 지시 수행 능력이 뛰어난 모델)은 `Open with` → `Follow with` → `Include` → `Finish with`로 이어지는 불릿을 "상세페이지 작성의 순차적 체크리스트/레시피"로 해석합니다. 모델은 이 목록의 하향식(top-to-bottom) 순서를 그대로 자신의 출력 JSON 배열의 인덱스로 1:1 전사하고 있습니다.

---

#### 원인 2: 프롬프트 상단 Copy Map에 의한 이중 순서 각인 (Dual Sequence Reinforcement)
프롬프트 상단의 61~73행에서도 블록 설명이 동일한 순서로 나열되어 있습니다:

> **[원문 인용] (`src/detail_page_ai/prompts.py:61-73`)**
> ```text
> Use this section-aware copy map when composing page_plan:
> - hero: preserve the product identity and one distinctive supported proposition.
> - statement: explain the supplied making/process story in clear, human language.
> - feature_grid: convert three distinct visible or supplied product facts into separate cards;
>   do not make three versions of the same visual adjective.
> - detail_split: explain one concrete surface, shape, structure, or process detail with its
>   evidence level.
> - usage_scene: suggest a plausible setting or use without claiming that the image proves
>   performance, safety, durability, or actual use.
> - info_table: include only creator-supplied or image-visible fields; otherwise write "확인 필요".
> - notice: use only supplied care guidance plus concise missing-information notes; never invent
>   material-specific cleaning or handling instructions.
> - closing: restate the product identity or making idea without introducing a new fact.
> ```

- **산출물 연결**:
  프롬프트 전반부(61행)와 후반부(160행) 두 곳 모두에서 블록의 순서가 `hero → statement → feature_grid → detail_split → usage_scene → (gallery) → info_table → notice → closing`으로 일관되게 제시됩니다. 이로 인해 모델의 어텐션 메커니즘은 이 순서를 단 하나의 '공식 표준 템플릿'으로 확신하게 됩니다.

---

#### 원인 3: 블록 수 하한선(9개)과 가용 필수 블록 수의 일치로 인한 선택의 여지 박탈
> **[원문 인용] (`src/detail_page_ai/prompts.py:141`)**
> ```text
> page_plan must contain 9 to 12 safe, whitelisted blocks.
> ```

- **산출물 연결**:
  프롬프트에서 활발히 설명된 블록은 정확히 9종(`hero`, `statement`, `feature_grid`, `detail_split`, `usage_scene`, `gallery`, `info_table`, `notice`, `closing`)입니다.
  `palette`나 `scale_reference`, `wide_image`는 조건부이거나 억제되어 있어 사실상 쓰기 어렵습니다.
  결과적으로 "최소 9개 이상이어야 한다"는 조건은 **"위 9개 블록을 단 하나도 빠짐없이 모두 넣어야 한다"**는 강제 구속으로 작동합니다.
  유일하게 제작과정 데이터가 없어 `statement`를 뺀 `jewelry`(`cma-109609`) 케이스만 8블록으로 생성되어 9개 하한선을 간신히 위반했을 뿐, 나머지 5건은 모두 정확히 최소치인 9블록을 채우기 위해 9개 블록 전체를 동일 순서로 복사했습니다.

---

#### 원인 4: 아키타입(Archetype) 가이드와 구체적 `block_type` 간의 매핑 부재
> **[원문 인용] (`src/detail_page_ai/reference_guide.py:79-82`)**
> ```text
>   * silhouette-led: hero scale → form proof → proportion/edge detail → use context;
>   * texture-led: quiet hero → material macro → craft/finish proof → tactile use context;
>   * set-led: complete lineup → component grouping → comparison/gallery → shared use context;
>   * process-led: finished object → creator-provided process → detail proof → care and use.
> ```

- **산출물 연결 및 실측 증거**:
  `reference_guide.py`는 아키타입 4종을 제시하지만, 사용된 단어(`form proof`, `proportion/edge detail`, `material macro` 등)가 사진/큐레이션의 추상적 개념일 뿐 `PageBlockDto.block_type` 토큰과 직접 연결되지 않습니다.
  반면 160행 이하에서는 `block_type` 문자열이 직관적 순서로 나열되어 있으므로 모델은 구체적인 후자를 따릅니다.
  **[결정적 실측 증거 - Jewelry]**:
  위 아키타입 중 유일하게 구체적인 블록 유사어(`comparison/gallery`)가 명시된 `set-led`의 경우, `shared use context`보다 `gallery`가 앞에 옵니다.
  실제로 `pilot-20260910-102346`의 6건 중 유일하게 `catalog-grid` / `set-led`로 분류된 `analysis-cma-109609`(jewelry)에서만 **`gallery`가 `usage_scene`보다 앞서는 순서 역전**(`feature_grid → detail_split → gallery → usage_scene`)이 발생했습니다!
  이는 **아키타입에 구체적인 `block_type` 순서가 매핑되면 모델이 실제로 시퀀스를 변경한다는 명백한 실증적 근거**입니다.

---

#### 원인 5: 부정형 금지문("Do not use one fixed sequence")의 무력화
> **[원문 인용] (`src/detail_page_ai/prompts.py:139, 180`)**
> ```text
> The authoritative layout is page_plan. Do not use one fixed sequence for every product.
> Vary optional blocks and their order when the evidence calls for it; do not copy one fixed middle sequence for every product.
> ```

- **산출물 연결**:
  프롬프트에 "고정된 시퀀스를 쓰지 마라"는 문장이 2회나 등장하지만 완전히 무시되었습니다.
  LLM에 부정형 제약("~하지 마라")만 주고, 어떤 상황에서 어떤 순서로 배치해야 하는지에 대한 **양성적 조건 분기(Positive Conditional Branching)**를 제공하지 않으면, 모델은 가장 명확하고 안전한 디폴트 레시피(원인 1)로 수렴합니다.

---

## 2. 개정안 (Proposal)

최소 변경 원칙(Minimal Change)에 따라 `src/detail_page_ai/prompts.py`의 `build_analysis_prompt()` 내 3개 핵심 위치만 수정합니다.

### 2.1 수정 1: 상단 Copy Map의 순서 각인 해제 (61행)

#### [Before]
```python
Use this section-aware copy map when composing page_plan:
- hero: preserve the product identity and one distinctive supported proposition.
```

#### [After]
```python
Section copy reference (content role for each block type; the page sequence must follow the selected archetype, not this list order):
- hero: preserve the product identity and one distinctive supported proposition.
```

---

### 2.2 수정 2: 블록 개수 하한선 완화 (9 → 8개) (141행)

#### [Before]
```python
page_plan must contain 9 to 12 safe, whitelisted blocks. Compose it like a premium craft editorial
```

#### [After]
```python
page_plan must contain 8 to 12 safe, whitelisted blocks. Compose it like a premium craft editorial
```
*(근거: `validation.py` line 114의 `if len(middle) >= 6:` 조건은 hero + middle 6개 + closing = 총 8개 블록부터 모델 순서를 보존함. 8개로 낮춰야 제작과정 데이터가 없는 상품에서 무의미한 `statement`를 생략할 수 있음).*

---

### 2.3 수정 3: 시계열 레시피 불릿을 아키타입 기반 시퀀스 규칙으로 전환 (160~181행)

#### [Before]
```python
Reference-inspired composition rules:
{build_reference_guide_prompt()}
- Open with an editorial hero using the complete source view and generous copy space.
- Follow with a light statement or feature_grid that summarizes visible form, surface, color,
  and components without inventing material or performance claims.
- Include at least one dark detail_split using a real detail photo_id. Alternate image placement
  only when another visible feature deserves its own section.
- Include one full-bleed usage_scene with photo_id lifestyle. The copy must describe a plausible
  setting as a styling suggestion, never as proof of actual performance.
- Always include exactly one gallery with eyebrow PRODUCT GALLERY and photo_ids
  ["detail", "detail-02", "detail-03", "detail-04", "detail-05"]. The renderer uses available
  distinct assets in a 3-up then 2-up arrangement; never promise five original photographs.
  A palette is optional and must never replace the gallery. If generated cuts are included,
  describe the gallery as original detail plus AI styling references, not all original views.
- Include recommendation as clearly labeled styling suggestions, not product facts.
- Include info_table with image-visible or creator-provided fields; use "확인 필요" instead
  of inventing missing dimensions, materials, price, maker, or origin.
- Include a dark notice block for supplied careTips or concise verification notes. Supplied
  careTips are the product's declared care guidance and should be retained when present.
- Finish with a restrained closing statement. Closing must be last.
Use dark for the main detail_split, full-bleed for the main usage_scene, sand for palette when
present, dark for notice, and paper for hero and closing. Vary optional blocks and their order
when the evidence calls for it; do not copy one fixed middle sequence for every product.
```

#### [After]
```python
Reference-inspired composition rules:
{build_reference_guide_prompt()}
Structure and archetype-driven sequence rules:
- Outer frame: Hero must be first (variant paper). Closing must be last (variant paper).
  Place info_table and dark notice immediately before closing.
- Core required blocks: Every page must include hero, at least one dark detail_split, one
  full-bleed usage_scene (photo_id lifestyle), exactly one gallery with eyebrow PRODUCT GALLERY
  and photo_ids ["detail", "detail-02", "detail-03", "detail-04", "detail-05"], info_table,
  dark notice, and closing. Include statement ONLY when creator supplies making/process facts.
- Order the middle blocks (between hero and info_table) strictly according to the product's
  primary editorial archetype:
  * texture-led (textile, ceramic, metalware with prominent surface, relief, or weave):
    hero → detail_split → feature_grid → gallery → usage_scene → info_table → notice → closing
  * silhouette-led (furniture, box, vessels where spatial presence, scale, and function lead):
    hero → usage_scene → feature_grid → detail_split → gallery → info_table → notice → closing
  * set-led / catalog-grid (jewelry, small accessories, multi-part items):
    hero → feature_grid → gallery → detail_split → usage_scene → info_table → notice → closing
  * process-led (when creator supplied making method):
    hero → statement → feature_grid → detail_split → gallery → usage_scene → info_table → notice → closing
Use dark for detail_split, full-bleed for usage_scene, sand for palette when present, dark for notice,
and paper for hero and closing.
```

---

## 3. 검증 가능한 예측 (Testable Predictions)

이 개정안을 적용하고 6건 파일럿을 재실행했을 때 실측되어야 하는 명확한 변화:

1. **고유 시퀀스 다양성 확대**:
   - 현재: 6건 중 실질적 시퀀스 단 1종 (5건 동일, jewelry 1건만 미세 차이).
   - 예측: 6건 파일럿에서 **최소 3개 이상의 서로 다른 고유 시퀀스**가 도출됨.
2. **카테고리별 2번째 블록의 즉각적 분기**:
   - **직물(`cma-102980`)**: `texture-led`로 분류되어 `hero` 바로 다음에 `detail_split`이 2번째 블록으로 위치 (`hero → detail_split → ...`).
   - **가구/도구(`cma-110793`) 또는 상자(`cma-101636`)**: `silhouette-led`로 분류되어 `hero` 바로 다음에 `usage_scene`이 2번째 블록으로 전진 배치 (`hero → usage_scene → ...`).
   - **장신구(`cma-109609`)**: `set-led`로 분류되어 `hero → feature_grid → gallery`의 카탈로그형 흐름 유지.
3. **불필요한 statement 블록의 자연스러운 탈락**:
   - 제작과정(`howMade`) 데이터가 없는 공예품 6건 중 최소 3건 이상에서 `statement`가 생략되어 총 블록 수가 8개로 컴팩트해짐.
4. **Validation 무결성 유지**:
   - 모든 케이스의 중간 블록 수가 6~7개(`len(middle) >= 6`)를 유지하여, `validation.py`의 레거시 fallback 주입 로직을 전혀 건드리지 않고 모델 순서가 100% 보존됨.

---

## 4. 위험과 완화책 (Risks & Mitigations)

1. **`validation.py`의 `len(middle) >= 6` 임계치 위험**:
   - 만약 모델이 블록을 3개 이상 한꺼번에 생략하여 중간 블록이 5개 이하가 되면, `validation.py`의 fallback 삽입 루틴(145~250행)이 발동하여 모델이 계획한 시퀀스가 파괴되고 강제로 기본 블록들이 재배치될 위험이 있음.
   - **완화책**: 개정안에서 `Core required blocks`를 명시하여 `hero`, `detail_split`, `usage_scene`, `gallery`, `info_table`, `notice`, `closing` (총 7개, 중간 블록 5개) 외에 `feature_grid`나 `statement` 중 하나를 반드시 포함하도록 유도함으로써 중간 블록 수가 최소 6개 이상이 되도록 방어함.
2. **DTO 제약 위반 위험 (`max_length=14`)**:
   - 제안된 아키타입별 시퀀스는 총 8~9개 블록으로 구성되므로, `PageBlockDto`의 14개 제한을 초과할 위험은 0%임.
3. **렌더러(Canvas / HTML) 호환성**:
   - `html_renderer.py` 및 `react_document_builder.py`는 `PageBlockDto` 리스트의 인덱스 순서대로 캔버스를 빌드하므로, 중간 블록의 순서가 바뀌어도(예: `detail_split`이 `feature_grid`보다 앞에 옴) 렌더링 엔진 파이프라인에서 오류가 발생하지 않음.
4. **아키타입 분류의 일관성**:
   - LLM이 제품의 시각적 특성에 따라 아키타입을 잘못 선택할 가능성은 있으나, 제시된 4개 아키타입 모두 검증된 화이트리스트 블록과 스타일 토큰만 사용하므로 배포 차단(Gate) 위반이나 깨진 레이아웃을 생성할 위험이 전혀 없음.
