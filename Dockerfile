FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip git curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip

# CUDA-enabled PyTorch (cu121)
RUN pip install --no-cache-dir \
    torch==2.4.1+cu121 torchvision==0.19.1+cu121 \
    --index-url https://download.pytorch.org/whl/cu121

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY handler.py /app/handler.py

CMD ["python3", "-u", "handler.py"]
