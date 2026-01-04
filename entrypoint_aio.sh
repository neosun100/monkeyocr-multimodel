#!/bin/bash
# MonkeyOCR All-in-One Entrypoint
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

log_info "=== MonkeyOCR All-in-One Container ==="

# Show GPU info
if command -v nvidia-smi &>/dev/null; then
    log_info "GPU Information:"
    nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader
fi

# Download models if needed
log_info "Checking models..."
if [ -f /app/MonkeyOCR/docker/download_models.sh ]; then
    /app/MonkeyOCR/docker/download_models.sh || log_warn "Model download had issues"
fi

# Create temp directory
mkdir -p /tmp/monkeyocr

# Start mode
MODE=${1:-all}
PORT=${PORT:-7870}

case "$MODE" in
    all)
        log_info "Starting All-in-One service (UI + API) on port $PORT"
        cd /app/MonkeyOCR
        exec python -u api/main_aio.py
        ;;
    demo)
        log_info "Starting Gradio Demo on port $PORT"
        cd /app/MonkeyOCR
        exec python -u demo/demo_gradio.py
        ;;
    api)
        log_info "Starting FastAPI on port $PORT"
        cd /app/MonkeyOCR
        exec uvicorn api.main:app --host 0.0.0.0 --port $PORT
        ;;
    mcp)
        log_info "Starting MCP Server (stdio mode)"
        cd /app/MonkeyOCR
        exec python -u mcp_server.py
        ;;
    bash)
        log_info "Starting Bash shell"
        exec /bin/bash
        ;;
    *)
        log_info "Executing: $@"
        exec "$@"
        ;;
esac
