# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-01-04

### Added
- Multi-model support: Qwen2.5-VL-3B and Qwen3-VL-8B-Instruct
- `MonkeyChat_Qwen3VL` class for Qwen3-VL backend
- ImageBody (category_id=3) OCR processing for handwritten content
- Model configuration files (`model_configs_qwen3vl.yaml`, `model_configs_original.yaml`)
- Multi-language README (English, 简体中文, 繁體中文, 日本語)
- Detailed model comparison report
- All-in-One Docker image with embedded models
- Docker Compose configurations
- MCP (Model Context Protocol) server integration

### Changed
- Enhanced prompts for handwritten/ancient Chinese text recognition
- Updated `.gitignore` for better security
- Flash Attention auto-detection for both Qwen2.5-VL and Qwen3-VL

### Performance
- Qwen2.5-VL-3B: ~4.6 pages/min, ~12GB VRAM
- Qwen3-VL-8B: ~0.5 pages/min, ~25-27GB VRAM (9x slower but significantly better accuracy for handwritten text)

### Docker
- Image: `neosun/monkeyocr-multimodel:1.0.0`
- Size: ~43GB (includes all models)
- Supports: Gradio UI, FastAPI, MCP

---

Based on [MonkeyOCR](https://github.com/Yuliang-Liu/MonkeyOCR) by Yuliang Liu et al.
