# SGLang 확정 구성 정본 (2026-09-16, 오케스트레이터 검증)

## 확정된 운영 경로
- **서버 1대(AWS EC2 g6e.xlarge, NVIDIA L40S 48GB, Ubuntu) + docker compose.** EKS 는 아직 확정 경로가 아니다(아래 EKS 절).
- 서비스 3개: `detail-page-ai`(포트 8000, CPU 전용), `sglang-text`(30000), `sglang-image`(30001). 두 SGLang 프로세스가 GPU 1장을 나눠 쓴다.
- 파일: `Dockerfile`(서비스), `docker/sglang-diffusion.Dockerfile`(이미지 서버), `docker-compose.yml`, `.env.example`, `docs/operations/ubuntu-deployment.md`, `docs/operations/sglang-serving-research.md`, `notebooks/colab_sglang_smoke_test.ipynb`.

## 모델
| 역할 | 저장소 | 고정 커밋 | 크기 |
|---|---|---|---|
| 텍스트·비전 | `cyankiwi/Qwen3.8-27B-AWQ-INT4` | `6e134bae811fb5adac50ee042ae5f029ac6779aa` | 19.60 GiB |
| 이미지 생성·편집 | `circulus/FLUX.2-klein-9B-bnb-4bit` | `58c2804f31af12c8888504b96250010c50b55e44` | 약 10.2 GiB (transformer 4.36 + text_encoder 5.66 + vae 0.16, bitsandbytes nf4) |
- `.env` 변수 `TEXT_MODEL_REVISION`, `IMAGE_MODEL_REVISION` 로 고정해 `--revision` 으로 전달. 모델은 이름 있는 볼륨 `huggingface-cache` 에 1회 다운로드.
- 원본 `black-forest-labs/FLUX.2-klein-9B` 는 FLUX Non-Commercial License. 위 저장소는 그 커뮤니티 양자화본이며 **관리자 결정으로 채택**. 상업 운영 전 BFL 라이선스 확인 필요(사실만 기록, 권고 금지). 대안은 `black-forest-labs/FLUX.2-klein-4B`(Apache 2.0).

## 서버 기동 (docker-compose.yml 기준)
- 텍스트: `python3 -m sglang.launch_server --model-path <텍스트> --revision <커밋> --served-model-name qwen-text --host 0.0.0.0 --port 30000 --mem-fraction-static 0.50 --context-length 8192 --trust-remote-code`
- 이미지: `sglang serve --model-path <이미지> --revision <커밋> --served-model-name flux-klein --host 0.0.0.0 --port 30001 --num-gpus 1 --dit-cpu-offload false --text-encoder-cpu-offload false`
- 이미지 서버 이미지는 `lmsysorg/sglang:v0.5.19` 위에 `sglang[diffusion]==0.5.19` 와 `bitsandbytes==0.50.2` 설치(공식 이미지에 diffusion 미포함, bitsandbytes 는 test extra 에만 있음).
- SGLang 은 이미지 생성 모델이면 `dit_cpu_offload`/`text_encoder_cpu_offload` 를 기본 True 로 켜므로 명시적으로 false. 4bit 텍스트 인코더는 GPU 상주가 필요하다.
- 헬스체크는 두 서버 모두 `GET /v1/models`(확산 서버에 `/health` 없음).
- 메모리(가중치 하한): 44.7 GiB 중 텍스트 22.35(0.50) + 이미지 10.2 = 32.6 GiB, 여유 약 12 GiB. CPU 오프로드 없음 → 호스트 RAM 32 GiB 압박 없음.

## 클라이언트 계약 (src/local_detail_page_ai/clients.py)
- `LOCAL_TEXT_PROVIDER=sglang`, `LOCAL_IMAGE_PROVIDER=sglang`, `BACKGROUND_PROVIDER=sglang`. `LOCAL_TEXT_MODEL=qwen-text`, `LOCAL_IMAGE_MODEL=flux-klein` — SGLang 의 `--served-model-name` 과 정확히 같아야 하며 클라이언트는 모델 ID 를 변환하지 않는다.
- 텍스트: `POST /v1/chat/completions`, content 에 `image_url` data URI, `response_format {"type":"json_object"}`. 기존 OpenAI 호환 클라이언트를 그대로 재사용.
- 이미지 생성: `POST /v1/images/generations` JSON — `model`, `prompt`, `negative_prompt`, `n`, `size`, `response_format=b64_json`, `num_inference_steps`(기존 `steps` 아님), 선택적 `guidance_scale`·`seed`.
- 이미지 편집: `POST /v1/images/edits` **multipart**, 입력 이미지는 `image` 필드. `strength` 는 SGLang 핸들러에 필드가 없어 전송하지 않는다.
- MLX 경로(`LOCAL_*_PROVIDER=mlx`)는 그대로 남아 있고 **로컬 Mac 개발용**이다: MLX Serve `127.0.0.1:11234`, `ddalcu/Qwen3.8-27B-MLX-Serve-4bit`, `mlx-community/flux2-klein-9b-4bit`. 서버 경로와 혼동하지 말 것.

## 사진 정책 (현재)
- hero 는 촬영 원본 그대로(`asset_mode=source_original`, `fidelity_status=VERIFIED`). BE 전달 필터는 `source_original` 을 hero + VERIFIED 일 때만 통과.
- 누끼는 rembg(`birefnet-general`, rembg==2.0.69), 실패 시 `source`/`FALLBACK`.
- 생성 사진의 '참고용' 표시는 제거됨. 생성 여부는 `product_generated` 플래그로 구분. `scripts/check_reference_label.py` 는 삭제됨.

## 검증 상태 (과장 금지)
- 로컬: 테스트 353개 통과, `docker compose config` 통과, 서비스 이미지 arm64 빌드·기동·healthy 확인, amd64 빌드 확인.
- **GPU 에서는 한 번도 실행되지 않았다.** 두 모델 동시 적재, 4bit 파이프라인 로딩, 편집 품질, 처리 시간 모두 미검증. `notebooks/colab_sglang_smoke_test.ipynb` 로 Colab 사전 확인 가능(아직 실행 안 함).

## EKS 현황
- **EKS 전용 산출물 없음**: Deployment/Service/PVC 매니페스트, Helm 차트, ECR 푸시 스크립트 모두 없다. `aws-deployment.md` 는 설계 서술만 있다.
- EKS 로 갈 경우 확인된 차이 4가지:
  1. Dockerfile 의 `HEALTHCHECK` 를 쿠버네티스는 무시한다. 게다가 현재 방식(없는 작업 조회 404)은 `httpGet` probe 로 쓸 수 없다(2xx/3xx 만 성공). exec probe 나 상태 엔드포인트가 필요하다.
  2. GPU 1장을 파드 2개가 나눠 쓸 수 없다(device plugin 은 컨테이너 단위 배타 할당). 타임슬라이싱/MPS 설정이나 두 서버를 한 파드에 묶는 설계가 필요하다.
  3. 모델 캐시가 도커 볼륨 → PVC 로 바뀌어야 한다.
  4. `aws-deployment.md` 5절의 추론 서버 규격(vLLM + Diffusers 프록시, CUDA 12.4 베이스)은 SGLang 확정 이전 서술이라 사실과 다르다.
