# ---------- builder ----------
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libc6-dev pkg-config \
    libavformat-dev libavcodec-dev libavdevice-dev \
    libavutil-dev libswscale-dev libswresample-dev libavfilter-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
# CPU-only torch first, pinned via a constraints file so the later
# requirements.txt install can't upgrade it into a CUDA build; ultralytics
# is installed with --no-deps since its own opencv-python/torch pulls would
# duplicate opencv-python-headless above and re-pull CUDA torch.
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    && pip freeze | grep -Ei '^torch==|^torchvision==' > /tmp/torch-constraints.txt \
    && pip install --no-cache-dir -r requirements.txt -c /tmp/torch-constraints.txt --extra-index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir --no-deps ultralytics==8.3.145

# ---------- runtime ----------
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash appuser

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY . .
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
