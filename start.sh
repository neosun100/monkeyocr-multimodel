#!/bin/bash
# MonkeyOCR One-Click Start Script
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load .env if exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Check nvidia-docker
check_nvidia_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker not installed"
        exit 1
    fi
    
    if ! docker info 2>/dev/null | grep -q "Runtimes.*nvidia"; then
        log_warn "nvidia-docker runtime not detected, checking GPU support..."
        if ! docker run --rm --gpus all nvidia/cuda:12.6.3-base-ubuntu22.04 nvidia-smi &>/dev/null; then
            log_error "GPU support not available in Docker"
            exit 1
        fi
    fi
    log_info "Docker GPU support verified"
}

# Auto-select GPU with least memory usage
select_best_gpu() {
    if command -v nvidia-smi &> /dev/null; then
        GPU_ID=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits 2>/dev/null | \
                 sort -t',' -k2 -n | head -1 | cut -d',' -f1 | tr -d ' ')
        if [ -n "$GPU_ID" ]; then
            export NVIDIA_VISIBLE_DEVICES=$GPU_ID
            GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader -i $GPU_ID 2>/dev/null)
            GPU_MEM=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader -i $GPU_ID 2>/dev/null)
            log_info "Selected GPU $GPU_ID: $GPU_NAME (Free: $GPU_MEM)"
        else
            export NVIDIA_VISIBLE_DEVICES=0
            log_warn "Could not detect GPU, using GPU 0"
        fi
    else
        export NVIDIA_VISIBLE_DEVICES=0
        log_warn "nvidia-smi not found, using GPU 0"
    fi
}

# Find available port
find_available_port() {
    local base_port=${1:-7870}
    local port=$base_port
    while ss -tlnp 2>/dev/null | grep -q ":$port "; do
        log_warn "Port $port is in use, trying next..."
        port=$((port + 1))
    done
    echo $port
}

# Main
log_info "=== MonkeyOCR Docker Startup ==="

check_nvidia_docker

# Select GPU if not set
if [ -z "$NVIDIA_VISIBLE_DEVICES" ]; then
    select_best_gpu
fi

# Find available port
PORT=${PORT:-7870}
PORT=$(find_available_port $PORT)
export PORT

# Create data directory
DATA_DIR=${DATA_DIR:-/tmp/monkeyocr}
mkdir -p "$DATA_DIR"
export DATA_DIR

log_info "Configuration:"
log_info "  GPU: $NVIDIA_VISIBLE_DEVICES"
log_info "  Port: $PORT"
log_info "  Data Dir: $DATA_DIR"

# Start container
log_info "Starting MonkeyOCR container..."
docker compose up -d monkeyocr-aio

# Wait for startup
log_info "Waiting for service to start..."
for i in {1..60}; do
    if curl -s "http://localhost:$PORT/health" &>/dev/null; then
        break
    fi
    sleep 2
    echo -n "."
done
echo ""

# Show access info
log_info "=== MonkeyOCR Started ==="
echo ""
echo -e "${GREEN}Access URLs:${NC}"
echo -e "  UI Demo:    http://0.0.0.0:$PORT/demo"
echo -e "  API Docs:   http://0.0.0.0:$PORT/docs"
echo -e "  Health:     http://0.0.0.0:$PORT/health"
echo ""
echo -e "${GREEN}MCP Configuration:${NC}"
echo '  {
    "mcpServers": {
      "monkeyocr": {
        "command": "docker",
        "args": ["exec", "-i", "monkeyocr-aio", "python", "mcp_server.py"]
      }
    }
  }'
echo ""
log_info "Use 'docker compose logs -f monkeyocr-aio' to view logs"
