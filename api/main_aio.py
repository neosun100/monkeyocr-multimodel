#!/usr/bin/env python3
"""
MonkeyOCR All-in-One API
Combines UI (Gradio) + API (FastAPI) + Health endpoints in single service
"""

import os
import sys
import tempfile
import time
import uuid
import zipfile
import asyncio
from typing import Optional, List
from pathlib import Path
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from tempfile import gettempdir
from loguru import logger
import uvicorn
import gradio as gr

# Add project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from magic_pdf.model.model_manager import model_manager

# Response models
class TaskResponse(BaseModel):
    success: bool
    task_type: str
    content: str
    message: Optional[str] = None

class ParseResponse(BaseModel):
    success: bool
    message: str
    output_dir: Optional[str] = None
    files: Optional[List[str]] = None
    download_url: Optional[str] = None

class GPUStatus(BaseModel):
    model_loaded: bool
    gpu_available: bool
    gpu_name: Optional[str] = None
    memory_used_mb: Optional[float] = None
    memory_total_mb: Optional[float] = None

# Global executor
executor = ThreadPoolExecutor(max_workers=4)

def initialize_model():
    """Initialize MonkeyOCR model"""
    config_path = os.getenv("MONKEYOCR_CONFIG", "model_configs.yaml")
    return model_manager.initialize_model(config_path)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler"""
    try:
        initialize_model()
        logger.info("✅ MonkeyOCR model initialized")
    except Exception as e:
        logger.error(f"❌ Model initialization failed: {e}")
        raise
    yield
    executor.shutdown(wait=True)
    logger.info("🔄 Shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="MonkeyOCR API",
    description="""
# MonkeyOCR - Document Parsing API

支持 PDF 和图片的文档解析，包括：
- 📄 完整文档解析 (结构+识别+关系)
- 📝 文本提取
- 🔢 公式识别 (LaTeX)
- 📊 表格提取 (HTML/LaTeX)

## 访问方式
- **Web UI**: [/demo](/demo)
- **API 文档**: [/docs](/docs)
- **MCP**: 通过 stdio 连接
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Setup temp directory
temp_dir = os.getenv("TMPDIR", gettempdir())
os.makedirs(temp_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=temp_dir), name="static")

# ============== Health & Status ==============

@app.get("/", include_in_schema=False)
async def root():
    """Redirect to demo"""
    return RedirectResponse(url="/demo")

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "model_loaded": model_manager.is_model_loaded(),
        "timestamp": time.time()
    }

@app.get("/gpu/status", response_model=GPUStatus)
async def gpu_status():
    """获取 GPU 状态"""
    try:
        import torch
        status = GPUStatus(
            model_loaded=model_manager.is_model_loaded(),
            gpu_available=torch.cuda.is_available()
        )
        if torch.cuda.is_available():
            status.gpu_name = torch.cuda.get_device_name()
            status.memory_used_mb = round(torch.cuda.memory_allocated() / 1024 / 1024, 2)
            status.memory_total_mb = round(torch.cuda.get_device_properties(0).total_memory / 1024 / 1024, 2)
        return status
    except Exception as e:
        return GPUStatus(model_loaded=False, gpu_available=False)

@app.post("/gpu/offload")
async def gpu_offload():
    """释放 GPU 显存"""
    try:
        import torch
        import gc
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        return {"status": "success", "message": "GPU memory released"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ============== OCR Endpoints ==============

@app.post("/ocr/text", response_model=TaskResponse)
async def extract_text(file: UploadFile = File(...)):
    """提取文本内容"""
    return await perform_ocr_task(file, "text")

@app.post("/ocr/formula", response_model=TaskResponse)
async def extract_formula(file: UploadFile = File(...)):
    """提取数学公式 (LaTeX)"""
    return await perform_ocr_task(file, "formula")

@app.post("/ocr/table", response_model=TaskResponse)
async def extract_table(file: UploadFile = File(...)):
    """提取表格 (HTML)"""
    return await perform_ocr_task(file, "table")

@app.post("/parse", response_model=ParseResponse)
async def parse_document(file: UploadFile = File(...)):
    """完整文档解析"""
    return await parse_document_internal(file, split_pages=False)

@app.post("/parse/split", response_model=ParseResponse)
async def parse_document_split(file: UploadFile = File(...)):
    """文档解析 (按页分割)"""
    return await parse_document_internal(file, split_pages=True)

# ============== Internal Functions ==============

TASK_INSTRUCTIONS = {
    'text': 'Please output the text content from the image.',
    'formula': 'Please write out the expression of the formula in the image using LaTeX format.',
    'table': 'This is the image of a table. Please output the table in html format.'
}

async def perform_ocr_task(file: UploadFile, task_type: str) -> TaskResponse:
    """Perform OCR task"""
    try:
        model = model_manager.get_model()
        if not model:
            raise HTTPException(status_code=500, detail="Model not initialized")
        
        # Validate file
        allowed_ext = {'.pdf', '.jpg', '.jpeg', '.png'}
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_ext:
            raise HTTPException(status_code=400, detail=f"Unsupported: {file_ext}")
        
        # Save temp file
        unique_id = str(uuid.uuid4())[:8]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext, prefix=f"ocr_{unique_id}_") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Load images
            def load_images():
                if file_ext == '.pdf':
                    from magic_pdf.utils.load_image import pdf_to_images
                    return pdf_to_images(tmp_path)
                else:
                    from PIL import Image
                    return [Image.open(tmp_path)]
            
            images = await asyncio.get_event_loop().run_in_executor(None, load_images)
            
            # Run inference
            instruction = TASK_INSTRUCTIONS.get(task_type, TASK_INSTRUCTIONS['text'])
            instructions = [instruction] * len(images)
            
            responses = await asyncio.get_event_loop().run_in_executor(
                None, model.chat_model.batch_inference, images, instructions
            )
            
            result = "\n\n".join(responses)
            
            return TaskResponse(
                success=True,
                task_type=task_type,
                content=result,
                message=f"{task_type} extraction completed"
            )
        finally:
            os.unlink(tmp_path)
            
    except Exception as e:
        logger.error(f"OCR error: {e}")
        return TaskResponse(success=False, task_type=task_type, content="", message=str(e))

async def parse_document_internal(file: UploadFile, split_pages: bool = False) -> ParseResponse:
    """Parse document"""
    try:
        model = model_manager.get_model()
        if not model:
            raise HTTPException(status_code=500, detail="Model not initialized")
        
        # Validate
        allowed_ext = {'.pdf', '.jpg', '.jpeg', '.png'}
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_ext:
            raise HTTPException(status_code=400, detail=f"Unsupported: {file_ext}")
        
        original_name = Path(file.filename).stem
        unique_id = str(uuid.uuid4())[:8]
        
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext, prefix=f"parse_{unique_id}_") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            output_dir = tempfile.mkdtemp(prefix=f"monkeyocr_{unique_id}_")
            
            # Parse
            def do_parse():
                from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
                from magic_pdf.data.dataset import PymuDocDataset, ImageDataset
                from magic_pdf.model.doc_analyze_by_custom_model_llm import doc_analyze_llm
                
                name = f"{original_name}_{unique_id}"
                local_md_dir = os.path.join(output_dir, name)
                local_image_dir = os.path.join(local_md_dir, "images")
                os.makedirs(local_image_dir, exist_ok=True)
                
                reader = FileBasedDataReader()
                file_bytes = reader.read(tmp_path)
                
                if file_ext == '.pdf':
                    ds = PymuDocDataset(file_bytes)
                else:
                    ds = ImageDataset(file_bytes)
                
                image_writer = FileBasedDataWriter(local_image_dir)
                md_writer = FileBasedDataWriter(local_md_dir)
                
                infer_result = ds.apply(doc_analyze_llm, MonkeyOCR_model=model, split_pages=split_pages)
                
                if isinstance(infer_result, list):
                    for idx, page_result in enumerate(infer_result):
                        page_dir = os.path.join(local_md_dir, f"page_{idx}")
                        os.makedirs(os.path.join(page_dir, "images"), exist_ok=True)
                        page_writer = FileBasedDataWriter(page_dir)
                        page_img_writer = FileBasedDataWriter(os.path.join(page_dir, "images"))
                        pipe_result = page_result.pipe_ocr_mode(page_img_writer, MonkeyOCR_model=model)
                        pipe_result.dump_md(page_writer, f"{original_name}_page_{idx}.md", "images")
                else:
                    pipe_result = infer_result.pipe_ocr_mode(image_writer, MonkeyOCR_model=model)
                    infer_result.draw_model(os.path.join(local_md_dir, f"{original_name}_model.pdf"))
                    pipe_result.draw_layout(os.path.join(local_md_dir, f"{original_name}_layout.pdf"))
                    pipe_result.dump_md(md_writer, f"{original_name}.md", "images")
                    pipe_result.dump_middle_json(md_writer, f"{original_name}_middle.json")
                
                return local_md_dir
            
            result_dir = await asyncio.get_event_loop().run_in_executor(None, do_parse)
            
            # List files
            files = []
            for root, dirs, filenames in os.walk(result_dir):
                for fn in filenames:
                    rel = os.path.relpath(os.path.join(root, fn), result_dir)
                    files.append(rel)
            
            # Create ZIP
            timestamp = int(time.time() * 1000)
            zip_name = f"{original_name}_parsed_{timestamp}.zip"
            zip_path = os.path.join(temp_dir, zip_name)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, filenames in os.walk(result_dir):
                    for fn in filenames:
                        fp = os.path.join(root, fn)
                        arcname = os.path.relpath(fp, result_dir)
                        zf.write(fp, arcname)
            
            return ParseResponse(
                success=True,
                message="Parsing completed",
                output_dir=result_dir,
                files=files,
                download_url=f"/static/{zip_name}"
            )
            
        finally:
            os.unlink(tmp_path)
            
    except Exception as e:
        logger.error(f"Parse error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============== Mount Gradio ==============

from demo.demo_gradio import create_gradio_app
gradio_app = create_gradio_app()
gradio_app.queue()
app = gr.mount_gradio_app(app, gradio_app, path="/demo")

# Custom OpenAPI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    schema.setdefault("paths", {})
    schema["paths"]["/demo"] = {
        "get": {
            "summary": "Web UI Demo",
            "description": "Gradio-based interactive demo",
            "responses": {"200": {"description": "Gradio UI"}}
        }
    }
    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi

if __name__ == "__main__":
    port = int(os.getenv("PORT", "7870"))
    logger.info(f"Starting MonkeyOCR All-in-One on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
