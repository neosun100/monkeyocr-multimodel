#!/usr/bin/env python3
"""
MonkeyOCR MCP Server
Model Context Protocol interface for programmatic access
"""

import os
import sys
import json
import tempfile
import asyncio
from typing import Optional
from pathlib import Path

from fastmcp import FastMCP

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from magic_pdf.model.model_manager import model_manager
from loguru import logger

# Initialize MCP server
mcp = FastMCP(
    "MonkeyOCR",
    description="Document parsing with Structure-Recognition-Relation paradigm. Supports PDF and image OCR, formula recognition, and table extraction."
)

# GPU Manager for resource tracking
class GPUResourceManager:
    def __init__(self):
        self.model_loaded = False
        self.idle_timeout = int(os.getenv("GPU_IDLE_TIMEOUT", "600"))
        self._last_use = None
        
    def ensure_model(self):
        """Ensure model is loaded"""
        if not model_manager.is_model_loaded():
            logger.info("Loading MonkeyOCR model...")
            model_manager.initialize_model()
            self.model_loaded = True
        self._last_use = asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else None
        return model_manager.get_model()
    
    def get_status(self) -> dict:
        """Get GPU status"""
        status = {
            "model_loaded": model_manager.is_model_loaded(),
            "idle_timeout": self.idle_timeout
        }
        try:
            import torch
            if torch.cuda.is_available():
                status["gpu_available"] = True
                status["gpu_count"] = torch.cuda.device_count()
                status["current_device"] = torch.cuda.current_device()
                status["device_name"] = torch.cuda.get_device_name()
                status["memory_allocated_mb"] = round(torch.cuda.memory_allocated() / 1024 / 1024, 2)
                status["memory_reserved_mb"] = round(torch.cuda.memory_reserved() / 1024 / 1024, 2)
            else:
                status["gpu_available"] = False
        except Exception as e:
            status["gpu_error"] = str(e)
        return status
    
    def offload(self) -> dict:
        """Release GPU memory"""
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

gpu_manager = GPUResourceManager()


@mcp.tool()
def parse_document(
    file_path: str,
    split_pages: bool = False,
    output_dir: Optional[str] = None
) -> dict:
    """
    Parse a PDF or image document to extract structured content.
    
    Args:
        file_path: Path to PDF or image file
        split_pages: Whether to split output by pages
        output_dir: Output directory (default: temp directory)
    
    Returns:
        Dictionary with parsing results including markdown content and file paths
    """
    try:
        if not os.path.exists(file_path):
            return {"status": "error", "error": f"File not found: {file_path}"}
        
        model = gpu_manager.ensure_model()
        
        from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
        from magic_pdf.data.dataset import PymuDocDataset, ImageDataset
        from magic_pdf.model.doc_analyze_by_custom_model_llm import doc_analyze_llm
        
        # Setup output
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix="monkeyocr_")
        
        name = Path(file_path).stem
        local_md_dir = os.path.join(output_dir, name)
        local_image_dir = os.path.join(local_md_dir, "images")
        os.makedirs(local_image_dir, exist_ok=True)
        
        # Read file
        reader = FileBasedDataReader()
        file_bytes = reader.read(file_path)
        
        # Create dataset
        ext = Path(file_path).suffix.lower()
        if ext == ".pdf":
            ds = PymuDocDataset(file_bytes)
        else:
            ds = ImageDataset(file_bytes)
        
        # Process
        image_writer = FileBasedDataWriter(local_image_dir)
        md_writer = FileBasedDataWriter(local_md_dir)
        
        infer_result = ds.apply(doc_analyze_llm, MonkeyOCR_model=model, split_pages=split_pages)
        
        if isinstance(infer_result, list):
            # Multiple pages
            results = []
            for idx, page_result in enumerate(infer_result):
                page_dir = os.path.join(local_md_dir, f"page_{idx}")
                os.makedirs(os.path.join(page_dir, "images"), exist_ok=True)
                page_writer = FileBasedDataWriter(page_dir)
                page_img_writer = FileBasedDataWriter(os.path.join(page_dir, "images"))
                
                pipe_result = page_result.pipe_ocr_mode(page_img_writer, MonkeyOCR_model=model)
                pipe_result.dump_md(page_writer, f"{name}_page_{idx}.md", "images")
                
                md_path = os.path.join(page_dir, f"{name}_page_{idx}.md")
                with open(md_path, 'r', encoding='utf-8') as f:
                    results.append({"page": idx, "content": f.read(), "path": md_path})
            
            return {
                "status": "success",
                "pages": len(results),
                "results": results,
                "output_dir": local_md_dir
            }
        else:
            # Single result
            pipe_result = infer_result.pipe_ocr_mode(image_writer, MonkeyOCR_model=model)
            pipe_result.dump_md(md_writer, f"{name}.md", "images")
            pipe_result.dump_middle_json(md_writer, f"{name}_middle.json")
            
            md_path = os.path.join(local_md_dir, f"{name}.md")
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "status": "success",
                "content": content,
                "markdown_path": md_path,
                "output_dir": local_md_dir
            }
            
    except Exception as e:
        logger.error(f"Parse error: {e}")
        gpu_manager.offload()
        return {"status": "error", "error": str(e)}


@mcp.tool()
def extract_text(file_path: str) -> dict:
    """
    Extract text content from an image or PDF.
    
    Args:
        file_path: Path to image or PDF file
    
    Returns:
        Dictionary with extracted text content
    """
    return _single_task(file_path, "text", "Please output the text content from the image.")


@mcp.tool()
def extract_formula(file_path: str) -> dict:
    """
    Extract mathematical formulas from an image in LaTeX format.
    
    Args:
        file_path: Path to image file containing formula
    
    Returns:
        Dictionary with LaTeX formula content
    """
    return _single_task(file_path, "formula", "Please write out the expression of the formula in the image using LaTeX format.")


@mcp.tool()
def extract_table(file_path: str, format: str = "html") -> dict:
    """
    Extract table from an image.
    
    Args:
        file_path: Path to image file containing table
        format: Output format - 'html' or 'latex'
    
    Returns:
        Dictionary with table content in specified format
    """
    if format == "latex":
        instruction = "This is the image of a table. Please output the table in LaTeX format."
    else:
        instruction = "This is the image of a table. Please output the table in html format."
    return _single_task(file_path, "table", instruction)


def _single_task(file_path: str, task: str, instruction: str) -> dict:
    """Internal function for single-task recognition"""
    try:
        if not os.path.exists(file_path):
            return {"status": "error", "error": f"File not found: {file_path}"}
        
        model = gpu_manager.ensure_model()
        
        from magic_pdf.utils.load_image import pdf_to_images
        from PIL import Image
        
        ext = Path(file_path).suffix.lower()
        if ext == ".pdf":
            images = pdf_to_images(file_path)
        elif ext in [".jpg", ".jpeg", ".png"]:
            images = [Image.open(file_path)]
        else:
            return {"status": "error", "error": f"Unsupported format: {ext}"}
        
        instructions = [instruction] * len(images)
        responses = model.chat_model.batch_inference(images, instructions)
        
        content = "\n\n".join(responses)
        
        return {
            "status": "success",
            "task": task,
            "pages": len(images),
            "content": content
        }
        
    except Exception as e:
        logger.error(f"{task} extraction error: {e}")
        gpu_manager.offload()
        return {"status": "error", "error": str(e)}


@mcp.tool()
def get_gpu_status() -> dict:
    """
    Get current GPU status and memory usage.
    
    Returns:
        Dictionary with GPU information
    """
    return gpu_manager.get_status()


@mcp.tool()
def release_gpu_memory() -> dict:
    """
    Release GPU memory to free up resources.
    
    Returns:
        Dictionary with operation status
    """
    return gpu_manager.offload()


@mcp.tool()
def get_model_info() -> dict:
    """
    Get information about the loaded model.
    
    Returns:
        Dictionary with model configuration
    """
    try:
        model = model_manager.get_model()
        if model is None:
            return {"status": "not_loaded", "message": "Model not yet loaded"}
        
        return {
            "status": "loaded",
            "layout_model": model.layout_model_name,
            "chat_backend": model.chat_config.get("backend", "unknown"),
            "device": model.device,
            "supports_async": model_manager.get_async_support()
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    mcp.run()
