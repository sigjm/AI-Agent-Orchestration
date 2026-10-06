# 교차검증: 순서는 갈라졌지만 블록 집합이 고정되는 원인

## 조사 범위와 실측 근거

이 문서는 현재 `build_analysis_prompt()`·주입되는 `build_reference_guide_prompt()`·`validation.py`·DTO와 `pilot-20260910-111715`의 여섯 `result_summary.json`만 읽어 작성했다. 다른 워커의 결과나 다른 작업 브리프는 읽지 않았다.

최신 파일럿의 재집계 결과는 다음과 같다.

| 지표 | 관측값 |
|---|---:|
| 전체 계획 수 | 6 |
| 계획 길이 | 9블록 6/6 |
| 고유 전체 시퀀스 | 3종 |
| 최빈 전체 시퀀스 | 3/6 |
| 고유 `block_type` 집합(순서 무시) | 2종 |
| 최빈 `block_type` 집합 | 5/6 |
| `hero`, `feature_grid`, `detail_split`, `gallery`, `usage_scene`, `info_table`, `notice`, `closing` | 각 6/6 |
| `statement` / `recommendation` | 5/6 / 1/6 |

여섯 분석 입력의 `analysis_60.jsonl`은 모두 `user_hints: {}`다. 즉 runner가 만든 `UserHintsDto`에는 `product_name`, `making_method`, `care_guide`가 모두 없고, `build_analysis_prompt()`의 `Creator product data`는 `(none)`이다. `care_guide` 부재 때문에 `notice` 6/6은 의도된 안전 계약이며, 그것만으로 문제라고 보지 않는다.

## 진단

### 1. “선택 메뉴”가 실제로는 8블록 바닥을 채우는 완성형 페이지 요구다 — 확신 높음

현재 프롬프트는 다음 네 블록을 이미 고정한다.

> “Required skeleton: hero is first, closing is last, include exactly one gallery …”

> “Required care protection: include a dark notice block …”

그 직후 메뉴는 다음처럼 최소 네 개를 더 선택하라고 한다.

> “Select four to eight of them from the product's visible evidence and chosen archetype …”

따라서 hero·closing·gallery·notice 4개에 메뉴 최소 4개가 더해져, 모델은 처음부터 **8블록을 채워야 한다**. 이 자체는 `validation.py`의 `len(middle) >= 6` 보존 경계와 맞지만, 8블록 초안에서 9번째를 추가할 기준은 없다. 현재 결과는 여섯 건 모두 메뉴 블록을 다섯 개 선택해 정확히 9블록이 되었다. 메뉴의 각 설명이 넓고 긍정형이어서 모델에는 `statement + feature_grid + detail_split + usage_scene + info_table`가 가장 안전한 “완성형” 다섯 개로 읽힌다.

즉 기존 개정은 **배열 순서**는 풀었지만, “8개 이상을 충족하는 보편적 묶음”을 선택하는 문제는 남겼다.

### 2. statement에는 선택 게이트가 없고, metadata가 비어 있어도 이미지 재서술로 채워진다 — 확신 높음

Copy Map의 statement 설명은 다음뿐이다.

> “statement: explain the supplied making/process story in clear, human language.”

그러나 선택 조건에는 `detail_split`, `info_table`, `recommendation`, `usage_scene`, `feature_grid`만 있고 statement의 **포함·생략 조건은 없다**.

실측상 creator making data가 없는 6건 중 5건이 statement를 만들었다. 예를 들어 textile statement는 “작은 사각형들이 … 다이아몬드 형태”라는 이미지 문양 설명이고, box statement는 “동물과 식물 문양 … 황색과 적색의 대비”라는 설명이다. 이는 각각의 feature_grid·detail_split과 같은 관찰을 다른 블록으로 재서술한 것이지 supplied process story가 아니다.

따라서 statement 5/6은 입력이 process story를 제공해서 생긴 것이 아니라, “statement가 선택되면 무엇을 쓸지”만 있고 “언제 선택하지 말아야 하는지”가 없는 프롬프트 결함으로 보는 것이 타당하다.

### 3. 나머지 선택 조건의 문턱이 낮고 서로 중복을 막지 않는다 — 확신 높음

현재 조건은 다음처럼 거의 모든 단일 제품 사진에 성립한다.

> “detail_split requires a real detail photo_id that proves a distinct surface, shape, or process fact”

> “info_table requires image-visible or creator-provided fields”

> “usage_scene requires photo_id lifestyle and a plausible setting that adds information beyond hero and detail”

평가 파이프라인은 여섯 케이스 모두 detail·lifestyle 역할을 제공하고, 모든 제품 사진에는 색·형태·문양 같은 image-visible field가 있다. 그 결과 `detail_split`, `info_table`, `usage_scene`가 6/6으로 선택됐다. 실제 usage 문구도 “서재나 거실의 선반”, “다양한 상황”, “벽걸이 장식이나 소품” 같은 일반 제안이 대부분이며, product-specific use evidence의 강한 판별로 작동하지 않는다.

또한 feature_grid와 info_table 양쪽에 같은 형태·색·문양을 넣어도 막는 규칙이 없다. box는 feature_grid에 직사각형 형태·문양·황적 대비를, info_table에 형태·색채·잠금장치를 다시 넣고, textile도 grid의 기하무늬·줄무늬·색감과 table의 형태·색상을 병행한다. “각 블록은 distinct communication job”이라는 선언만으로는 이 중복을 거르지 못했다.

### 4. 주입되는 참조 가이드의 암묵적 block set을 precedence가 완전히 덮지 못한다 — 확신 중간

`build_reference_guide_prompt()`에는 다음이 남아 있다.

> “Finish with compact basic information, creator-provided care/notice content, and recommendations.”

> “Build the narrative arc as hook → proof → context → use → information → close.”

현재 override 문구는 다음과 같이 **순서만** 대상으로 한다.

> “these constraints override any fixed order implied by the Reference guide contract above.”

따라서 모델은 guide의 information·care/notice·recommendations를 “필요할 법한 블록의 집합”으로 계속 해석할 수 있다. 특히 information/notice를 포함하는 6/6 패턴은 이 해석과 일치한다. 다만 notice는 care data gate로도 강제되므로, 이 가이드만을 6/6 notice의 직접 원인이라고 단정하지는 않는다.

### 5. 입력 동질성은 보조 원인이나, 프롬프트 문제를 면제하지는 않는다 — 확신 높음

여섯 건은 모두 metadata가 없고 care는 `확인 필요`로 귀결되므로 공통 notice와 일부 기본 정보 수렴은 자연스럽다. 그러나 이 사실은 process data가 전혀 없는데 statement가 5/6인 현상, 그리고 grid/table/usage가 같은 일반 근거를 중복해 6/6인 현상을 설명하지 못한다. 입력 동질성은 안전한 block set이 겹칠 가능성을 높이는 **보조 요인**이고, 블록별 생략·중복 게이트 부재가 우선 수정할 프롬프트 원인이다.

## 최소 개정안

수정 대상은 계속 `src/detail_page_ai/prompts.py`의 `build_analysis_prompt()`다. `validation.py`, DTO, renderer, care data gate 및 gallery photo_ids 계약은 바꾸지 않는다.

### A. 8블록 하한을 “첫 계획 예산”으로 명시한다

**Before**

> “page_plan must contain 8 to 12 safe, whitelisted blocks. … Do not add a generic block merely to reach the minimum.”

**After**

```text
page_plan must contain 8 to 12 safe, whitelisted blocks. Build an eight-block plan first:
hero, closing, exactly one gallery, the care-gated notice, and four evidence-qualified
middle blocks. Add a ninth or later block only when it answers a distinct product-specific
question that no selected block already answers. Do not add a generic block merely to reach
the minimum or make the page feel complete.
```

8블록은 hero/closing 사이에 gallery·notice와 선택 블록 네 개, 즉 중간 블록 6개를 보장한다. 따라서 현재 validation 보존 분기를 유지하면서 9번째 범용 블록을 기본값에서 예외로 바꾼다.

### B. Copy Map을 inclusion list가 아닌 사후 참조표로 제한한다

**Before**

> “Section copy reference (content role per block_type; alphabetized for lookup, not a page-plan sequence):”

**After**

> “Section copy reference (content role only after a block type is selected; alphabetized for lookup, not an inclusion list or a page-plan sequence):”

이 한 문장은 “모든 설명된 block_type을 채워야 한다”는 암묵적 해석을 끊는다. 실제 생략 판단은 다음 C의 게이트가 담당한다.

### C. 메뉴를 선택 예산과 상호배타적 evidence gate로 교체한다

**Before (요지)**

> “Select four to eight of them from the product's visible evidence …”

> “Selection conditions: detail_split requires …; info_table requires …; recommendation requires …; usage_scene requires …; When feature_grid is selected …”

**After**

```text
- Evidence budget: first select exactly four menu block types for the eight-block plan.
  Select a ninth or later block only for a non-overlapping, product-specific evidence job.
  A block whose body would repeat another selected block's form, color, pattern, or use claim
  is not evidence-qualified.
- Selection gates (alphabetized; these are not page order): detail_split requires a real detail
  crop with a surface, construction, or process fact not already carried by feature_grid or
  info_table; feature_grid requires three independent visible facts not repeated by detail_split
  or info_table; info_table requires at least three discrete creator-provided or image-visible
  facts that are not generic form/color restatements and are not already feature cards;
  recommendation requires at least two distinct, product-specific styling suggestions, not
  generic table, shelf, light, or background advice; statement requires supplied making_method
  or a real process image with visible tools, hands, or making action, and must never restate
  visual form, color, or pattern; usage_scene requires a product-specific use or scale context
  beyond generic placement, and lifestyle availability alone is not evidence.
- When fewer than four candidates pass the gates, prefer a selected archetype's best-supported
  wide_image, palette, or scale_reference before duplicating a claim. When more than four pass,
  choose the four that best distinguish this product from a generic catalog page.
- When feature_grid is selected, use three concise feature cards with distinct observations.
```

이 변경은 선택 가능한 type을 줄이지 않는다. 대신 statement·grid·table·detail·usage가 같은 시각 문장을 반복하는 경우 하나만 남기고, texture/silhouette/set 특성이 실제로 강한 상품에는 palette/wide_image/scale_reference 같은 보완 type을 고를 통로를 만든다. 8블록의 네 선택 슬롯은 그대로라 validation fallback을 피한다.

### D. Reference guide의 시각·카피 역할과 page_plan block 선택을 분리한다

**Before**

> “Page-plan selection precedence: for page_plan, these constraints override any fixed order implied by the Reference guide contract above.”

**After**

> “Page-plan selection precedence: for page_plan, these constraints override any fixed page-plan order or implied block set in the Reference guide contract above. The guide controls visual and copy direction only; it does not require a page_plan block_type.”

이는 guide의 hook/proof/use/information 서사와 종결부를 시각적 방향으로 보존하되, information·recommendation 등을 모든 상품의 기본 block set으로 읽는 경로를 차단한다.

## 검증 가능한 예측

다음 재생성은 같은 여섯 이미지, 같은 모델 조건, 동일한 빈 `user_hints`를 사용해 `result_summary.json`의 `product.page_plan`을 집계한다.

1. 기존 합격 기준: 전체 `block_type` 시퀀스는 **최소 3종**, 최빈 시퀀스는 **최대 2/6**이어야 한다.
2. 순서를 무시한 `block_type` 집합도 **최소 3종**, 단일 집합의 빈도는 **최대 2/6**이어야 한다. 현재는 집합 2종, 최빈 5/6이다.
3. 여섯 계획은 모두 **8~9블록**이어야 하며, **최소 3/6은 정확히 8블록**이어야 한다. 9블록 계획은 네 선택 슬롯을 넘는 블록이 다른 selected block과 겹치지 않는 product-specific evidence job을 가져야 한다. 7블록 이하는 허용하지 않는다.
4. 이 배치에는 `making_method`와 process image가 없으므로 `statement`는 **0/6**이어야 한다. `feature_grid`와 `info_table`을 동시에 쓰는 계획은 두 블록의 facts가 겹치지 않는 경우만 허용하며, 이 배치에서는 **최대 2/6**이어야 한다.
5. 모든 계획은 hero 첫 번째, closing 마지막, 허용된 block_type, DTO의 최대 14블록을 지켜야 한다. gallery가 있는 계획은 기존 `photo_ids` 5개 계약을 유지하고, `care_guide`가 없는 모든 입력의 notice는 기존 정확한 `확인 필요` 문구를 유지해야 한다.

## 위험과 완화

| 위험 | 영향 | 완화 |
|---|---|---|
| 게이트가 너무 엄격해 네 menu block을 못 고름 | 총 7블록 이하이면 중간 6개 미만이 되어 validation fallback이 다시 삽입·재배열할 수 있음 | 8블록 예산(선택 4개)을 유지하고, 부족할 때는 중복 대신 archetype에 맞는 `wide_image`/`palette`/`scale_reference`를 우선 검토하게 한다. 재생성에서 모든 계획의 길이와 middle 길이를 함께 집계한다. |
| set 다양성 목표가 근거 없는 임의 블록을 유도 | 카피 중복·환각·안전성 저하 | 목표를 “제품별 non-overlapping evidence job”에 종속한다. 단순히 metric을 맞추려 가짜 recommendation·usage를 추가하지 않으며, 각 9번째 블록은 본문 근거로 검수한다. |
| statement gate가 metadata 없는 상품의 서사를 줄임 | 페이지가 건조해질 수 있음 | statement로 분리할 process가 없을 때는 hero/detail/feature copy가 이미지 사실을 담당하게 한다. process data가 있는 실제 상품에는 statement를 계속 허용한다. |
| reference guide 우선순위 축소 | 일관된 편집 리듬이 약해질 수 있음 | guide의 typography, 색, 이미지/카피 방향은 그대로 유지한다. block 선택만 현재 프롬프트의 evidence gate가 최종 결정한다. |
| 8~12 요구와 DTO/renderer 제약 불일치 | parse 또는 렌더 문제 | 제안 범위는 8~9이며 `ProductProfileDto.page_plan`의 max 14 안에 있다. hero/closing·gallery photo_ids·care notice 조건은 유지한다. |

이 문서는 제안만 담으며 `prompts.py`와 그 밖의 소스는 변경하지 않았다.
