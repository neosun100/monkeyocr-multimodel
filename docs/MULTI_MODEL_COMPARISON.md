# Multi-Model Comparison Report: Handwritten Chinese OCR

[English](MULTI_MODEL_COMPARISON.md) | [简体中文](MULTI_MODEL_COMPARISON_CN.md)

## Overview

This document presents a comprehensive comparison between **Qwen2.5-VL-3B** (original MonkeyOCR backend) and **Qwen3-VL-8B-Instruct** for handwritten ancient Chinese text recognition, specifically tested on Taoist manuscript PDFs.

## Test Environment

| Component | Specification |
|-----------|---------------|
| GPU | NVIDIA L40S (46GB VRAM) |
| Test Document | Taoist manuscript PDF (46 pages, 60MB) |
| Test Date | January 2026 |

## Performance Metrics

| Metric | Qwen2.5-VL-3B | Qwen3-VL-8B |
|--------|---------------|-------------|
| Parameters | 3 Billion | 8 Billion |
| Processing Time (46 pages) | ~10 minutes | ~93 minutes |
| Speed | ~4.6 pages/min | ~0.5 pages/min |
| VRAM Usage | ~12GB | ~25-27GB |
| Speed Ratio | 1x (baseline) | ~0.11x (9x slower) |

## Recognition Accuracy Comparison

### Sample 1: "金光篆" (Golden Light Seal Script)

| Model | Recognition Result | Correct? |
|-------|-------------------|----------|
| Qwen2.5-VL-3B | 金光**藻** | ❌ Wrong |
| Qwen3-VL-8B | 金光**篆** | ✅ Correct |

**Analysis**: The character "篆" (zhuàn - seal script) was misrecognized as "藻" (zǎo - algae) by the 3B model. These characters share similar visual components but have completely different meanings in Taoist context.

### Sample 2: "棒敕下人间" (Divine Decree to the Mortal World)

| Model | Recognition Result | Correct? |
|-------|-------------------|----------|
| Qwen2.5-VL-3B | 棒**救**下人间 | ❌ Wrong |
| Qwen3-VL-8B | 棒**敕**下人间 | ✅ Correct |

**Analysis**: The character "敕" (chì - imperial/divine decree) is a common term in Taoist texts. The 3B model incorrectly recognized it as "救" (jiù - rescue), which changes the meaning entirely.

## Technical Implementation

### Code Modifications

1. **`magic_pdf/model/custom_model.py`**
   - Added `MonkeyChat_Qwen3VL` class for Qwen3-VL support
   - Added `qwen3vl` backend option
   - Implemented flash_attention_2 detection for both Qwen2.5-VL and Qwen3-VL

2. **`magic_pdf/model/batch_analyze_llm.py`**
   - Added `category_id=3` (ImageBody) to OCR processing pipeline
   - Enhanced prompts for handwritten/ancient Chinese text recognition

### Configuration Files

**Qwen3-VL Configuration** (`model_configs_qwen3vl.yaml`):
```yaml
device: cuda
models_dir: model_weight
chat_config:
  model: Qwen3-VL-8B-Instruct
  backend: qwen3vl
  batch_size: 3
```

**Original Configuration** (`model_configs_original.yaml`):
```yaml
device: cuda
models_dir: model_weight
chat_config:
  model: MonkeyOCR-pro-3B
  backend: lmdeploy
  batch_size: 5
```

### Usage

```bash
# Use Qwen3-VL-8B for better handwritten recognition
python parse.py input.pdf -c model_configs_qwen3vl.yaml

# Use original Qwen2.5-VL-3B for faster processing
python parse.py input.pdf -c model_configs_original.yaml
```

## Conclusions

### When to Use Qwen3-VL-8B

✅ **Recommended for:**
- Handwritten manuscripts
- Ancient Chinese texts (Taoist, Buddhist, Classical)
- Documents requiring high accuracy
- Research and archival digitization
- Complex calligraphic styles

### When to Use Qwen2.5-VL-3B

✅ **Recommended for:**
- Printed documents
- High-volume processing
- Time-sensitive tasks
- Standard Chinese/English documents
- Limited GPU resources

### Trade-off Summary

| Aspect | Qwen2.5-VL-3B | Qwen3-VL-8B |
|--------|---------------|-------------|
| Speed | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Accuracy (Printed) | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Accuracy (Handwritten) | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| VRAM Efficiency | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Ancient Chinese | ⭐⭐ | ⭐⭐⭐⭐⭐ |

## Future Improvements

1. **Quantization**: Apply AWQ/GPTQ quantization to Qwen3-VL-8B for faster inference
2. **Batch Optimization**: Tune batch sizes for optimal throughput
3. **Hybrid Pipeline**: Auto-detect handwritten regions and route to appropriate model
4. **Fine-tuning**: Consider fine-tuning on domain-specific datasets (Taoist texts)

---

*Report generated: January 2026*
*Test conducted on MonkeyOCR Multi-Model Fork*
