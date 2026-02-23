# Qwen Image Edit 2511 + Rapid-AIO v21 (RunPod Serverless Worker)

A small but complete pet project: a **RunPod serverless worker** for image editing with the API flow:

**prompt + image_base64 → result_base64**

It is based on the base model:
- https://huggingface.co/Qwen/Qwen-Image-Edit-2511

But it **replaces only the transformer weights** with an extracted transformer:
- https://huggingface.co/prithivMLmods/Qwen-Image-Edit-Rapid-AIO-V21

## Main effects of this replacement:
- **Much fewer steps**: a usable 4-step mode (instead of dozens of steps with the base model).
- **Faster inference** at comparable quality for many edit tasks.
- A tendency toward **more realistic-looking results**.
- **NSFW-capable behavior**.

---

## What this repo contains

- RunPod Serverless **Queue** endpoint (async): submit job → get `id` → poll status.
- A simple API contract: `prompt + image_base64 → result_base64`.
- Docker packaging (CUDA + PyTorch + diffusers) and deploy via GitHub → RunPod build.
- MVP-oriented defaults: `num_inference_steps=4`, timeouts, worker limits.

---

## Benchmark (my measurement)

Environment:
- GPU: **A100 80GB**

Test input:
- photo size: ~**1.5MB**

Results (first cold run):
- Rapid-AIO v21 (4 steps): **delay ~10s**, **execution ~45s**
- Base `Qwen-Image-Edit-2511`: around **130s** (even without cold start)

This is an orientation point only. Times vary with region, queue, caching, disk, image size, and image/build versions.

---

## API

### Submit job (async)
`POST /run`

Request body:
```json
{
  "input": {
    "prompt": "Make the photo more realistic, soft natural light",
    "image_base64": "<BASE64>"
  }
}
```

Response:

```
{
  "id": "<job_id>",
  "status": "IN_QUEUE"
}
```

Poll status
`GET /status/<job_id>`
Successful result:

```
{
  "status": "COMPLETED",
  "output": {
    "result_base64": "<BASE64>",
    "meta": {
      "inference_seconds": 12.345,
      "steps": 4
    }
  }
}
```

utils (local base64 tools)
The `utils/` folder contains two HTML files that run locally in your browser:
* `image_to_base64.html` — pick an image → get base64
* `base64_to_image.html` — paste base64 → preview/download result
This makes manual testing easy without terminal permissions or third-party services.
