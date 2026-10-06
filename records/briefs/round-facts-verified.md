# 차수별 실측 검증표 (오케스트레이터 재측정, 2026-09-10)

아래는 각 파일럿 디렉터리에 대해 현재 `scripts/check_plan_diversity.py` 를 다시 돌려
얻은 실측값이다. **문서에 쓰는 수치는 이 표를 따른다.** 기억이나 기존 문서 문장이
이 표와 다르면 이 표가 맞다.

## 1. 구성 다양성 지표

| 차수 | 파일럿 | 평균 Jaccard | 유효 공통 블록 | 완전 일치 쌍 | 고유 시퀀스 | 최빈 반복 | 길이 분포 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | pilot-20260909-224737 | 96.7% | 7종 | 10쌍 | 2종/6건 | 5회 | 9블록 1, 10블록 5 |
| 1차 | pilot-20260910-102346 | 96.3% | 6종 | 10쌍 | 2종/6건 | 5회 | 8블록 1, 9블록 5 |
| 2차 | pilot-20260910-111715 | 93.3% | 6종 | 10쌍 | 3종/6건 | 3회 | 9블록 6 |
| 3차 | pilot-20260910-115722 | 78.3% | 4종 | 2쌍 | 4종/6건 | 2회 | 8블록 5, 9블록 1 |
| 4차 | pilot-20260910-123917 | 79.8% | 4종 | 3쌍 | 6종/6건 | 1회 | 8블록 6 |
| 5차 | pilot-20260910-135605 | 72.4% | 4종 | 1쌍 | 5종/6건 | 2회 | 8블록 3, 10블록 3 |
| 6차 | pilot-20260910-145007 | 72.4% | 4종 | 1쌍 | 5종/6건 | 2회 | 8블록 3, 10블록 3 |
| 7차 | pilot-20260910-153208 | 72.4% | 4종 | 1쌍 | 4종/5건 | 2회 | 8블록 2, 10블록 3 |
| 8차 | pilot-20260910-161310 | 66.0% | 1종 | 2쌍 | 4종/6건 | 2회 | 8블록 4, 9블록 2 |
| 9차 | pilot-20260910-164008 | 52.3% | 0종 | 0쌍 | 6종/6건 | 1회 | 8블록 5, 9블록 1 |

"유효 공통 블록"은 DTO가 구조적으로 고정하는 `hero`/`closing` 을 **제외한** 종수다.
기존 문서에 "공통 6종" 같은 표현이 있으면 그것은 `hero`/`closing` 을 포함한 총계이므로
유효 종수(위 표)와 함께 병기하거나 유효 종수로 통일하라.

차수별 유효 공통 블록 목록:
- baseline: detail_split, feature_grid, gallery, info_table, notice, recommendation, usage_scene
- 1차: detail_split, feature_grid, gallery, info_table, notice, usage_scene
- 2차: detail_split, feature_grid, gallery, info_table, notice, usage_scene
- 3차: detail_split, feature_grid, gallery, notice
- 4차: detail_split, feature_grid, gallery, notice
- 5차/6차/7차: detail_split, info_table, notice, usage_scene
- 8차: wide_image
- 9차: (없음)

## 2. 실행 메타데이터

| 차수 | 성공/총 | 소요 | 이미지 재생성 |
| --- | --- | --- | --- |
| baseline | 6/6 | 31.3분 | 예 |
| 1차 | 6/6 | 28.2분 | 예 |
| 2차 | 6/6 | 27.8분 | 예 |
| 3차 | 6/6 | 27.3분 | 예 |
| 4차 | 6/6 | 27.1분 | 예 |
| 5차 | 6/6 | 26.6분 | 예 |
| 6차 | 6/6 | 27.3분 | 예 |
| 7차 | **5/6** | 11.0분 | 아니오 (6차 이미지 재사용) |
| 8차 | 6/6 | 11.7분 | 아니오 (6차 이미지 재사용) |
| 9차 | 6/6 | 27.6분 | 예 |

모델은 전 차수 동일: text `ddalcu/Qwen3.8-27B-MLX-Serve-4bit`,
image `mlx-community/flux2-klein-9b-4bit`.

## 3. 앞서 내려간 브리프의 오류 정정

- **1차를 "지표 변화 없음"이라고 쓴 것은 틀렸다.** 평균 Jaccard 96.7% → 96.3%,
  유효 공통 7종 → 6종으로 미세하게 움직였고 완전 일치 쌍 10쌍은 그대로였다.
  "패딩 제거가 구성 수렴을 풀지 못했다"가 정확한 기술이다.
- **5차·6차·7차의 구성 지표는 완전히 동일하다** (72.4% / 4종 / 1쌍). 6차와 7차는
  구성이 아니라 variant 표현 계층만 바꾼 차수임을 문서에 명시하라.
- **7차는 6/6이 아니라 5/6이다. 다만 실패 원인은 두 사건이 별개다.** (오케스트레이터가
  하나로 뭉뚱그려 기술했던 것을 정정한다.)
  - 사건 A — 폐기된 선행 실행 `pilot-20260910-152852`: `--no-product-photos` 를
    "이미지 생성 생략"으로 오인해 사용했고 실행이 중단돼 `run_index.json` 조차 남지
    않았다(디렉터리가 비어 있다). 이후 구조 실행은 `--image-provider none` 만 쓴다.
  - 사건 B — 채택된 실행 `pilot-20260910-153208` 의 1건 실패: 케이스
    `analysis-cma-122443` 이 `LocalModelError: Local vision model response does not
    match ProductProfileDto` 로 죽었다. 근본 원인은 `--no-product-photos` 와 무관하며,
    로컬 텍스트 모델이 `keywords` 를 9개 반환해 `src/detail_page_ai/dto.py:167` 의
    `max_length=8` 을 위반한 Pydantic `too_long` 검증 실패다.
  두 사건 모두 7차 02-error-analysis.md 에 별개 사건으로 기록해야 한다.
- **"6차 이미지 재사용"이라는 표현 자체가 부정확하다.** 실제로 7·8차는 6차 자산을
  복사해 온 것이 아니라 `--image-provider none` 으로 **AI 이미지 생성을 끄고** 돌렸다.
  - 6차 `145007`, 9차 `164008`: per-case `image_model` = `mlx-community/flux2-klein-9b-4bit`.
    케이스당 사진 8장. 실제 생성 수행(27.3분·27.6분).
  - 7차 `153208`: per-case `image_model` = `none`. **`photos/` 가 전 케이스 0장**이다.
    그래서 `check_cutout_fidelity.py` 는 이 차수에서 `[FAIL] MISSING_OUTPUT 6건` 을 낸다.
    컷아웃 지표를 이 차수 성과로 인용하지 마라.
  - 8차 `161310`: per-case `image_model` = `none`. 케이스당 4장 또는 8장이 남았는데
    전부 `asset_mode` 가 `source_composite`/`source_crop` 이고 `product_generated` 는
    `false` 다. 즉 원본 사진에서 결정적으로 파생한 컷이며 AI 생성물이 아니다.
    6차와 `01-hero`/`02-packshot`/`03-detail` 이 바이트 동일한 것은 재사용이 아니라
    같은 원본에 같은 연산을 했기 때문이다. 컷아웃 게이트는 OK 6건.
  - `run_index.json` 의 **최상위** `image_model` 은 설정값이라 전 차수 flux2 로 보인다.
    실제로 무엇이 돌았는지는 반드시 **케이스별** `image_model` 을 봐야 한다.
- 9차 variant 분포: light 15 / paper 14 / compact 6 / image-left 5 / sand 3 /
  image-right 3 / full-bleed 2 / dark 1.
- 9차 컷아웃 게이트: 총 6건, OK 6건, 부분 손실 0, 심각 손실 0 (ALL_OK).

## 4. variant 출력 분포 실측

- 7차 `pilot-20260910-153208` (성공 5건, 블록 46개):
  paper 18 / light 7 / sand 5 / compact 5 / image-left 3 / image-right 3 /
  full-bleed 3 / dark 2. 8종 전량 사용.
- 9차 `pilot-20260910-164008` (6건, 블록 49개):
  light 15 / paper 14 / compact 6 / image-left 5 / sand 3 / image-right 3 /
  full-bleed 2 / dark 1. 8종 전량 사용.
