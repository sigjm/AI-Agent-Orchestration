# 수정 — 생성 활용 장면을 쓰는 레이아웃이 뽑히게 한다

## 관리자 결정
생성 컷을 만들었으면 **페이지가 쓰도록** 한다. 구체적으로 **`usage_scene` 블록이 뽑히게** 한다.

## 지금 구조 (확인됨)
- `select_layout_archetypes()`(`src/detail_page_ai/layout_archetypes.py:42`)가 카탈로그 25종에서 **이미지 sha256 을 시드로 4종을 표본 추출**해 모델에 예시로 보여준다 (`src/local_detail_page_ai/adapters.py:75`)
- 모델은 그 예시를 참고해 `page_plan` 블록 순서를 만든다
- 카탈로그 25종 중 **`usage_scene` 을 포함한 것은 16종**이다
- 부채 세트 2회 실행에서 표본에 들지 않아 `usage_scene` 이 선택되지 않았고, 생성한 활용 장면(`lifestyle`)이 페이지에 쓰이지 않았다

## 담당 파일
- `src/detail_page_ai/layout_archetypes.py`
- `src/local_detail_page_ai/adapters.py` (표본 추출 호출부)
- 필요하면 `src/detail_page_ai/prompts.py` (지시문)
- `tests/`

## 바꿀 것
**이미지 생성이 켜져 있을 때는 `usage_scene` 을 포함한 원형이 표본에 반드시 들어가게** 한다.

- 이미지 생성이 꺼져 있으면(`LOCAL_IMAGE_PROVIDER=none` 또는 생성 상한 0) **지금 동작 그대로** 둔다. 쓸 수 없는 블록을 권할 이유가 없다
- 켜져 있으면 표본 4종 중 **최소 1종은 `usage_scene` 을 포함**하게 한다. 나머지는 지금처럼 뽑는다
- **시드 기반 재현성을 유지**하라. 같은 이미지·같은 조건이면 같은 표본이 나와야 한다 (`random.Random(image_sha256)`)
- 다양성을 죽이지 마라. `usage_scene` 포함 16종 중에서 **고정된 하나를 항상 쓰지 말고** 시드로 골라라

표본에 넣는 것만으로 모델이 반드시 채택한다는 보장은 없다. 프롬프트에 **"활용 장면 사진이 제공되면 usage_scene 블록을 포함하라"** 는 취지의 지시를 더해도 좋다. 다만:
- **없는 사진을 쓰라고 지시하지 마라.** 생성이 꺼져 있을 때는 이 지시가 나가면 안 된다
- 기존 지시문(입력 데이터 우선, evidence 규칙 등)을 바꾸지 마라

## 하지 말 것
- 카탈로그(`assets/references/detail-page-layouts.json`)를 수정하지 마라
- `LayoutId` 리터럴(`editorial-split`·`image-first`·`catalog-grid`)을 바꾸지 마라. 별개 체계다
- `_DEFAULT_PHOTO_BY_BLOCK` 을 바꾸지 마라
- page_plan 을 사후에 강제로 조작하지 마라. **표본과 지시로 유도**하는 것까지가 이번 범위다

## 테스트
- 이미지 생성이 켜진 조건 → 표본 4종 중 `usage_scene` 포함이 최소 1종
- 이미지 생성이 꺼진 조건 → 기존 동작과 동일 (표본 구성이 달라지지 않음)
- 같은 `image_sha256` 으로 두 번 호출 → 같은 표본 (재현성)
- 서로 다른 sha256 → `usage_scene` 포함 원형이 **매번 같은 것 하나로 고정되지 않는다**

기존 테스트를 통과시키려고 지우거나 완화하지 마라.

## 검증
`.venv/bin/python -m pytest -q` → **381 이상**

## 보고
`## 결과` 에 바꾼 방식, 재현성을 어떻게 유지했는지, 추가 테스트를 적고, 마지막 줄에 `완료: 테스트 N passed` 출력.
