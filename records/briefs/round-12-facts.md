# 12차 기록용 실측 정본 (오케스트레이터 검증)

주제: hero 원본 고정, rembg 누끼 채택, '참고용' 표시 제거, 누끼+생성배경 합성 시도(반려)
커밋 범위: `cf8a4b1..cfd60bb` — `492e776` (hero 원본), `cfd60bb` (rembg + 참고용 제거 + 워커 등록부 수정)

## 1. 판매 상품 사진 첫 적용
- 입력 1: `~/Downloads/c61a0f801dba776b47ad64eb24762511.jpg` 나전칠기 상자, 1060×1060.
- 입력 2: `~/Downloads/3811a2b462822a91caa1ffc8321b0af3.jpg` 반투명 꽃잎 장식, 1060×1060.
- 나전칠기 분석(`generated/attached/najeon-real-024039`): 제품명 "반응색 나전상자", 전통공예 True, craft_type 나전칠기, 신뢰도 0.9 / 공예 0.85, 9블록. 원본 모서리 밝기 240/216/238/216, 최대 편차 12.5 로 기존 추출기 임계값 24 를 통과해 배경 제거 성공. 미술관 사진 60건의 모서리 편차 중앙값은 101.3.
- 꽃잎 분석(`generated/attached/petal-220947`): 제품명 "색조 꽃잎 장식 오브제", 유형 장식용 오브제, 신뢰도 0.55, 전통공예 False, 공예 신뢰도 0.2, 후보 장식용 오브제·핀·부자재·클립, 11블록. "브로치"라고 부르지 않음.

## 2. hero 원본 고정 (채택, `492e776`)
- 관리자 지시: hero 는 원본을 쓴다.
- 이전 hero: `source_composite`, 1200×1200 png, 배경 제거 후 단색 재합성. 이후: 원본 바이트 그대로, 1060×1060 jpg, 원본과 픽셀 차이 bbox `None`.
- 의미 충돌 해결: 기존 원본 반환은 `asset_mode="source"`, `fidelity_status="FALLBACK"` 이며 "누끼 실패로 물러섬"을 뜻한다. hero 가 이를 쓰면 게이트(`--role hero`)가 전건 미수행으로 셈. 그래서 신규 `asset_mode="source_original"`, `fidelity_status="VERIFIED"`, label "원본 보존 대표 이미지", `product_generated=False` 도입.
- BE 전달 필터: `source_original` 은 `photo_id=="hero"` 이고 `VERIFIED` 일 때만 통과.
- 게이트 재확인: 저장된 60건에서 여전히 `컷아웃 수행 9/60 (15.0%) · 미수행 51건`.
- 재생성 확인: `generated/attached/najeon-hero-030813` (모델 재실행으로 제품명 "반응색 꽃무늬 상자", 신뢰도 0.85, 10블록 — hero 외 카피·구성도 달라짐).
- 테스트 349 → 351.

## 3. rembg 누끼 채택 (채택, `cfd60bb`)
- 관리자 지시: 누끼는 rembg 로.
- 구현: `RembgCutoutExtractor` 추가, 모델 `birefnet-general`(1024px 분할, 반투명·광택 가장자리 보존 목적). 세션 지연 생성·1회 생성, `session_factory`/`segmenter` 주입으로 테스트는 실모델·네트워크 불사용. 알파 8 미만 제외 전경비율 0.5% 미만 또는 99.5% 초과면 `None` → 기존 폴백 경로(누끼 실패 `source`/`FALLBACK`, hero `source_original`). `SolidBackgroundCutoutExtractor` 는 학습 증강·비교 기준선 용도로 잔존.
- 채택 전 비교(`generated/cutout-compare/`, 62케이스 = 60건 + nacre + petals, 각 old.png/rembg.png): 기존 추출기 누끼 성공 11/62(60건 중 9 + 판매사진 2), rembg 62/62, 빈 마스크 0, 전체 마스크 0. 꽃잎 전경비율 기존 6.1% vs rembg 21.9% — 기존 방식이 반투명 꽃잎을 대부분 배경으로 지움.
- 관리자 육안 판정: "잘땄네" → 채택.
- 의존성 충돌: rembg 2.0.70 이상은 `pillow>=12.1,<13` 요구, 프로젝트는 `pillow>=10.4,<12`. `uv lock` 실패. 렌더러·게이트가 Pillow 11 에서 검증돼 있어 Pillow 를 올리지 않고 **rembg==2.0.69** 로 고정(pillow 제약 없음, birefnet-general 지원). 2.0.69 와 비교에 쓴 2.0.83 의 마스크를 기준 6장(nacre, petals, cma-109609, cma-165271, cma-122443, cma-168479)에서 대조 — 알파 차이 0. 최종 잠금: rembg 2.0.69, pillow 11.3.0, numpy 2.5.3, onnxruntime 1.29.0.
- 모델 캐시: 2.0.69 는 `~/.u2net/birefnet-general.onnx`(973MB). 비교 때 2.0.83 이 받은 `~/.rembg/models/birefnet-general/`(930MiB)는 미사용.
- 확인된 반영 결과(`generated/attached/petal-rembg-000846`): 제품명·유형·신뢰도 0.55 동일, 8블록, 사진 hero source_original / packshot source_composite / detail source_crop / lifestyle generated_scene / detail-02~05 generated_view, 상세페이지 774×4290. 관리자 "나쁘지 않네 지금 파이프라인 쓸게".

## 4. '참고용' 표시 제거 (채택, `cfd60bb`)
- 관리자 지시: 참고용 라벨 붙는 것 없앤다. 가이드 §4 5항에 배포 조건으로 적혀 있던 항목이며 관리자 결정으로 제거.
- 제거: `react_document_builder.py` 의 `...-reference-label` figcaption 노드와 `generated_photos` 인자(라벨에만 쓰였음; `pipeline.py` 호출부 2곳 포함), `html_renderer.py` 의 figure/figcaption 오버레이, `web/detail_page.css` 규칙, `scripts/check_reference_label.py` 와 `tests/test_reference_label_gate.py` 삭제, 계약 문서·AWS 문서 갱신. 과거 차수 기록은 미수정.
- 라벨 문자열: "AI 생성 활용 장면(참고용)" → "AI 생성 활용 장면", "AI 생성 디테일(참고용)" → "AI 생성 디테일". `product_generated` 플래그는 유지(BE 는 이것으로 생성물 구분). 문서 내 '참고용' 출현 0회 확인.
- 테스트: 351 → 348 (게이트 테스트 삭제 포함), 종료코드 0.

## 5. 누끼 + 생성 배경 합성 시도 (반려, 미커밋 후 되돌림)
- 관리자 지시: "rembg 로 누끼 따고 배경합성".
- 발견: 누끼 성공 시에도 lifestyle 은 `_generated_usage_scene`(flux 가 제품째 재생성, `generated_scene`, `product_generated=True`)을 먼저 쓰고, 누끼+생성배경 합성은 그 실패 시 예비 경로였음.
- 변경 시도: lifestyle 기본 경로를 생성배경+누끼 합성(`source_composite`, `background_generated=True`, `product_generated=False`)으로, 실패 시 flux 편집 → 단색 합성 순. 배경 프롬프트 버전 `background-v4-jewelry-coverage` → `background-v5-front-facing-composite`(빈 바닥면, 정면·아이레벨, 부드러운 조명, 하단 중앙 제품 영역). detail-02~05 는 범위 밖.
- 검증 생성: `generated/composite-check/nacre`(322.13초), `generated/composite-check/petals`(267.83초). 테스트 350 passed.
- 관리자 앞 육안 소견(오케스트레이터가 비교 페이지에 명시): 제품 형태는 정확(이전 flux 방식은 누운 꽃잎 장식을 세운 조각처럼 재생성). 그러나 두 상품 모두 배경이 거의 같은 흰 원판으로 수렴. 꽃잎은 위에서 본 원본을 정면 배경 앞에 세워 붙여 시점 불일치.
- 관리자 결정: 선택지 2(이전 방식 유지). 미커밋 3파일(`source_photos.py`, `prompts.py`, `tests/test_source_photos.py`)을 `cfd60bb` 로 되돌림, 프롬프트 v4 복귀, 348 passed. 산출물 `generated/composite-check/` 는 참고로 보존.

## 6. 이번 차수의 사고·오판 (에러 분석 대상)
- **데모 스크립트 오용**: `scripts/runtime/generate_attached_detail_page.py` 는 53~140행에 "분홍 곡선 손잡이 부채" 프로필이 하드코딩된 렌더러 데모(`model_run: False`). 오케스트레이터가 이름만 보고 골라 나전칠기 사진이 "분홍 곡선 손잡이 부채"로 나옴(`generated/attached/najeon-023918`). 실제 파이프라인은 `run_local_detail_page.py`. 입력 md5·sha256 은 정상이었고 `model_run: false` 가 유일한 단서였음.
- **모델 서버 미기동**: 세션 재시작 사이 `mlx-serve` 가 내려가 첫 꽃잎 실행이 `Connection refused` 로 실패. `/Applications/MLX Core.app/Contents/MacOS/mlx-serve serve --model ~/.mlx-serve/models/ddalcu/Qwen3.8-27B-MLX-Serve-4bit --host 127.0.0.1 --port 11234` 로 재기동.
- **워커 등록부 tty 불일치**: 재시작 후 터미널이 다른 tty 로 떠서 `scripts/orchestration/workers.tsv` 가 codex↔agy 를 바꿔 가리키고 agy2 는 missing. rembg 배정이 agy 창으로, 라벨 제거 배정이 codex 창으로 가서 둘 다 실행 안 됨(변경 0). 오케스트레이터가 배정 직후 수신 확인을 하지 않아 사용자 질문("현재 작업중인거?") 때 발견. 실제 배치 codex ttys003 / agy ttys004 / agy2 ttys005 / codex3 ttys006 / codex2 ttys007 로 수정 후 재발행.
- **uv lock 충돌**: 위 3절 참고.
- **간헐적 종료 중단**: pytest 348 passed 직후 한 번 `libc++abi: terminating ... recursive_mutex lock failed` 출력, 재실행 시 재현 안 됨, 종료코드 0. onnxruntime 정리 과정 추정 — 원인 미확인.
- **부산물 파일**: 저장소 루트에 `:memory:.ses`(51바이트, 타임스탬프+UUID) 생성, 우리 코드에서 만드는 곳 없음 → 삭제.

## 7. 산출물 위치
- `generated/attached/najeon-023918` (데모 스크립트 오용 결과, 무효)
- `generated/attached/najeon-real-024039` (실제 파이프라인 첫 결과)
- `generated/attached/najeon-hero-030813` (hero 원본 적용)
- `generated/attached/hero-check` (hero 원본 검증)
- `generated/attached/petal-220947` (rembg 이전)
- `generated/attached/petal-rembg-000846` (현재 채택 파이프라인)
- `generated/cutout-compare/` (기존 대 rembg 누끼 62케이스)
- `generated/composite-check/{nacre,petals}` (반려된 합성 시도)

## 8. 갤러리
- 나전칠기 첫 결과: https://claude.ai/code/artifact/<redacted>
- hero 원본 비교: https://claude.ai/code/artifact/<redacted>
- 꽃잎 첫 결과: https://claude.ai/code/artifact/<redacted>
- 누끼 비교(기존 vs rembg): https://claude.ai/code/artifact/<redacted>
- 배경 합성 비교(반려): https://claude.ai/code/artifact/<redacted>
- 꽃잎 rembg 적용: https://claude.ai/code/artifact/<redacted>
