# MonkeyOCR All-in-One Docker Image
# Supports: UI (Gradio) + API (FastAPI) + MCP (Model Context Protocol)
FROM nvidia/cuda:12.6.3-runtime-ubuntu22.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 python3.10-dev python3-pip \
    libgl1-mesa-glx libglib2.0-0 git curl wget \
    poppler-utils texlive-latex-base texlive-latex-extra \
    build-essential gcc g++ \
    && rm -rf /var/lib/apt/lists/*

# Create symbolic links
RUN ln -sf /usr/bin/python3.10 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip

# Configure pip
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --upgrade pip setuptools
ENV PIP_NO_CACHE_DIR=1

# Install PyTorch
ARG CUDA_VERSION=126
RUN pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu${CUDA_VERSION}

# Copy project
COPY . /app/MonkeyOCR
WORKDIR /app/MonkeyOCR

# Install project dependencies
RUN pip install -e .

# Install inference backend
RUN pip install lmdeploy==0.9.2

# Install model download tools
RUN pip install modelscope huggingface_hub

# Install PaddlePaddle for PP-DocLayout
RUN pip install paddlepaddle-gpu==3.0.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/
RUN pip install "paddlex[base]"

# Install MCP dependencies
RUN pip install fastmcp>=2.0.0 anyio

# Apply LMDeploy patcher (for 20/30/40 series GPUs)
ARG LMDEPLOY_PATCHED=true
RUN if [ "$LMDEPLOY_PATCHED" = "true" ]; then \
      python /app/MonkeyOCR/tools/lmdeploy_patcher.py patch && \
      echo "LMDeploy patch applied"; \
    fi

# Create directories
RUN mkdir -p /app/MonkeyOCR/model_weight /tmp/monkeyocr

# Make scripts executable
RUN chmod +x /app/MonkeyOCR/docker/*.sh 2>/dev/null || true
RUN chmod +x /app/MonkeyOCR/start.sh 2>/dev/null || true
RUN chmod +x /app/MonkeyOCR/entrypoint_aio.sh 2>/dev/null || true

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV TMPDIR=/tmp/monkeyocr
ENV HF_HUB_CACHE=/app/MonkeyOCR/model_weight
ENV MODELSCOPE_CACHE=/app/MonkeyOCR/model_weight

# Expose ports: 7870 for UI+API, MCP via stdio
EXPOSE 7870

# Default entrypoint
ENTRYPOINT ["/app/MonkeyOCR/entrypoint_aio.sh"]
CMD ["all"]
