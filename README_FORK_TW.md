[English](README_FORK.md) | [简体中文](README_FORK_CN.md) | [繁體中文](README_FORK_TW.md) | [日本語](README_FORK_JP.md)

<div align="center">
<h1>MonkeyOCR 多模型分支</h1>
<p>增強版文檔解析 - 支援多模型切換，優化手寫古籍中文識別</p>

[![License](https://img.shields.io/badge/License-Apache%202.0-yellow)](LICENSE.txt)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![CUDA](https://img.shields.io/badge/CUDA-12.x-green)](https://developer.nvidia.com/cuda-toolkit)
</div>

## 🌟 本分支新特性

本分支在原版 [MonkeyOCR](https://github.com/Yuliang-Liu/MonkeyOCR) 基礎上擴展了：

- **多模型支援**：可在 Qwen2.5-VL-3B 和 Qwen3-VL-8B 之間切換
- **增強手寫識別**：顯著提升手寫古籍中文的識別準確率
- **靈活配置**：基於 YAML 的模型配置系統
- **道教文獻優化**：針對古典中文文獻進行測試和優化

## 📊 模型對比

| 指標 | Qwen2.5-VL-3B | Qwen3-VL-8B |
|------|---------------|-------------|
| 參數量 | 30億 | 80億 |
| 速度 (46頁) | ~10分鐘 | ~93分鐘 |
| 顯存佔用 | ~12GB | ~25-27GB |
| 印刷體 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 手寫體 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 古籍識別 | ⭐⭐ | ⭐⭐⭐⭐⭐ |

查看[詳細對比報告](docs/MULTI_MODEL_COMPARISON_CN.md)。

## 🚀 快速開始

### 環境要求

- Python 3.10+
- CUDA 12.x
- 16GB+ 顯存 (Qwen2.5-VL-3B) 或 32GB+ 顯存 (Qwen3-VL-8B)

### 安裝

```bash
# 克隆倉庫
git clone https://github.com/neosun100/monkeyocr-multimodel.git
cd monkeyocr-multimodel

# 創建虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或: venv\Scripts\activate  # Windows

# 安裝依賴
pip install -r requirements.txt

# 下載模型
python tools/download_model.py -n MonkeyOCR-pro-3B
```

### 使用方法

```bash
# 標準解析 (Qwen2.5-VL-3B - 快速)
python parse.py input.pdf

# 高精度解析 (Qwen3-VL-8B - 適合手寫體)
python parse.py input.pdf -c model_configs_qwen3vl.yaml

# 批量處理
python parse.py /path/to/folder -g 20
```

## 🐳 Docker 部署

```bash
# 構建鏡像
docker compose build monkeyocr

# 運行 Gradio 演示
docker compose up monkeyocr-demo

# 運行 FastAPI 服務
docker compose up monkeyocr-api
```

訪問地址：
- Gradio 演示: http://localhost:7860
- API 文檔: http://localhost:7861/docs

## 📈 測試結果

在道教手抄本上測試（46頁，手寫體）：

| 原文 | Qwen2.5-VL-3B | Qwen3-VL-8B | 正確答案 |
|------|---------------|-------------|----------|
| 金光篆 | 金光藻 ❌ | 金光篆 ✅ | 篆 |
| 棒敕下人間 | 棒救下人間 ❌ | 棒敕下人間 ✅ | 敕 |

## 📄 許可證

本項目採用 Apache 2.0 許可證 - 詳見 [LICENSE.txt](LICENSE.txt)。

## 🙏 致謝

- [MonkeyOCR](https://github.com/Yuliang-Liu/MonkeyOCR) - 原始項目
- [Qwen-VL](https://github.com/QwenLM/Qwen2.5-VL) - 視覺語言模型
- [LMDeploy](https://github.com/InternLM/lmdeploy) - 推理框架

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/monkeyocr-multimodel&type=Date)](https://star-history.com/#neosun100/monkeyocr-multimodel)

## 📱 關注公眾號

![公眾號](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)
