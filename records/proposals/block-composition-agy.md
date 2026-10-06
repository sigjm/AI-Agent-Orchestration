# 블록 구성 고정 원인 진단과 프롬프트 최소 개정안

- 작성자: 워커 agy
- 작성일시: 2026-09-10 11:50:00
- 대상 파일: `src/detail_page_ai/prompts.py` (`build_analysis_prompt`)

---

## 1. 진단 (Diagnosis)

### 1.1 현상 실측 요약 (`pilot-20260910-111715`)
이전 개정(Copy Map 알파벳화, 하한 9→8 조정, 선택 메뉴 도입)으로 **시퀀스 순서**는 3종으로 분기되었으나, **블록 구성(집합)과 총 블록 수**는 여전히 굳어져 있습니다.

```text
textile     (9블록): hero statement feature_grid detail_split gallery usage_scene info_table notice closing
box         (9블록): hero statement detail_split feature_grid gallery usage_scene info_table notice closing
metalware   (9블록): hero statement feature_grid detail_split gallery usage_scene info_table notice closing
ceramic     (9블록): hero statement detail_split feature_grid gallery usage_scene info_table notice closing
furniture   (9블록): hero statement feature_grid detail_split gallery usage_scene info_table notice closing
jewelry     (9블록): hero feature_grid detail_split usage_scene gallery recommendation info_table notice closing
```

- **블록 개수 완전 고정**: 6건 전수가 **정확히 9블록** (8블록 선택률 0%).
- **블록 집합 실질적 단일화**:
  - 공예품 5건은 집합이 100% 동일: `{hero, statement, feature_grid, detail_split, gallery, usage_scene, info_table, notice, closing}`
  - 장신구(jewelry) 1건만 `statement` 대신 `recommendation`을 치환했을 뿐, 핵심 7개 블록이 모든 케이스에 공통 포함됨.

---

### 1.2 원인 분석 및 확신 수준

#### 원인 1: 가용 메뉴(9개) 중 현실적으로 선택 가능한 블록이 5~6개로 제한됨 [확신도: 확실]
현재 프롬프트 170~173행의 `Evidence-led menu`는 9개 블록을 메뉴로 제시합니다:
> **[원문 인용] (`src/detail_page_ai/prompts.py:170-173`)**
> ```text
> - Evidence-led menu: treat detail_split, feature_grid, info_table, palette, recommendation,
>   scale_reference, statement, usage_scene, and wide_image as a menu, not a checklist. Select four
>   to eight of them from the product's visible evidence and chosen archetype; every selected block
>   must have a distinct communication job. Do not select or order blocks by the order in this prompt.
> ```

그러나 9개 메뉴 항목 중 3개는 실제 실행 환경에서 **구조적으로 선택 불가능(Dead Options)**합니다:
1. `scale_reference`: 프롬프트 207행(`Do not infer small size without a scale reference`) 및 157행(`Remove any section whose claim lacks image evidence`)에 의해, 치수 기준자(ruler)가 없는 CMA 박물관 이미지 특성상 선택이 엄격히 차단됨.
2. `wide_image`: 어떤 이미지 자산(`photo_id`)을 써야 하는지, `hero`와 무엇이 다른지 역할 정의가 전무함.
3. `palette`: 166행(`A palette is optional and must never replace the gallery`)에서 소극적 선택지로 밀려나 있어 LLM이 색상 hex/명칭 환각 위험을 피해 기피함.

결국 모델에게 실질적으로 남은 메뉴는 `detail_split`, `feature_grid`, `info_table`, `usage_scene`, `statement`, `recommendation`의 **단 6개**뿐입니다.
4개의 필수 뼈대(`hero`, `gallery`, `notice`, `closing`)에 최소 8블록을 맞추려면 메뉴에서 최소 4~5개를 골라야 하므로, **수학적으로 6개 중 5개를 고를 수밖에 없어 모든 케이스가 동일한 집합으로 수렴**하게 됩니다.

---

#### 원인 2: 블록별 설명이 '내용 서술법'일 뿐 '생략/배제 조건'이 전혀 없음 [확신도: 확실]
현재 프롬프트 174~180행의 `Selection conditions`와 61~73행의 `Section copy reference`는 각 블록을 넣었을 때 **어떤 내용을 적어야 하는가(내용 가이드)**만 규정하고 있을 뿐, **어떤 조건에서 이 블록을 빼야 하는가(생략/배제 조건)**가 없습니다:

> **[원문 인용] (`src/detail_page_ai/prompts.py:174-180`)**
> ```text
> - Selection conditions: detail_split requires a real detail photo_id that proves a distinct surface,
>   shape, or process fact; info_table requires image-visible or creator-provided fields and uses
>   "확인 필요" rather than inventing missing dimensions, materials, price, maker, or origin;
>   recommendation requires at least two non-generic product-specific styling suggestions; usage_scene
>   requires photo_id lifestyle and a plausible setting that adds information beyond hero and detail,
>   never proof of actual performance. When feature_grid is selected, use three concise feature cards
>   with distinct observations.
> ```

- `detail_split`: "실제 디테일 사진이 필요하다" → 6건 모두 `03-detail.jpg`가 있으므로 무조건 선택됨.
- `info_table`: "시각적 확인 사실을 적고 미확인은 확인필요로 둔다" → 모든 제품에 적용 가능하므로 무조건 선택됨.
- `usage_scene`: "그럴듯한 연출 배경을 적는다" → 6건 모두 `04-lifestyle.png`가 있고 연출 제안이 가능하므로 무조건 선택됨.
- `feature_grid`: "3장의 카드를 쓴다" → 루트 DTO에서 이미 3대 feature를 추출했으므로 무조건 선택됨.
- `statement`: **선택 조건에서 아예 누락되어 있음!** 제작과정 데이터(`howMade`)가 없는데도 공예품 5건 모두에서 문양·색채 묘사 카피로 채워져 무조건 선택됨.

LLM은 "넣을 수 있는 근거(사진, 시각 사실)가 존재하고 생략하라는 지침이 없으면, 상세한 페이지를 만들기 위해 전부 집어넣는" 기본 속성(Additivity)을 가집니다. 생략 규칙이 없으니 5개 핵심 블록이 전부 필수가 됩니다.

---

#### 원인 3: 아키타입 선호(Archetype Preferences)의 식별력 상실 [확신도: 확실]
> **[원문 인용] (`src/detail_page_ai/prompts.py:181-183`)**
> ```text
> - Archetype preferences, not required bundles: silhouette-led favors wide_image or scale_reference;
>   texture-led favors detail_split or palette; set-led favors feature_grid, gallery, or info_table;
>   process-led favors statement and detail_split.
> ```

현재 아키타입 선호 지침은 상품군별 분기 기능을 완전히 상실했습니다:
- `silhouette-led`가 선호하는 `wide_image`, `scale_reference`는 위 원인 1에 의해 선택 불가 → 결국 디폴트 집합으로 후퇴.
- `texture-led`가 선호하는 `detail_split`은 모든 상품이 선택함.
- `set-led`가 선호하는 `feature_grid, gallery, info_table`도 모든 상품이 선택함.
- `process-led`가 선호하는 `statement, detail_split` 중 `statement`는 제작 데이터가 없는데도 남용됨.
즉, 4개 아키타입 중 무엇을 선택하든 **결과 블록 집합이 똑같아지도록 선호 목록이 설계**되어 있습니다.

---

#### 원인 4: 하한선 8의 경계 기피 심리 (Range Edge Avoidance) [확신도: 유력]
> **[원문 인용] (`src/detail_page_ai/prompts.py:141, 171`)**
> ```text
> page_plan must contain 8 to 12 safe, whitelisted blocks.
> Select four to eight of them from the product's visible evidence and chosen archetype;
> ```

- 필수 뼈대 4개(`hero`, `gallery`, `notice`, `closing`)에 메뉴 4개를 더하면 정확히 8개입니다.
- 그러나 LLM에게 "8 to 12", "Select 4 to 8"이라는 범위를 주면, 하한선 경계값(8개, 4개)은 "최소 요구조건 미달로 실패할 위험이 있는 경계"로 인식됩니다.
- 모델은 안전 마진을 두기 위해 메뉴에서 4개가 아닌 5개를 선택하여 `4 + 5 = 9블록`에 고착됩니다.

---

#### 원인 5: 입력 데이터의 대칭성 (CMA 데이터셋의 메타데이터 부재) [확신도: 확실]
- 6건 모두 클리블랜드 미술관 소장품으로, 사용자 입력 메타데이터(`product_name`, `making_method`, `care_guide`)가 100% `(none)`입니다.
- 모든 케이스가 동일하게 [1장 원본 + 누끼 + 크롭 + Flux 연출컷 1장 + 참고컷 4장]의 균일한 자산 구조를 가집니다.
- 입력 정보가 동일하므로, **프롬프트가 "어떤 경우에 어떤 블록을 빼고 어떤 블록을 넣어야 하는지" 명시적 배타/생략 조건(Mutually Exclusive Conditions)을 주지 않는 한, 모델이 자발적으로 서로 다른 구성을 내놓을 이유가 없습니다.**

---

## 2. 개정안 (Proposal)

최소 변경 원칙에 따라 `src/detail_page_ai/prompts.py`의 `build_analysis_prompt()` 중 170~186행의 `Evidence-led menu`, `Selection conditions`, `Archetype preferences` 섹션만 집중 개정합니다.

### 핵심 변경 내용
1. **8블록을 디폴트 기준으로 명시**: "기본 8블록(필수 4 + 메뉴 4), 명확한 추가 근거가 있을 때만 9~10블록"으로 기준점(Anchor)을 재조정.
2. **배타적 생략/선택 규칙(Inclusion/Omission Rules) 도입**:
   - `statement`: 제작과정(`howMade`) 데이터가 제공된 경우에만 포함. 미제공 시 **반드시 생략** (외형 묘사로 채우지 말 것).
   - `palette`: 직물·회화 등 색상 대비와 조화가 핵심인 상품에서 `usage_scene` 대신 또는 추가로 선택.
   - `recommendation`: 가구·상자·장신구 등 공간 소품/스타일링 중심 상품에서 `detail_split`(미세 질감) 대신 또는 보조로 선택.
   - `detail_split`: 양각, 투각, 직조 등 표면 마크로 질감이 두드러진 상품에서 선택.
3. **아키타입별 차별화된 4블록 메뉴 번들 제시**:
   - 4대 아키타입이 실제로 서로 다른 메뉴 조합(각 4개)을 선택하도록 구체화.

---

### [Before] (`src/detail_page_ai/prompts.py:170-186`)
```python
- Evidence-led menu: treat detail_split, feature_grid, info_table, palette, recommendation,
  scale_reference, statement, usage_scene, and wide_image as a menu, not a checklist. Select four
  to eight of them from the product's visible evidence and chosen archetype; every selected block
  must have a distinct communication job. Do not select or order blocks by the order in this prompt.
- Selection conditions: detail_split requires a real detail photo_id that proves a distinct surface,
  shape, or process fact; info_table requires image-visible or creator-provided fields and uses
  "확인 필요" rather than inventing missing dimensions, materials, price, maker, or origin;
  recommendation requires at least two non-generic product-specific styling suggestions; usage_scene
  requires photo_id lifestyle and a plausible setting that adds information beyond hero and detail,
  never proof of actual performance. When feature_grid is selected, use three concise feature cards
  with distinct observations.
- Archetype preferences, not required bundles: silhouette-led favors wide_image or scale_reference;
  texture-led favors detail_split or palette; set-led favors feature_grid, gallery, or info_table;
  process-led favors statement and detail_split.
Use dark for selected detail_split and notice, full-bleed for selected usage_scene, sand for palette
when present, and paper for hero and closing. Vary optional blocks and their order when the evidence
calls for it; do not copy one fixed middle sequence for every product.
```

### [After] (`src/detail_page_ai/prompts.py:170-186`)
```python
- Evidence-led menu: exactly four required blocks form the outer frame (hero, gallery, notice, closing).
  From the menu (detail_split, feature_grid, info_table, palette, recommendation, statement, usage_scene),
  select exactly four (default: 8 blocks total) to five (9 blocks total) blocks based on the archetype.
  Do not include all blocks; choose an intentional subset so different products have distinct block sets.
- Strict inclusion and omission conditions:
  * statement: include ONLY when creator-provided making_method (howMade) is supplied. If making data
    is absent, OMIT statement entirely (do not invent a making story or rewrite appearance as a statement).
  * palette: select for colorful textiles, multi-tone lacquer, or polychrome crafts; omit for monotone items.
  * recommendation: select for lifestyle, furniture, boxes, or jewelry needing concrete styling/placement ideas;
    it may replace detail_split when overall silhouette and placement matter more than micro-surface texture.
  * detail_split: select when distinct carved, woven, or embossed surface texture exists; omit if covered by gallery.
  * usage_scene: select when in-situ spatial context adds clear value beyond the hero image.
  * info_table: select when at least 3 concrete product specifications can be verified or explicitly marked "확인 필요".
- Archetype block sets (select 4 middle blocks to reach 8 blocks total, or 5 for 9 blocks):
  * texture-led (textile, relief ceramic, engraved metal): detail_split + feature_grid + palette (or usage_scene) + info_table
  * silhouette-led (furniture, storage box, architectural vessel): usage_scene + feature_grid + recommendation + info_table
  * set-led (jewelry, small accessory, ornament): feature_grid + detail_split + recommendation + info_table
  * process-led (only when howMade is present): statement + detail_split + feature_grid + info_table
Use dark for selected detail_split and notice, full-bleed for selected usage_scene, sand for palette
when present, and paper for hero and closing.
```

---

## 3. 검증 가능한 예측 (Testable Predictions)

다음 파일럿 재생성(`pilot-run`)에서 확인할 정량적 지표:

1. **블록 수 다양화 (8블록 출현)**:
   - 현재: 9블록 100% (6/6).
   - 예측: **8블록 케이스가 최소 3건 이상 (3/6 ~ 5/6)** 출현.
   - 근거: CMA 6건 모두 `howMade`가 없으므로 `statement`가 규칙에 따라 탈락하여 자연스럽게 8블록으로 슬림화됨.
2. **블록 집합(Block Set) 다양성**:
   - 현재: 2종 (공예 5건 동일, jewelry 1건만 다름).
   - 예측: **최소 3종 이상의 서로 다른 고유 블록 집합** 출현.
     - 집합 A (texture-led): `{hero, detail_split, feature_grid, palette (또는 usage_scene), gallery, info_table, notice, closing}` (textile, ceramic 등)
     - 집합 B (silhouette-led): `{hero, usage_scene, feature_grid, recommendation, gallery, info_table, notice, closing}` (box, furniture 등, `detail_split` 생략)
     - 집합 C (set-led): `{hero, feature_grid, detail_split, gallery, recommendation, info_table, notice, closing}` (jewelry)
3. **시퀀스 다양성 지표 달성**:
   - **고유 시퀀스 수: 3종 이상** 유지 (예상: 3~4종).
   - **최빈 시퀀스 빈도: 2/6 이하 달성** (목표 합격선 통과).
4. **Statement 블록의 정밀 정제**:
   - CMA 6건 중 `statement`를 포함하는 케이스가 0건(또는 최대 1건)으로 감소 (메타 없는 상품의 억지 서술 제거).

---

## 4. 위험과 완화책 (Risks & Mitigations)

1. **`validation.py`의 `len(middle) < 6` Fallback 발동 위험 (치명적)**:
   - 만약 모델이 블록을 너무 적극적으로 생략하여 총 7블록 이하(`len(middle) <= 5`)를 반환하면, `validation.py`의 145~250행이 작동하여 모델의 구성을 무시하고 누락된 블록들을 강제로 다시 채워 넣어 원점으로 회귀함.
   - **완화책**: 개정안에서 "select exactly four (default: 8 blocks total)"로 명시하여, 메뉴에서 반드시 4개 이상을 선택하도록 유도. `4(필수) + 4(메뉴) = 8블록`을 확보하여 중간 블록 수 `len(middle) == 6`을 보장함.
2. **DTO 제약 (`max_length=14`)**:
   - 제안된 구성은 8~9블록이므로 14블록 한도에 전혀 저촉되지 않음.
3. **렌더러 호환성**:
   - `palette`가 새로 선택될 경우 `react_document_builder.py`의 `_DEFAULT_PHOTO_BY_BLOCK["palette"] = "detail"` 및 `_VARIANT_COLORS["sand"]`가 정상 구현되어 있으므로 렌더링 에러 없이 아름다운 샌드 톤 컬러 카드로 조판됨.
   - `recommendation` 선택 시에도 기존 DTO 및 렌더러가 완벽히 지원함.
4. **입력 데이터 결손 시의 안정성**:
   - `howMade`가 주어지는 실제 판매자 상품 데이터가 유입될 경우, `statement` 조건이 정상 발동하여 자연스럽게 `process-led`(9블록)로 분기되므로 향후 확장성 완벽 보장.
