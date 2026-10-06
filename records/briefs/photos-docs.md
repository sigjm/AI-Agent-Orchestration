# 문서 정리 — 사진 배정 동작이 바뀌었다

## 담당 파일 (이 6개만. `.env.example` 과 `src/`, `tests/` 는 다른 워커가 동시에 고치는 중이니 열지 말 것)
- `README.md`
- `docs/operations/local-llm.md`
- `docs/operations/aws-deployment.md`
- `docs/architecture/ai-architecture-and-safety.md`
- `docs/api/ai-fe-io-spec.md`
- `docs/data/collection-license-cleaning-plan.md`

`docs/api/be-ai-integration-negotiation.md` 는 관리자가 직접 고치는 중이니 **건드리지 말 것.**

## 무엇이 바뀌었나 (커밋 `07ce5da`)

### 이전 동작
- 제공 사진이 4장 미만이면 **첫 장만 쓰고** 나머지 제공 사진은 버린 채 생성 컷으로 역할을 채웠다. 버려진 사진은 `alternate` 자리에만 남았다.
- 제공 사진이 4장 이상이면 **생성을 전혀 하지 않고** 제공 사진만 썼다.
- 이 분기를 `SOURCE_PHOTO_VARIATION_THRESHOLD`(기본 4)가 갈랐다.

### 현재 동작
- **제공 사진이 항상 먼저다.** 역할(`hero`, `packshot`, `detail`, `lifestyle` …) 앞에서부터 제공 사진을 순서대로 배정한다.
- **제공 사진으로 채우지 못한 역할만 생성**한다.
- **장수와 무관하게 보조 생성 컷(활용 장면·디테일 뷰)을 붙인다.** 4장을 받아도 생성 컷이 함께 나온다.
- 역할 수를 넘는 제공 사진은 `alternate` 로 **한 장도 버리지 않고** 보존한다.
- `hero` 는 그대로 촬영 원본 보존 (`asset_mode=source_original`, `fidelity_status=VERIFIED`).
- 생성 컷이 제공 사진과 같은 역할을 쓰지 않도록 활용 장면 생성분은 `lifestyle-02` 로 구분한다.

### 설정 변경
다른 워커가 동시에 작업 중이며 **아래가 확정 사양**이다. 이 이름으로 문서에 적을 것.

- `SOURCE_PHOTO_VARIATION_THRESHOLD` → **`MAX_GENERATED_PHOTOS`**
- 의미: **한 세트에 붙일 보조 생성 컷의 최대 장수**
- 범위 0~12, 기본값 **5**
- **0 이면 생성을 전혀 하지 않고 제공 사진만 사용한다**

## 할 것
1. 위 6개 문서에서 **옛 동작을 설명하는 서술을 현재 동작으로** 고친다. "4장 이상이면 생성하지 않는다", "4장 미만이면 파생한다" 류가 대상이다.
2. 옛 설정 이름이 나오면 새 이름·새 의미로 고친다.
3. **문서마다 성격이 다르니 그 문서의 문맥에 맞게 쓸 것.** `local-llm.md` 는 Mac 로컬 실행 문서, `ai-fe-io-spec.md` 는 FE/BE 계약 문서다. 기계적으로 같은 문장을 붙여넣지 말 것.
4. 해당 문서에 그 서술이 없으면 **억지로 넣지 말 것.** 고칠 것이 없으면 없다고 보고하면 된다.

## 하지 말 것
- 검증되지 않은 것을 검증된 것처럼 쓰지 말 것. 서버 GPU 실행은 아직 한 번도 없었다.
- 사람 평가 점수 같은 없는 데이터를 만들지 말 것.
- 코드·설정 파일을 고치지 말 것.

## 검증
- 담당 6개 문서에 `SOURCE_PHOTO_VARIATION_THRESHOLD` 가 0건
- `.venv/bin/python -m pytest -q` → 362 이상

## 보고
`## 결과` 에 파일별 고친 곳(행 번호·전/후 요지)과, 고칠 것이 없던 파일을 적고, 마지막 줄에 `완료: 수정 N개 파일` 출력.
