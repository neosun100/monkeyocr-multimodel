[English](README_FORK.md) | [简体中文](README_FORK_CN.md) | [繁體中文](README_FORK_TW.md) | [日本語](README_FORK_JP.md)

<div align="center">
<h1>MonkeyOCR マルチモデルフォーク</h1>
<p>強化版ドキュメント解析 - マルチモデル対応、手書き古典中国語認識を最適化</p>

[![License](https://img.shields.io/badge/License-Apache%202.0-yellow)](LICENSE.txt)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![CUDA](https://img.shields.io/badge/CUDA-12.x-green)](https://developer.nvidia.com/cuda-toolkit)
</div>

## 🌟 このフォークの新機能

このフォークは、オリジナルの [MonkeyOCR](https://github.com/Yuliang-Liu/MonkeyOCR) を以下の機能で拡張しています：

- **マルチモデル対応**：Qwen2.5-VL-3B と Qwen3-VL-8B の切り替えが可能
- **手書き認識の強化**：手書き古典中国語の認識精度を大幅に向上
- **柔軟な設定**：YAMLベースのモデル設定システム
- **道教文献の最適化**：古典中国語文献でテストと最適化を実施

## 📊 モデル比較

| 指標 | Qwen2.5-VL-3B | Qwen3-VL-8B |
|------|---------------|-------------|
| パラメータ数 | 30億 | 80億 |
| 処理速度 (46ページ) | 約10分 | 約93分 |
| VRAM使用量 | 約12GB | 約25-27GB |
| 印刷文字 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 手書き文字 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 古典文献 | ⭐⭐ | ⭐⭐⭐⭐⭐ |

[詳細な比較レポート](docs/MULTI_MODEL_COMPARISON.md)をご覧ください。

## 🚀 クイックスタート

### 必要条件

- Python 3.10+
- CUDA 12.x
- 16GB+ VRAM (Qwen2.5-VL-3B) または 32GB+ VRAM (Qwen3-VL-8B)

### インストール

```bash
# リポジトリをクローン
git clone https://github.com/neosun100/monkeyocr-multimodel.git
cd monkeyocr-multimodel

# 仮想環境を作成
python -m venv venv
source venv/bin/activate  # Linux/Mac
# または: venv\Scripts\activate  # Windows

# 依存関係をインストール
pip install -r requirements.txt

# モデルをダウンロード
python tools/download_model.py -n MonkeyOCR-pro-3B
```

### 使用方法

```bash
# 標準解析 (Qwen2.5-VL-3B - 高速)
python parse.py input.pdf

# 高精度解析 (Qwen3-VL-8B - 手書き向け)
python parse.py input.pdf -c model_configs_qwen3vl.yaml

# バッチ処理
python parse.py /path/to/folder -g 20
```

## 🐳 Docker デプロイ

```bash
# イメージをビルド
docker compose build monkeyocr

# Gradio デモを実行
docker compose up monkeyocr-demo

# FastAPI サービスを実行
docker compose up monkeyocr-api
```

アクセス先：
- Gradio デモ: http://localhost:7860
- API ドキュメント: http://localhost:7861/docs

## 📈 テスト結果

道教手写本でテスト（46ページ、手書き）：

| 原文 | Qwen2.5-VL-3B | Qwen3-VL-8B | 正解 |
|------|---------------|-------------|------|
| 金光篆 | 金光藻 ❌ | 金光篆 ✅ | 篆 |
| 棒敕下人間 | 棒救下人間 ❌ | 棒敕下人間 ✅ | 敕 |

## 📄 ライセンス

このプロジェクトは Apache 2.0 ライセンスの下で公開されています - [LICENSE.txt](LICENSE.txt) を参照してください。

## 🙏 謝辞

- [MonkeyOCR](https://github.com/Yuliang-Liu/MonkeyOCR) - オリジナルプロジェクト
- [Qwen-VL](https://github.com/QwenLM/Qwen2.5-VL) - ビジョン言語モデル
- [LMDeploy](https://github.com/InternLM/lmdeploy) - 推論フレームワーク

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/monkeyocr-multimodel&type=Date)](https://star-history.com/#neosun100/monkeyocr-multimodel)

## 📱 公式アカウント

![WeChat](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)
