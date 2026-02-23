# RunPod Serverless Deploy (Queue, scale-to-zero)

A short guide to deploy this repository as a RunPod Serverless **Queue** endpoint.

---

## Endpoint

1) Serverless → New Endpoint → Import Git Repository  
2) Select `Dockerfile` and build context `.`

Then configure the endpoint:

- Endpoint type: `Queue`
- Worker type: `GPU`
- GPU: **48GB+** (for stability, **80GB** is usually better)
- Active workers: `0`
- Max workers: e.g. `4`
- Concurrency per worker: `1`
- Init timeout: `10 min`
- Job timeout: `10 min`
- Container disk: `150 GB`

These settings are not the only correct ones — adjust them based on your latency/cost goals, traffic, and GPU availability.

---

## Model caching

In the **Model** field set:
- `Qwen/Qwen-Image-Edit-2511`

---

## Env vars

Add:
- `HF_TOKEN=<your token>`

---

## Test

Submit a job in **Requests**: `prompt + image_base64`  
Then poll `/status/<job_id>` and read `output.result_base64`.
