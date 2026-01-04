# MonkeyOCR MCP Guide

MonkeyOCR 提供 Model Context Protocol (MCP) 接口，支持程序化访问文档解析功能。

## 快速开始

### 1. MCP 配置

在你的 MCP 客户端配置文件中添加：

```json
{
  "mcpServers": {
    "monkeyocr": {
      "command": "docker",
      "args": ["exec", "-i", "monkeyocr-aio", "python", "mcp_server.py"],
      "env": {
        "GPU_IDLE_TIMEOUT": "600"
      }
    }
  }
}
```

或者本地运行：

```json
{
  "mcpServers": {
    "monkeyocr": {
      "command": "python",
      "args": ["/path/to/MonkeyOCR/mcp_server.py"],
      "env": {
        "MONKEYOCR_CONFIG": "/path/to/MonkeyOCR/model_configs.yaml"
      }
    }
  }
}
```

## 可用工具

### 1. parse_document - 文档解析

完整解析 PDF 或图片文档，提取结构化内容。

**参数：**
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| file_path | string | ✅ | PDF 或图片文件路径 |
| split_pages | bool | ❌ | 是否按页分割输出 (默认: false) |
| output_dir | string | ❌ | 输出目录 (默认: 临时目录) |

**返回示例：**
```json
{
  "status": "success",
  "content": "# Document Title\n\nParsed content...",
  "markdown_path": "/tmp/monkeyocr_xxx/doc/doc.md",
  "output_dir": "/tmp/monkeyocr_xxx/doc"
}
```

### 2. extract_text - 文本提取

从图片或 PDF 中提取纯文本内容。

**参数：**
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| file_path | string | ✅ | 图片或 PDF 文件路径 |

**返回示例：**
```json
{
  "status": "success",
  "task": "text",
  "pages": 1,
  "content": "Extracted text content..."
}
```

### 3. extract_formula - 公式识别

从图片中识别数学公式，输出 LaTeX 格式。

**参数：**
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| file_path | string | ✅ | 包含公式的图片路径 |

**返回示例：**
```json
{
  "status": "success",
  "task": "formula",
  "pages": 1,
  "content": "$$E = mc^2$$"
}
```

### 4. extract_table - 表格提取

从图片中提取表格，支持 HTML 或 LaTeX 格式。

**参数：**
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| file_path | string | ✅ | 包含表格的图片路径 |
| format | string | ❌ | 输出格式: "html" 或 "latex" (默认: html) |

**返回示例：**
```json
{
  "status": "success",
  "task": "table",
  "pages": 1,
  "content": "<table><tr><td>...</td></tr></table>"
}
```

### 5. get_gpu_status - GPU 状态

获取当前 GPU 状态和显存使用情况。

**参数：** 无

**返回示例：**
```json
{
  "model_loaded": true,
  "gpu_available": true,
  "gpu_count": 1,
  "device_name": "NVIDIA L40S",
  "memory_allocated_mb": 8192.5,
  "memory_reserved_mb": 10240.0
}
```

### 6. release_gpu_memory - 释放显存

释放 GPU 显存以释放资源。

**参数：** 无

**返回示例：**
```json
{
  "status": "success",
  "message": "GPU memory released"
}
```

### 7. get_model_info - 模型信息

获取已加载模型的配置信息。

**参数：** 无

**返回示例：**
```json
{
  "status": "loaded",
  "layout_model": "PP-DocLayout_plus-L",
  "chat_backend": "lmdeploy",
  "device": "cuda",
  "supports_async": false
}
```

## 使用示例

### Python 客户端示例

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="docker",
        args=["exec", "-i", "monkeyocr-aio", "python", "mcp_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 解析文档
            result = await session.call_tool(
                "parse_document",
                {"file_path": "/path/to/document.pdf"}
            )
            print(result)
            
            # 提取公式
            result = await session.call_tool(
                "extract_formula",
                {"file_path": "/path/to/formula.png"}
            )
            print(result)

asyncio.run(main())
```

## MCP vs API 对比

| 特性 | MCP | REST API |
|------|-----|----------|
| 通信方式 | stdio | HTTP |
| 适用场景 | AI Agent 集成 | Web 应用/服务 |
| 文件传输 | 本地路径 | 上传文件 |
| 并发支持 | 单会话 | 多并发 |
| 状态管理 | 有状态 | 无状态 |

## 注意事项

1. **文件路径**: MCP 使用本地文件路径，确保路径在容器内可访问
2. **GPU 资源**: 所有工具共享同一个 GPU 管理器，长时间空闲后会自动释放显存
3. **错误处理**: 所有工具返回统一格式，包含 `status` 字段表示成功或失败
4. **首次调用**: 首次调用会触发模型加载，可能需要较长时间

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| GPU_IDLE_TIMEOUT | GPU 空闲超时(秒) | 600 |
| MONKEYOCR_CONFIG | 模型配置文件路径 | model_configs.yaml |
