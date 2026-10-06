# 검수 작업 — 운영·배포 문서와 실제 이미지 정의 대조

당신은 검수자입니다. **파일을 절대 수정하지 마세요.** 발견 사항만 보고서에 적습니다.

## 담당 파일
- docs/operations/aws-deployment.md
- docs/operations/aws-migration-checklist.md
- docs/operations/eks-workload-spec.md
- docs/operations/local-generation-test-report.md
- docs/operations/local-llm.md
- docs/operations/orchestration.md
- docs/operations/server-memory-estimate.md
- docs/operations/sglang-serving-research.md
- docs/operations/sglang-vllm-fit.md
- docs/operations/ubuntu-deployment.md

대조 기준(읽기 전용): .env.example, docker-compose.yml, Dockerfile, sglang/Dockerfile, sglang/entrypoint.sh, docker/sglang-diffusion.Dockerfile, notebooks/colab_sglang_smoke_test.ipynb, src/local_detail_page_ai/clients.py

## 확인 항목
1. **모델 식별자 일치**: 텍스트/이미지 모델 경로, 커밋 SHA(revision), served-model-name 이 다섯 곳 — `.env.example` / `docker-compose.yml` / `sglang/Dockerfile` / 콜랩 노트북 / 각 문서 — 에서 **전부 같은 값**인가. 하나라도 다르면 파일·행 번호와 두 값을 나란히 적을 것.
2. **포트·경로 일치**: 8000 / 30000 / 30001, `/var/lib/detail-page-ai/...` 하위 경로, UID·GID 10001 이 문서와 실제 파일에서 일치하는가.
3. **수치 모순**: 19.6 GiB(텍스트 가중치), 10.2 GiB(이미지 가중치), 22.4 GiB(텍스트 정적 선점), 32.6 GiB(합계), 44.7 GiB(가용), 모델 다운로드 약 30GB, 도커 이미지 18~22GB — 이 값들이 문서 간에 서로 어긋나는 곳. 산수가 맞지 않는 문장도 포함.
4. **미검증을 검증처럼 적은 문장**: 이 구성은 **GPU 에서 한 번도 실행된 적이 없고 이 Dockerfile 은 빌드된 적도 없다.** 그런데 "확인함 / 통과 / 정상 동작" 처럼 단정한 문장이 있으면 전부 보고. 반대로 "미검증"이라고 정확히 표시된 곳은 이상 없음으로 적을 것.
5. **SGLang 인터페이스 오기**: 텍스트 서버는 `sglang.launch_server`, 이미지 확산 서버는 `sglang serve` 다. 확산 서버에는 `/health` 가 없고 `/v1/models` 만 있다. 이미지 편집은 multipart `/v1/images/edits`(필드명 image), 생성은 JSON `/v1/images/generations`. 문서가 이와 다르게 적은 곳.
6. **문서 간 충돌**: `eks-workload-spec.md`(EKS·PVC·단일 컨테이너)와 `ubuntu-deployment.md`·`aws-deployment.md`(단일 서버·docker compose·3 컨테이너)는 서로 다른 배포 대상이다. 둘이 **모순**인 서술과, 단순히 **대상이 달라서 다른** 서술을 구분해서 적을 것. 후자는 이상 없음이다.
7. `local-llm.md` 는 Mac 로컬 전용 문서다. 여기서 MLX·11234 포트가 나오는 것은 정상이다. 서버 문서에 MLX 가 섞여 있으면 그것만 보고.

## 보고 규칙
- 근거는 반드시 `파일경로:행번호`. 행 번호 없는 지적은 채택하지 않는다.
- 추측은 `[추정]`, 파일에서 확인한 것은 `[확인]`.
- 문제 없던 항목도 "이상 없음"으로 적을 것.
- 심각도 3단계: `치명`(인프라팀이 이 문서대로 하면 배포가 실패) / `불일치`(문서-코드 차이) / `사소`(표기).

## 산출물
`.orchestration/reports/audit-2026-09-16/agy.md` 한 파일.
끝나면 마지막 줄에 `완료: .orchestration/reports/audit-2026-09-16/agy.md, 발견 N건` 을 출력하세요.
