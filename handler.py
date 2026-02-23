import base64
import io
import os
import time
from typing import Any, Dict, Optional

import runpod
import torch
from PIL import Image

from diffusers import QwenImageEditPlusPipeline
from diffusers.models import QwenImageTransformer2DModel

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE = torch.bfloat16 if DEVICE == "cuda" else torch.float32

HF_TOKEN = os.getenv("HF_TOKEN")
PIPE: Optional[QwenImageEditPlusPipeline] = None

BASE_MODEL_ID = "Qwen/Qwen-Image-Edit-2511"
TRANSFORMER_ID = "prithivMLmods/Qwen-Image-Edit-Rapid-AIO-V21"


def _strip_data_url_prefix(b64: str) -> str:
    if "," in b64 and b64.strip().lower().startswith("data:"):
        return b64.split(",", 1)[1]
    return b64


def _b64_to_pil(b64: str) -> Image.Image:
    b64 = _strip_data_url_prefix(b64)
    raw = base64.b64decode(b64)
    return Image.open(io.BytesIO(raw)).convert("RGB")


def _pil_to_b64(img: Image.Image, fmt: str = "PNG") -> str:
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def _load_pipeline() -> QwenImageEditPlusPipeline:
    global PIPE
    if PIPE is not None:
        return PIPE

    t0 = time.time()

    if DEVICE == "cuda":
        torch.backends.cuda.matmul.allow_tf32 = True

    transformer = QwenImageTransformer2DModel.from_pretrained(
        TRANSFORMER_ID,
        torch_dtype=DTYPE,
        token=HF_TOKEN,
    )

    pipe = QwenImageEditPlusPipeline.from_pretrained(
        BASE_MODEL_ID,
        transformer=transformer,
        torch_dtype=DTYPE,
        token=HF_TOKEN,
    ).to(DEVICE)

    PIPE = pipe
    print(f"[INIT] Loaded in {time.time() - t0:.1f}s | device={DEVICE} dtype={DTYPE}")
    return PIPE


def handler(job: Dict[str, Any]) -> Dict[str, Any]:
    inp = job.get("input") or {}
    prompt = inp.get("prompt")
    image_b64 = inp.get("image_base64")

    if not isinstance(prompt, str) or not prompt.strip():
        return {"error": "Missing/invalid 'prompt' (string)"}
    if not isinstance(image_b64, str) or not image_b64.strip():
        return {"error": "Missing/invalid 'image_base64' (base64 string)"}

    pipe = _load_pipeline()
    init_img = _b64_to_pil(image_b64)

    t0 = time.time()
    with torch.inference_mode():
        out = pipe(
            image=[init_img],  # IMPORTANT: list
            prompt=prompt,
            negative_prompt=" ",
            true_cfg_scale=1.0,
            guidance_scale=1.0,
            num_inference_steps=4,
            num_images_per_prompt=1,
        )

    result_img = out.images[0]
    result_b64 = _pil_to_b64(result_img, "PNG")

    if DEVICE == "cuda":
        torch.cuda.empty_cache()

    return {
        "result_base64": result_b64,
        "meta": {"inference_seconds": round(time.time() - t0, 3), "steps": 4},
    }


runpod.serverless.start({"handler": handler})
