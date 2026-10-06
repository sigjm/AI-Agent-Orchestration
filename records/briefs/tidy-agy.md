# 작업 — 저장소 루트 정리

## 담당 파일 (이 셋만)
- `.dockerignore`
- `README.md` (저장소 루트. `docs/README.md` 는 다른 워커 담당이니 열지 말 것)
- 빈 디렉터리 `.models/`

`docs/` 아래는 전부 다른 워커가 동시에 고치는 중이다. **열지 말 것.**

## 할 것

### 1. `.dockerignore` 보강
현재 큰 것들은 이미 잘 막혀 있다(확인함): `generated/`(2.9G), `.local/`(70G), `.venv/`(592M), `data/`, `node_modules/`, `.git/`, `.orchestration/`.

빠진 것은 IDE·에이전트 로컬 상태 디렉터리다. 이미지에 들어갈 이유가 없다.
- `.idea/`, `.claude/`, `.gemini/`, `.omo/`, `.models/`
- 이 저장소에는 Dockerfile 이 셋이고(`Dockerfile`, `sglang/Dockerfile`, `docker/sglang-diffusion.Dockerfile`) 모두 **저장소 루트를 빌드 컨텍스트로** 쓴다. 따라서 루트 `.dockerignore` 하나가 셋 모두에 적용된다.
- 기존 항목은 지우지 말 것. 특히 `generated/`, `.local/`, `data/` 는 지우면 빌드 컨텍스트가 수십 GB 가 된다.

### 2. 빈 디렉터리 `.models/` 제거
크기 0B 이고 아무것도 참조하지 않는다. `rg -n "\.models" .` 로 참조가 없는지 확인한 뒤 지울 것. **참조가 하나라도 있으면 지우지 말고 보고할 것.**

### 3. 루트 `README.md` 사실 확인
오늘 다음이 바뀌었다. README 가 이와 어긋나는 곳이 있으면 고칠 것.
- `GET /health`(무인증 200)와 `GET /health/ready`(200/503) 가 추가됐다.
- EKS 용 단일 컨테이너 이미지 `sglang/Dockerfile` + `sglang/entrypoint.sh` 가 생겼다.
- `scripts/build_review_page.py` 가 삭제됐다. README 가 이 스크립트를 안내하면 지울 것.
- 테스트는 **358개**이고 `uv run pytest` 와 `python -m pytest` **둘 다** 통과한다. README:246 부근의 테스트 명령 안내를 확인할 것.
- 서버 추론은 SGLang, Mac 로컬은 MLX 다. **서버 GPU 에서는 아직 한 번도 실행되지 않았다** — 이 문장이 README 에 있는지 확인하고 없으면 추가할 것.

바뀐 게 없으면 억지로 고치지 말 것. **고칠 이유가 없으면 그대로 두는 것이 맞다.**

## 하지 말 것
- 문서를 옮기거나 이름을 바꾸지 말 것.
- `local.env.example` 과 `.env.example` 은 각각 Mac 로컬용·서버용으로 이미 구분돼 있다. 건드리지 말 것.
- 코드·테스트를 고치지 말 것.

## 검증
1. `.venv/bin/python -m pytest -q` → **358 passed**
2. `.dockerignore` 수정 후, 기존 항목이 하나도 사라지지 않았는지 `git diff .dockerignore` 로 확인하고 보고에 붙일 것.

## 보고
`## 결과` 에 파일별 전/후와 `.models/` 참조 검사 결과를 적고, 마지막 줄에 `완료: 수정 N개 파일, 테스트 358 passed` 출력.
