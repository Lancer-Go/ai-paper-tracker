"""
src/processing/translator.py — 论文翻译核心逻辑

提取自 translate_papers.py，负责 PDF 下载、文本提取、文本翻译。
"""

import time
import logging
from pathlib import Path
from typing import Optional

import httpx
import fitz  # PyMuPDF
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

# ── 常量 ──────────────────────────────────────────────────────
MAX_CHUNK = 4900          # Google 免费翻译单次上限约 5000 字符
DOWNLOAD_TIMEOUT = 60     # 下载 PDF 超时（秒）
RETRY_WAIT = 2            # 翻译失败后重试等待（秒）
MAX_RETRIES = 3           # 每段最大重试次数


def download_pdf(url: str, dest: Path) -> bool:
    """下载 PDF 到本地路径，成功返回 True"""
    if dest.exists() and dest.stat().st_size > 1000:
        logger.info(f"  ↳ PDF 已缓存: {dest.name}")
        return True
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/131.0.0.0 Safari/537.36"
        }
        with httpx.Client(timeout=DOWNLOAD_TIMEOUT, follow_redirects=True) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            dest.write_bytes(resp.content)
        logger.info(f"  ↳ 下载完成: {dest.name} ({len(resp.content) / 1024:.0f} KB)")
        return True
    except Exception as e:
        logger.warning(f"  ✗ 下载失败 {url}: {e}")
        return False


def extract_text_by_page(pdf_path: Path) -> list[str]:
    """使用 PyMuPDF 提取 PDF 每页的文本内容"""
    pages = []
    try:
        doc = fitz.open(str(pdf_path))
        for page in doc:
            text = page.get_text("text")
            if text.strip():
                pages.append(text.strip())
        doc.close()
    except Exception as e:
        logger.warning(f"  ✗ PDF 解析失败: {e}")
    return pages


def split_text(text: str, max_len: int = MAX_CHUNK) -> list[str]:
    """将长文本按段落边界拆分为不超过 max_len 的块"""
    paragraphs = text.split("\n")
    chunks, current = [], ""
    for para in paragraphs:
        if len(current) + len(para) + 1 > max_len:
            if current:
                chunks.append(current)
            # 单段超长时强制截断
            while len(para) > max_len:
                chunks.append(para[:max_len])
                para = para[max_len:]
            current = para
        else:
            current = current + "\n" + para if current else para
    if current:
        chunks.append(current)
    return chunks


def translate_text(text: str) -> str:
    """使用 Google 免费翻译将英文文本翻译为中文，自动分块"""
    if not text.strip():
        return ""
    translator = GoogleTranslator(source="en", target="zh-CN")
    chunks = split_text(text)
    translated_parts = []
    for i, chunk in enumerate(chunks):
        for attempt in range(MAX_RETRIES):
            try:
                result = translator.translate(chunk)
                translated_parts.append(result or "")
                break
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_WAIT * (attempt + 1))
                else:
                    logger.warning(f"    ✗ 翻译块 {i+1}/{len(chunks)} 失败: {e}")
                    translated_parts.append(f"[翻译失败] {chunk[:200]}...")
        # 友好限速：每块之间间隔一丢丢
        time.sleep(0.5)
    return "\n".join(translated_parts)
