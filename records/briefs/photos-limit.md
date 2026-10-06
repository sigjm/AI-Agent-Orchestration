# 설정 재정의 — 죽은 임계값을 "보조 생성 컷 장수 상한"으로

## 배경
`07ce5da` 로 사진 배정 방식을 바꾸면서 `SOURCE_PHOTO_VARIATION_THRESHOLD` 가 **아무 분기도 가르지 않는 죽은 설정**이 됐다. 값만 보관된다(`source_photos.py:678-691`). 관리자 결정으로 **이 설정에 실제 의미를 준다.**

## 담당 파일
- `src/detail_page_ai/source_photos.py`
- `src/detail_page_ai/config.py`
- `src/local_detail_page_ai/factory.py`
- `.env.example`
- `tests/` 중 이 설정을 참조하는 것 (`test_source_photos.py`, `test_config.py`, `test_app.py`, `test_security.py` 등)

`docs/` 는 다른 워커가 동시에 고치는 중이니 **열지 말 것.**

## 확정 사양

### 이름
`SOURCE_PHOTO_VARIATION_THRESHOLD` → **`MAX_GENERATED_PHOTOS`**
설정 속성 `source_photo_variation_threshold` → **`max_generated_photos`**

구 이름은 남기지 않는다. 이 값은 **우리 서비스 내부 설정**이고 아직 아무 곳에도 배포되지 않았다.

### 의미
**한 세트에 붙일 보조 생성 컷의 최대 장수.** 제공 사진으로 채우지 못한 역할을 메우는 생성과, 활용 장면·디테일 뷰 같은 보조 생성 컷을 모두 합쳐 이 수를 넘지 않는다.

- 범위: **0 이상 12 이하**
- 기본값: **5** — 지금 동작(활용 장면 1 + 디테일 뷰 4)을 그대로 보존하는 값이다
- **0 이면 생성을 전혀 하지 않는다.** 제공 사진만으로 세트를 구성한다
- 채우는 순서: 역할을 메우는 생성 → 활용 장면 → 디테일 뷰. 상한에 닿으면 거기서 멈춘다

`0` 을 허용하는 것이 중요하다. BE 팀 계약서는 "AI 이미지 생성 없음"을 전제하고 있어, 협의 결과에 따라 이 값 하나로 그 동작을 만들 수 있어야 한다. `config.py` 의 `ge=` 제약을 `ge=0` 으로 바꿔야 한다.

### 기존 동작 보존
기본값 5 에서 **`07ce5da` 직후와 완전히 동일한 결과**가 나와야 한다. 입력 1·2·3·4장에 대해 사진 구성이 달라지면 회귀다.

## 지켜야 할 계약
- `photo_id` 는 한 세트 안에서 유일 (`lifestyle-02` 포함)
- 제공 사진은 한 장도 버리지 않는다. 역할을 넘으면 `alternate`
- `asset_mode`·`fidelity_status`·`product_generated` 의미 불변
- 생성 컷은 `product_generated=True`

## 테스트
- `MAX_GENERATED_PHOTOS=0` → 생성 자산이 **0개**, 제공 사진만 나온다
- `=1` → 보조 생성 컷이 정확히 1장 (활용 장면)
- 기본값 `=5` → 입력 1·2·3·4장 결과가 `07ce5da` 와 동일
- 상한을 넘겨도 `photo_id` 유일성이 유지된다
- 범위 밖(`-1`, `13`)은 설정 검증에서 거부된다

기존 테스트를 통과시키려고 삭제·완화하지 말 것. 구 이름을 쓰던 테스트는 새 이름으로 고치되 **검증 내용은 유지**할 것.

## 검증
`.venv/bin/python -m pytest -q` → **362 이상**. 줄면 회귀다.
`grep -rn "SOURCE_PHOTO_VARIATION_THRESHOLD\|source_photo_variation_threshold" src/ tests/ .env.example` → **0건**

## 보고
`## 결과` 에 바꾼 파일·행, 추가 테스트, 기본값 5에서 기존 동작이 보존됨을 어떻게 확인했는지 적고, 마지막 줄에 `완료: 테스트 N passed` 출력.
