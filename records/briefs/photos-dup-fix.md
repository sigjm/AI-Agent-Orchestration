# 결함 수정 — photo_id 중복 (`lifestyle` 두 개)

## 담당 파일
- `src/detail_page_ai/source_photos.py`
- `tests/test_source_photos.py`

## 증상 (관리자가 실측)
사진 4장을 넣고 방금 작업한 코드로 돌리면 한 세트 안에 **같은 `photo_id` 가 두 번** 나온다.

```
입력 4장 → ['hero', 'packshot', 'detail', 'lifestyle', 'lifestyle',
            'detail-02', 'detail-03', 'detail-04', 'detail-05']
                          ^^^^^^^^^^  ^^^^^^^^^^  중복
```

네 번째 제공 사진이 `lifestyle` 역할을 차지하는데, 보조 생성 경로가 `lifestyle` 활용 장면을 **또** 만들어 붙이기 때문이다.

## 왜 문제인가
`photo_id` 는 산출물에서 사진을 가리키는 식별자다. `react_document` 의 `props.imageId` 가 이 값으로 사진을 참조하므로(자세한 계약은 `docs/api/react-json-output-contract.md`), 한 세트에 같은 id 가 둘이면 **어느 사진을 가리키는지 정해지지 않는다.**

## 고칠 것
**한 세트 안에서 `photo_id` 는 유일해야 한다.**

방향은 다음 중 하나를 고르되, 고른 이유를 결과 보고에 적을 것.
- (가) 제공 사진이 이미 차지한 역할에 대해서는 같은 역할의 보조 생성을 건너뛴다
- (나) 보조 생성 컷에 충돌하지 않는 id 를 준다 (예: `lifestyle-02`)

**관리자 의견: (나)를 권한다.** 관리자 지시가 "4장 이상이어도 필요한 사진은 생성해서 제공"이므로, 제공 사진이 있다고 해서 활용 장면 생성을 빼면 지시와 어긋난다. 다만 (가)가 더 맞다고 판단하면 근거를 적고 그렇게 해도 된다.

- 새 id 를 쓴다면 `_labels` 에 해당 라벨이 있어야 한다. 없으면 기존 라벨 체계와 일관되게 추가할 것.
- `asset_mode`·`fidelity_status`·`product_generated` 의 의미는 그대로 둔다. 생성 컷은 `generated_scene`/`generated_view`, `GENERATED`, `product_generated=True`.

## 테스트
`tests/test_source_photos.py` 에 추가한다.
- **입력 1~5장 각각에 대해 한 세트 안의 `photo_id` 가 모두 유일하다** (이 결함의 회귀 테스트)
- 4장 입력에서 제공 사진 4장이 모두 원본 바이트 그대로 실리고, 보조 생성 컷도 함께 나온다 (기존 기대 유지)

기존 테스트를 통과시키려고 삭제·완화하지 말 것.

## 검증
`.venv/bin/python -m pytest -q` → **361 이상**. 줄어들면 회귀다.

## 보고
`## 결과` 에 고른 방향과 이유, 바꾼 행, 추가 테스트, 테스트 개수를 적고 마지막 줄에 `완료: 테스트 N passed` 출력.
