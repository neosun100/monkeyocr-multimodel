# 多模型对比报告：手写中文古籍 OCR

[English](MULTI_MODEL_COMPARISON.md) | [简体中文](MULTI_MODEL_COMPARISON_CN.md)

## 概述

本文档详细对比了 **Qwen2.5-VL-3B**（MonkeyOCR 原版后端）与 **Qwen3-VL-8B-Instruct** 在手写古籍中文识别方面的表现，测试样本为道教手抄本 PDF。

## 测试环境

| 组件 | 规格 |
|------|------|
| GPU | NVIDIA L40S (46GB 显存) |
| 测试文档 | 道教手抄本 PDF (46页, 60MB) |
| 测试日期 | 2026年1月 |

## 性能指标

| 指标 | Qwen2.5-VL-3B | Qwen3-VL-8B |
|------|---------------|-------------|
| 模型参数 | 30亿 | 80亿 |
| 处理时间 (46页) | ~10分钟 | ~93分钟 |
| 处理速度 | ~4.6页/分钟 | ~0.5页/分钟 |
| 显存占用 | ~12GB | ~25-27GB |
| 速度比 | 1x (基准) | ~0.11x (慢9倍) |

## 识别准确率对比

### 样本1："金光篆"

| 模型 | 识别结果 | 是否正确 |
|------|----------|----------|
| Qwen2.5-VL-3B | 金光**藻** | ❌ 错误 |
| Qwen3-VL-8B | 金光**篆** | ✅ 正确 |

**分析**："篆"（zhuàn - 篆书）被3B模型误识别为"藻"（zǎo - 藻类）。这两个字在视觉上有相似的部件，但在道教语境中含义完全不同。

### 样本2："棒敕下人间"

| 模型 | 识别结果 | 是否正确 |
|------|----------|----------|
| Qwen2.5-VL-3B | 棒**救**下人间 | ❌ 错误 |
| Qwen3-VL-8B | 棒**敕**下人间 | ✅ 正确 |

**分析**："敕"（chì - 敕令/诏令）是道教文献中的常用术语。3B模型将其误识别为"救"（jiù - 救助），完全改变了原意。

## 技术实现

### 代码修改

1. **`magic_pdf/model/custom_model.py`**
   - 新增 `MonkeyChat_Qwen3VL` 类支持 Qwen3-VL
   - 添加 `qwen3vl` 后端选项
   - 实现 flash_attention_2 自动检测（同时支持 Qwen2.5-VL 和 Qwen3-VL）

2. **`magic_pdf/model/batch_analyze_llm.py`**
   - 将 `category_id=3`（ImageBody）加入 OCR 处理流程
   - 增强手写体/古籍中文识别的提示词

### 配置文件

**Qwen3-VL 配置** (`model_configs_qwen3vl.yaml`):
```yaml
device: cuda
models_dir: model_weight
chat_config:
  model: Qwen3-VL-8B-Instruct
  backend: qwen3vl
  batch_size: 3
```

**原版配置** (`model_configs_original.yaml`):
```yaml
device: cuda
models_dir: model_weight
chat_config:
  model: MonkeyOCR-pro-3B
  backend: lmdeploy
  batch_size: 5
```

### 使用方法

```bash
# 使用 Qwen3-VL-8B 获得更好的手写识别效果
python parse.py input.pdf -c model_configs_qwen3vl.yaml

# 使用原版 Qwen2.5-VL-3B 获得更快的处理速度
python parse.py input.pdf -c model_configs_original.yaml
```

## 结论

### 何时使用 Qwen3-VL-8B

✅ **推荐场景：**
- 手写稿本
- 古籍文献（道教、佛教、古典文献）
- 对准确率要求高的场景
- 研究和档案数字化
- 复杂书法风格

### 何时使用 Qwen2.5-VL-3B

✅ **推荐场景：**
- 印刷体文档
- 大批量处理
- 时间敏感任务
- 标准中英文文档
- GPU 资源有限

### 权衡总结

| 方面 | Qwen2.5-VL-3B | Qwen3-VL-8B |
|------|---------------|-------------|
| 速度 | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| 印刷体准确率 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 手写体准确率 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 显存效率 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 古籍识别 | ⭐⭐ | ⭐⭐⭐⭐⭐ |

## 未来改进方向

1. **量化**：对 Qwen3-VL-8B 应用 AWQ/GPTQ 量化以加速推理
2. **批处理优化**：调整批处理大小以获得最佳吞吐量
3. **混合流水线**：自动检测手写区域并路由到合适的模型
4. **微调**：考虑在特定领域数据集（道教文献）上进行微调

---

*报告生成时间：2026年1月*
*测试基于 MonkeyOCR 多模型分支*
