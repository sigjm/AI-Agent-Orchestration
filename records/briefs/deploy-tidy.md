# 구조 정리 — 배포 파일을 `deploy/` 로 모은다

## 배경
이 저장소를 `Jangingmall/GenAI` 의 `page_generation/` 하위로 옮긴다. 옮기기 전에 루트에 흩어진 배포 파일을 한 곳으로 모은다. **`src/` 레이아웃은 그대로 둔다.**

## 목표 구조
```
deploy/
├── Dockerfile              ← 루트 Dockerfile
├── docker-compose.yml      ← 루트 docker-compose.yml
├── sglang/                 ← 루트 sglang/ (Dockerfile, entrypoint.sh)
└── docker/                 ← 루트 docker/ (sglang-diffusion.Dockerfile)
```

`src/`, `tests/`, `docs/`, `scripts/`, `assets/`, `web/`, `data/`, `notebooks/`, `pyproject.toml`, `uv.lock`, `README.md`, `.env.example`, `local.env.example`, `package.json`, `.gitignore`, `.dockerignore` 는 **자리를 그대로 둔다.**

## 담당 파일
- 이동: `Dockerfile`, `docker-compose.yml`, `sglang/`, `docker/`
- 참조 수정: 위 경로를 가리키는 모든 파일 (문서·설정·스크립트·테스트)

`docs/deliverables/PHASE3_AI_산출물.md` 는 다른 워커가 동시에 쓰는 중이니 **열지 말 것.**

## 반드시 지킬 것

### 1. `git mv` 로 옮긴다
파일 히스토리가 끊기지 않게 `git mv` 를 쓸 것. 복사 후 삭제하지 말 것.

### 2. 빌드 컨텍스트가 깨지지 않아야 한다
Dockerfile 들은 **저장소 루트를 빌드 컨텍스트로** 쓴다(`COPY src ./src` 등). 옮긴 뒤에도 그래야 한다.
- 빌드 명령이 `docker build -f deploy/Dockerfile .` 형태가 된다
- `docker-compose.yml` 안의 `build.context` 와 `dockerfile` 경로를 새 위치에 맞게 고칠 것
- **`COPY` 경로 자체는 바꾸지 말 것.** 컨텍스트가 여전히 루트이므로 `COPY src ./src` 는 그대로 맞다

### 3. `docker compose config` 로 검증
`docker compose -f deploy/docker-compose.yml config` 가 오류 없이 통과해야 한다. 결과를 보고에 적을 것.

### 4. 문서의 경로 참조를 전부 고친다
`Dockerfile`, `docker-compose.yml`, `sglang/Dockerfile`, `sglang/entrypoint.sh`, `docker/sglang-diffusion.Dockerfile` 를 가리키는 서술이 여러 문서에 있다. 다음은 **특히 중요**하니 빠뜨리지 말 것.
- `docs/operations/eks-workload-spec.md` — 인프라팀 전달용이다. Dockerfile 경로와 빌드 명령이 여기 적혀 있다
- `docs/operations/ubuntu-deployment.md`, `aws-deployment.md`, `aws-migration-checklist.md`
- `README.md`, `docs/README.md`
- `.dockerignore` 안에 경로 규칙이 있으면 확인

단, **시점 기록은 고치지 말 것**: `docs/deliverables/experiments/`, `docs/evaluation/`, `docs/refactoring/`, `docs/superpowers/`, `docs/operations/sglang-serving-research.md`.

### 5. 테스트
`tests/test_project_layout.py` 가 파일 위치를 검증한다. 새 구조에 맞게 고치되 **검증 의도를 약화시키지 말 것.** 통과시키려고 assertion 을 지우지 말 것.

## 검증
1. `.venv/bin/python -m pytest -q` → **369 이상**
2. `docker compose -f deploy/docker-compose.yml config` 통과
3. `grep -rn "\bsglang/Dockerfile\|\bdocker/sglang\|^Dockerfile\b" docs/ README.md` 로 옛 경로 참조가 남았는지 확인 (시점 기록 제외)

## 보고
`## 결과` 에 옮긴 파일, 고친 참조(파일·행), 위 검증 3건 결과를 적고, 마지막 줄에 `완료: 이동 N개, 참조 수정 M곳, 테스트 N passed` 출력.
