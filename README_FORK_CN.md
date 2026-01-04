[English](README_FORK.md) | [简体中文](README_FORK_CN.md) | [繁體中文](README_FORK_TW.md) | [日本語](README_FORK_JP.md)

<div align="center">
<h1>MonkeyOCR 多模型分支</h1>
<p>增强版文档解析 - 支持多模型切换，优化手写古籍中文识别</p>

[![License](https://img.shields.io/badge/License-Apache%202.0-yellow)](LICENSE.txt)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![CUDA](https://img.shields.io/badge/CUDA-12.x-green)](https://developer.nvidia.com/cuda-toolkit)
</div>

## 🌟 本分支新特性

本分支在原版 [MonkeyOCR](https://github.com/Yuliang-Liu/MonkeyOCR) 基础上扩展了：

- **多模型支持**：可在 Qwen2.5-VL-3B 和 Qwen3-VL-8B 之间切换
- **增强手写识别**：显著提升手写古籍中文的识别准确率
- **灵活配置**：基于 YAML 的模型配置系统
- **道教文献优化**：针对古典中文文献进行测试和优化

## 📊 模型对比

| 指标 | Qwen2.5-VL-3B | Qwen3-VL-8B |
|------|---------------|-------------|
| 参数量 | 30亿 | 80亿 |
| 速度 (46页) | ~10分钟 | ~93分钟 |
| 显存占用 | ~12GB | ~25-27GB |
| 印刷体 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 手写体 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 古籍识别 | ⭐⭐ | ⭐⭐⭐⭐⭐ |

查看[详细对比报告](docs/MULTI_MODEL_COMPARISON_CN.md)。

## 🚀 快速开始

### 环境要求

- Python 3.10+
- CUDA 12.x
- 16GB+ 显存 (Qwen2.5-VL-3B) 或 32GB+ 显存 (Qwen3-VL-8B)

### 安装

```bash
# 克隆仓库
git clone https://github.com/neosun100/monkeyocr-multimodel.git
cd monkeyocr-multimodel

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或: venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 下载模型
python tools/download_model.py -n MonkeyOCR-pro-3B
# 可选：下载 Qwen3-VL-8B 以获得更好的手写识别效果
# huggingface-cli download Qwen/Qwen3-VL-8B-Instruct --local-dir model_weight/Qwen3-VL-8B-Instruct
```

### 使用方法

```bash
# 标准解析 (Qwen2.5-VL-3B - 快速)
python parse.py input.pdf

# 高精度解析 (Qwen3-VL-8B - 适合手写体)
python parse.py input.pdf -c model_configs_qwen3vl.yaml

# 批量处理
python parse.py /path/to/folder -g 20
```

## 🐳 Docker 部署

```bash
# 构建镜像
docker compose build monkeyocr

# 运行 Gradio 演示
docker compose up monkeyocr-demo

# 运行 FastAPI 服务
docker compose up monkeyocr-api
```

访问地址：
- Gradio 演示: http://localhost:7860
- API 文档: http://localhost:7861/docs

## ⚙️ 配置说明

### 模型配置文件

**快速模式** (`model_configs.yaml`):
```yaml
device: cuda
models_dir: model_weight
chat_config:
  model: MonkeyOCR-pro-3B
  backend: lmdeploy
  batch_size: 5
```

**高精度模式** (`model_configs_qwen3vl.yaml`):
```yaml
device: cuda
models_dir: model_weight
chat_config:
  model: Qwen3-VL-8B-Instruct
  backend: qwen3vl
  batch_size: 3
```

### 环境变量

复制 `.env.example` 到 `.env` 并配置：

```bash
PORT=7870
NVIDIA_VISIBLE_DEVICES=0
GPU_IDLE_TIMEOUT=600
MODEL_NAME=MonkeyOCR-pro-3B
```

## 📁 项目结构

```
monkeyocr-multimodel/
├── magic_pdf/              # 核心解析库
│   ├── model/              # 模型实现
│   │   ├── custom_model.py # 多模型支持 (Qwen2.5/Qwen3)
│   │   └── batch_analyze_llm.py
│   └── ...
├── api/                    # FastAPI 服务
├── demo/                   # Gradio 演示
├── docker/                 # Docker 配置
├── docs/                   # 文档
│   ├── MULTI_MODEL_COMPARISON.md
│   └── MULTI_MODEL_COMPARISON_CN.md
├── model_configs.yaml      # 默认配置
├── model_configs_qwen3vl.yaml  # Qwen3-VL 配置
├── parse.py                # 主入口
└── requirements.txt
```

## 🔧 技术细节

### 主要修改

1. **多模型后端**：新增 `MonkeyChat_Qwen3VL` 类支持 Qwen3-VL-8B
2. **ImageBody OCR**：启用 `category_id=3` 区域的 OCR（之前被跳过）
3. **Flash Attention**：自动检测 Qwen2.5-VL 和 Qwen3-VL 的支持
4. **增强提示词**：针对手写体/古籍文本优化提示词

### 支持的后端

| 后端 | 模型 | 使用场景 |
|------|------|----------|
| `lmdeploy` | MonkeyOCR-pro-3B | 快速，通用文档 |
| `qwen3vl` | Qwen3-VL-8B | 手写体，古籍文献 |
| `vllm` | 多种 | 高吞吐量服务 |
| `api` | OpenAI 兼容 | 外部 API 集成 |

## 📈 测试结果

在道教手抄本上测试（46页，手写体）：

| 原文 | Qwen2.5-VL-3B | Qwen3-VL-8B | 正确答案 |
|------|---------------|-------------|----------|
| 金光篆 | 金光藻 ❌ | 金光篆 ✅ | 篆 |
| 棒敕下人间 | 棒救下人间 ❌ | 棒敕下人间 ✅ | 敕 |

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

## 📄 许可证

本项目采用 Apache 2.0 许可证 - 详见 [LICENSE.txt](LICENSE.txt)。

## 🙏 致谢

- [MonkeyOCR](https://github.com/Yuliang-Liu/MonkeyOCR) - 原始项目
- [Qwen-VL](https://github.com/QwenLM/Qwen2.5-VL) - 视觉语言模型
- [LMDeploy](https://github.com/InternLM/lmdeploy) - 推理框架

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/monkeyocr-multimodel&type=Date)](https://star-history.com/#neosun100/monkeyocr-multimodel)

## 📱 关注公众号

![公众号](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)
