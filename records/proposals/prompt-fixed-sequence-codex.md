# 교차검증: 섹션 시퀀스 고정 원인과 최소 프롬프트 개정안

## 조사 범위와 관찰 근거

이 진단은 `build_analysis_prompt()`와 그 안에 주입되는 `build_reference_guide_prompt()`의 문구, 그리고 두 파일럿의 `result_summary.json`에 있는 `product.page_plan`만 대조했다. 다른 검수자의 결과나 다른 작업 브리프는 확인하지 않았다.

| 파일럿 | 최빈 시퀀스 | 빈도 | 예외 |
|---|---|---:|---|
| `pilot-20260909-224737` | `hero → statement → feature_grid → detail_split → usage_scene → gallery → recommendation → info_table → notice → closing` | 5/6 | jewelry만 `statement` 없이 9블록 |
| `pilot-20260910-102346` | `hero → statement → feature_grid → detail_split → usage_scene → gallery → info_table → notice → closing` | 5/6 | jewelry만 `statement` 없이 8블록 |

수정 후 파일럿도 5개 계획은 9블록(중간 7개), jewelry는 8블록(중간 6개)이다. 현재 `ensure_editorial_page_plan()`은 중간 블록 6개 이상에서 삽입을 건너뛰므로, 이 두 시퀀스는 검증기가 아닌 모델 출력에서 나온 것으로 판단할 수 있다.

## 진단

### 1. “고정하지 말라”는 선언이 뒤의 순차적 명령 목록과 충돌한다 — 확신 높음

프롬프트는 앞에서 다음처럼 금지한다.

> “The authoritative layout is page_plan. Do not use one fixed sequence for every product.”

하지만 이후의 `Reference-inspired composition rules`는 다음 순서로 구체적인 필수/명령형 지시를 나열한다.

> “Open with an editorial hero …”

> “Follow with a light statement or feature_grid …”

> “Include at least one dark detail_split …”

> “Include one full-bleed usage_scene …”

> “Always include exactly one gallery …”

> “Include recommendation …”

> “Include info_table …”

> “Include a dark notice block …”

> “Finish with a restrained closing statement.”

이 목록은 블록의 **선택 여부와 배열 순서**를 모두 제시한다. 모델 입장에서는 앞의 추상적 금지보다 뒤의 구체적이고 최근의 imperative 목록이 강한 실행 지시가 된다. 실제로 두 파일럿의 최빈 시퀀스는 이 나열 순서와 일치한다. 두 번째 파일럿에서 `recommendation`만 전부 빠진 것도, 모델이 제품별로 구조를 설계했다기보다 이 목록에서 한 항목만 누락한 체크리스트처럼 동작했다는 해석을 뒷받침한다.

### 2. 최소 9블록과 feature-grid 강제가 statement와 feature_grid의 동시 사용을 유도한다 — 확신 높음

다음 문장이 최소 블록 수를 강제한다.

> “page_plan must contain 9 to 12 safe, whitelisted blocks.”

그리고 마지막 일관성 검사에는 다음이 있다.

> “Use three concise feature cards with distinct observations.”

`hero`, `detail_split`, `usage_scene`, `gallery`, `recommendation`, `info_table`, `notice`, `closing`만으로는 8블록이다. 따라서 9블록 최소치를 맞추면서 세 카드 조건까지 충족하려면 `feature_grid`와 함께 `statement`를 추가하는 것이 가장 쉬운 해법이다. 실제로 5/6이 정확히 이 10블록을 사용했다. jewelry는 `statement`만 빠져 9블록이 되었고, 수정 후에는 `recommendation`까지 빠져 8블록이 되었는데도 동일한 골격을 유지했다.

### 3. archetype 선택은 추상적이고, 그 뒤의 참조 가이드가 다시 표준 서사를 강제한다 — 확신 중간

계획 단계에는 다음 지시가 있다.

> “Select one primary editorial archetype from silhouette-led, texture-led, set-led, or process-led.”

그러나 archetype마다 어떤 블록을 고르거나 생략할지 명시하지 않는다. 이어서 주입되는 참조 가이드는 다음처럼 표준 종결부와 서사 순서를 제시한다.

> “Finish with compact basic information, creator-provided care/notice content, and recommendations.”

> “Build the narrative arc as hook → proof → context → use → information → close.”

가이드는 “never as a fixed template”라고도 말하지만, page_plan에 대한 우선순위가 선언되지 않았다. 결과적으로 archetype은 블록 선택 규칙이 아니라 설명용 단어에 머물고, 모델은 구체적인 hook→proof→context→use→information→close 순서를 재사용한다. 이는 5개 `editorial-split` 결과가 같은 중간 순서를 가진 현상과 부합한다. 다만 `layout_id`의 `editorial-split` 기본값은 스타일 힌트이므로, 그 자체를 고정 시퀀스의 직접 원인으로 단정하지는 않는다.

## 최소 개정안

수정 대상은 `src/detail_page_ai/prompts.py`의 `build_analysis_prompt()` 안에서 세 군데다. `build_reference_guide_prompt()`와 DTO, 렌더러는 바꾸지 않는다.

### A. 최소 블록 수를 현재 검증 가드와 맞춘다

**Before**

> “page_plan must contain 9 to 12 safe, whitelisted blocks. Compose it like a premium craft editorial detail page, but keep it adaptive and product-specific; this is not a fixed template.”

**After**

> “page_plan must contain 8 to 12 safe, whitelisted blocks. Compose it like a premium craft editorial detail page, but keep it adaptive and product-specific; this is not a fixed template. Do not add a generic block merely to reach the minimum.”

8블록은 hero/closing을 제외하면 6개 중간 블록이어서 현재의 보존 가드와 일치한다. 9블록 최소치가 유도하던 범용 `statement` 추가 압력을 없앤다.

### B. 순서형 checklist를 선택 메뉴로 교체한다

`Reference-inspired composition rules` 아래의 “Open/Follow/Include/Always include/Finish” 9개 bullet을 다음 블록으로 교체한다. 여기서 기존의 care data gate와 gallery의 실제 photo_ids 규칙은 보존한다.

**Before (요지)**

> “Open with … Follow with … Include … Include … Always include exactly one gallery … Include recommendation … Include info_table … Include a dark notice … Finish with …”

**After**

```text
Page-plan selection precedence: for page_plan, this rule overrides any fixed order
implied by the Reference guide contract above.
- Required skeleton: hero is first, closing is last, include exactly one gallery with
  photo_ids ["detail", "detail-02", "detail-03", "detail-04", "detail-05"], and include
  the care-gated notice required above.
- Treat statement, feature_grid, detail_split, wide_image, usage_scene,
  scale_reference, palette, recommendation, and info_table as a menu, not a checklist.
  Select 4 to 8 of them from the product's visible evidence and chosen archetype; every
  selected block must have a distinct communication job. Do not select or order blocks
  by the order in this prompt.
- Choose statement or feature_grid as the first supporting block. Use both only when
  they carry non-overlapping evidence. If feature_grid is selected, use three concise
  cards with distinct observations.
- Use detail_split only when a real detail crop proves a distinct surface, shape, or
  process fact. Use usage_scene only when a product-specific styling/use context adds
  information beyond hero and detail. Use recommendation only when it can offer at
  least two non-generic, product-specific suggestions. Use info_table only when it has
  at least three distinct creator-provided or image-visible fields not repeated elsewhere.
- Bind block selection to the archetype: silhouette-led favors wide_image or
  scale_reference; texture-led favors detail_split or palette; set-led favors
  feature_grid, gallery, or info_table; process-led favors statement and detail_split.
  These are preferences, not required bundles.
```

이 변경은 hero/closing, gallery, care notice라는 렌더·안전 골격을 유지하면서 나머지 블록을 제품 근거에 따라 고르도록 만든다. 특히 `statement + feature_grid + detail_split + usage_scene + recommendation + info_table`의 동시 선택을 기본값이 아니라 예외로 바꾼다.

### C. 최종 일관성 검사의 feature-grid 강제를 조건화한다

**Before**

> “Use three concise feature cards with distinct observations.”

**After**

> “When feature_grid is selected, use three concise feature cards with distinct observations.”

이 한 문장 변경이 feature_grid를 모든 상품의 필수 블록으로 해석하는 경로를 제거한다.

## 검증 가능한 예측

다음 파일럿도 같은 6개 카테고리와 동일한 모델 조건으로 재생성하고 `result_summary.json`의 `product.page_plan`을 집계한다.

1. 6건 중 **최소 3개의 서로 다른 전체 `block_type` 시퀀스**가 나온다. 단일 시퀀스의 빈도는 **최대 2/6**이어야 한다. 현재의 5/6에서 검증 가능하게 달라지는 기준이다.
2. hero/closing을 제외한 블록 집합도 **최소 3개 조합**으로 나뉜다. 특히 `statement`와 `feature_grid`를 모두 쓰는 계획은 두 블록의 본문이 서로 다른 근거를 가질 때만 허용된다.
3. 모든 계획은 **8~12블록**, hero 첫 번째, closing 마지막, 허용된 `block_type`만 사용하며 `ProductProfileDto`의 **최대 14블록** 제한을 통과한다.
4. care_guide가 없는 입력은 기존과 동일하게 정확한 notice 문구를 유지하고, gallery가 선택된 모든 계획은 기존 5개 `photo_ids` 계약을 유지한다. 이는 구조 다양화가 안전성·이미지 계약을 훼손하지 않는지 확인하는 별도 관찰값이다.

## 위험과 완화

| 위험 | 영향 | 완화 |
|---|---|---|
| 8블록으로 하향한 최소치가 너무 짧은 페이지를 허용 | 정보·전환 맥락이 부족한 상품이 나올 수 있음 | hero/gallery/notice/closing을 유지하고, 현재 validation의 빈약 계획 안전 바닥을 그대로 둔다. |
| optional block 생략으로 usage 또는 정보 표가 사라짐 | 특정 상품에서 활용 제안 또는 사양 가독성이 낮아질 수 있음 | 사용·정보가 실제로 필요할 때만 선택하도록 조건을 명시하고, 다음 파일럿에서 block set과 카피 중복을 함께 검수한다. |
| referenced guide의 “Finish with … recommendations”가 새 규칙과 다시 충돌 | 모델이 이전 종결 순서를 계속 모방할 수 있음 | 새 `Page-plan selection precedence` 문장을 guide 주입 뒤에 두어 page_plan에서의 우선순위를 명시한다. |
| DTO/렌더 계약 위반 | parse 오류 또는 렌더 누락 | 8~12는 `ProductProfileDto.page_plan`의 max 14 안에 있고, 허용 enum·hero/closing·gallery photo_ids·care notice 조건을 새 규칙에 명시한다. |
| 프롬프트 문자열 단위 테스트 실패 | 적용 PR에서 기존 테스트가 문구를 전제 | `tests/test_prompts.py::test_analysis_prompt_requests_reference_inspired_adaptive_editorial_story`가 현재 `"9 to 12"`, `"full-bleed usage_scene"`, `"always include exactly one gallery"` 등을 기대하므로, 실제 적용 시 새 계약을 검증하는 assertions로 교체해야 한다. |

이 문서는 제안이며 `prompts.py`에는 변경을 적용하지 않았다.
