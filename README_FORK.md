[English](README_FORK.md) | [简体中文](README_FORK_CN.md) | [繁體中文](README_FORK_TW.md) | [日本語](README_FORK_JP.md)

<div align="center">
<h1>MonkeyOCR Multi-Model Fork</h1>
<p>Enhanced Document Parsing with Multi-Model Support for Handwritten Ancient Chinese</p>

[![License](https://img.shields.io/badge/License-Apache%202.0-yellow)](LICENSE.txt)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![CUDA](https://img.shields.io/badge/CUDA-12.x-green)](https://developer.nvidia.com/cuda-toolkit)
</div>

## 🌟 What's New in This Fork

This fork extends the original [MonkeyOCR](https://github.com/Yuliang-Liu/MonkeyOCR) with:

- **Multi-Model Support**: Switch between Qwen2.5-VL-3B and Qwen3-VL-8B
- **Enhanced Handwritten Recognition**: Significantly improved accuracy for handwritten ancient Chinese
- **Flexible Configuration**: YAML-based model configuration system
- **Taoist Manuscript Optimization**: Tested and optimized for classical Chinese texts

## 📊 Model Comparison

| Metric | Qwen2.5-VL-3B | Qwen3-VL-8B |
|--------|---------------|-------------|
| Parameters | 3B | 8B |
| Speed (46 pages) | ~10 min | ~93 min |
| VRAM Usage | ~12GB | ~25-27GB |
| Printed Text | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Handwritten | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Ancient Chinese | ⭐⭐ | ⭐⭐⭐⭐⭐ |

See [detailed comparison report](docs/MULTI_MODEL_COMPARISON.md).

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- CUDA 12.x
- 16GB+ VRAM (for Qwen2.5-VL-3B) or 32GB+ VRAM (for Qwen3-VL-8B)

### Installation

```bash
# Clone repository
git clone https://github.com/neosun100/monkeyocr-multimodel.git
cd monkeyocr-multimodel

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Download models
python tools/download_model.py -n MonkeyOCR-pro-3B
# Optional: Download Qwen3-VL-8B for better handwritten recognition
# huggingface-cli download Qwen/Qwen3-VL-8B-Instruct --local-dir model_weight/Qwen3-VL-8B-Instruct
```

### Usage

```bash
# Standard parsing (Qwen2.5-VL-3B - fast)
python parse.py input.pdf

# High-accuracy parsing (Qwen3-VL-8B - for handwritten)
python parse.py input.pdf -c model_configs_qwen3vl.yaml

# Batch processing
python parse.py /path/to/folder -g 20
```

## 🐳 Docker Deployment

```bash
# Build image
docker compose build monkeyocr

# Run Gradio demo
docker compose up monkeyocr-demo

# Run FastAPI service
docker compose up monkeyocr-api
```

Access:
- Gradio Demo: http://localhost:7860
- API Docs: http://localhost:7861/docs

## ⚙️ Configuration

### Model Configuration Files

**Fast Mode** (`model_configs.yaml`):
```yaml
device: cuda
models_dir: model_weight
chat_config:
  model: MonkeyOCR-pro-3B
  backend: lmdeploy
  batch_size: 5
```

**Accuracy Mode** (`model_configs_qwen3vl.yaml`):
```yaml
device: cuda
models_dir: model_weight
chat_config:
  model: Qwen3-VL-8B-Instruct
  backend: qwen3vl
  batch_size: 3
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
PORT=7870
NVIDIA_VISIBLE_DEVICES=0
GPU_IDLE_TIMEOUT=600
MODEL_NAME=MonkeyOCR-pro-3B
```

## 📁 Project Structure

```
monkeyocr-multimodel/
├── magic_pdf/              # Core parsing library
│   ├── model/              # Model implementations
│   │   ├── custom_model.py # Multi-model support (Qwen2.5/Qwen3)
│   │   └── batch_analyze_llm.py
│   └── ...
├── api/                    # FastAPI service
├── demo/                   # Gradio demo
├── docker/                 # Docker configurations
├── docs/                   # Documentation
│   ├── MULTI_MODEL_COMPARISON.md
│   └── MULTI_MODEL_COMPARISON_CN.md
├── model_configs.yaml      # Default config
├── model_configs_qwen3vl.yaml  # Qwen3-VL config
├── parse.py                # Main entry point
└── requirements.txt
```

## 🔧 Technical Details

### Key Modifications

1. **Multi-Model Backend**: Added `MonkeyChat_Qwen3VL` class supporting Qwen3-VL-8B
2. **ImageBody OCR**: Enabled OCR for `category_id=3` regions (previously skipped)
3. **Flash Attention**: Auto-detection for both Qwen2.5-VL and Qwen3-VL
4. **Enhanced Prompts**: Optimized prompts for handwritten/ancient text

### Supported Backends

| Backend | Model | Use Case |
|---------|-------|----------|
| `lmdeploy` | MonkeyOCR-pro-3B | Fast, general documents |
| `qwen3vl` | Qwen3-VL-8B | Handwritten, ancient texts |
| `vllm` | Various | High-throughput serving |
| `api` | OpenAI-compatible | External API integration |

## 📈 Benchmark Results

Tested on Taoist manuscript (46 pages, handwritten):

| Character | Qwen2.5-VL-3B | Qwen3-VL-8B | Correct |
|-----------|---------------|-------------|---------|
| 金光篆 | 金光藻 ❌ | 金光篆 ✅ | 篆 |
| 棒敕下人间 | 棒救下人间 ❌ | 棒敕下人间 ✅ | 敕 |

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the Apache 2.0 License - see [LICENSE.txt](LICENSE.txt).

## 🙏 Acknowledgments

- [MonkeyOCR](https://github.com/Yuliang-Liu/MonkeyOCR) - Original project
- [Qwen-VL](https://github.com/QwenLM/Qwen2.5-VL) - Vision-Language models
- [LMDeploy](https://github.com/InternLM/lmdeploy) - Inference framework

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/monkeyocr-multimodel&type=Date)](https://star-history.com/#neosun100/monkeyocr-multimodel)

## 📱 Follow Us

![WeChat](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)
