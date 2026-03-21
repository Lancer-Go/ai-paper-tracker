"""
translate_papers.py — 自动下载 Top N 论文 PDF，提取文本并翻译为中文，生成静态 HTML 页面
用法：
    python translate_papers.py                  # 翻译 latest.json 中 Top 10 论文
    python translate_papers.py --top-n 5        # 只翻译 Top 5
    python translate_papers.py --input data/exports/daily_2026-03-21.json
"""

import argparse
import json
import logging
import sys
import time
import re
from pathlib import Path

import httpx
import fitz  # PyMuPDF
from deep_translator import GoogleTranslator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
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


def sanitize_filename(name: str) -> str:
    """清理文件名中的非法字符"""
    return re.sub(r'[<>:"/\\|?*]', '_', name)[:80]


def generate_html(paper: dict, pages_zh: list[str], output_path: Path):
    """生成一份精美的翻译后 HTML 文件"""
    title = paper.get("title", "未知标题")
    arxiv_id = paper.get("arxiv_id", "")
    authors = ", ".join(paper.get("authors", []))
    categories = ", ".join(paper.get("categories", []))
    pdf_url = paper.get("pdf_url", "")
    arxiv_url = paper.get("arxiv_url", "")

    pages_html = ""
    for i, page_text in enumerate(pages_zh, 1):
        # 将换行转为 <br> 以保持段落结构
        formatted = page_text.replace("\n\n", "</p><p>").replace("\n", "<br>")
        pages_html += f"""
        <div class="page">
            <div class="page-header">第 {i} 页 / 共 {len(pages_zh)} 页</div>
            <div class="page-content"><p>{formatted}</p></div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 中文翻译</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
                         'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #0f0c29 0%, #1a1a3e 50%, #24243e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 0;
        }}
        .header {{
            background: rgba(255,255,255,0.04);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(255,255,255,0.08);
            padding: 32px 40px;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .header h1 {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #fff;
            margin-bottom: 12px;
            line-height: 1.4;
        }}
        .meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            font-size: 0.82rem;
            color: #8892b0;
        }}
        .meta a {{
            color: #64ffda;
            text-decoration: none;
        }}
        .meta a:hover {{ text-decoration: underline; }}
        .badge {{
            display: inline-block;
            background: rgba(99, 102, 241, 0.2);
            color: #a5b4fc;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            margin-right: 4px;
        }}
        .nav-bar {{
            display: flex;
            gap: 10px;
            margin-top: 14px;
        }}
        .nav-bar a {{
            padding: 6px 16px;
            border-radius: 8px;
            font-size: 0.8rem;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.2s;
        }}
        .btn-primary {{
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: #fff;
        }}
        .btn-secondary {{
            background: rgba(255,255,255,0.06);
            color: #a5b4fc;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .btn-secondary:hover {{ background: rgba(255,255,255,0.12); }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 32px 20px; }}
        .page {{
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 16px;
            margin-bottom: 24px;
            overflow: hidden;
            transition: transform 0.2s;
        }}
        .page:hover {{ transform: translateY(-2px); }}
        .page-header {{
            background: rgba(99, 102, 241, 0.1);
            padding: 10px 24px;
            font-size: 0.78rem;
            color: #8892b0;
            font-weight: 600;
            letter-spacing: 0.05em;
        }}
        .page-content {{
            padding: 24px;
            font-size: 0.95rem;
            line-height: 1.85;
            color: #cbd5e1;
        }}
        .page-content p {{ margin-bottom: 14px; }}
        .footer {{
            text-align: center;
            padding: 40px;
            color: #4a5568;
            font-size: 0.78rem;
        }}
        .footer a {{ color: #64ffda; text-decoration: none; }}

        @media (max-width: 640px) {{
            .header {{ padding: 20px 16px; }}
            .header h1 {{ font-size: 1.15rem; }}
            .container {{ padding: 16px 10px; }}
            .page-content {{ padding: 16px; font-size: 0.88rem; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📄 {title}</h1>
        <div class="meta">
            <span>👤 {authors}</span>
            <span>🏷️ {categories}</span>
            <span>📋 arXiv: <a href="{arxiv_url}" target="_blank">{arxiv_id}</a></span>
        </div>
        <div class="nav-bar">
            <a class="btn-primary" href="{pdf_url}" target="_blank">📥 原版 PDF</a>
            <a class="btn-secondary" href="{arxiv_url}" target="_blank">🔗 arXiv 页面</a>
            <a class="btn-secondary" href="javascript:history.back()">← 返回热榜</a>
        </div>
    </div>
    <div class="container">
        {pages_html}
    </div>
    <div class="footer">
        由 <a href="https://github.com/Lancer-Go/ai-paper-tracker">AI 论文热榜</a> 自动翻译生成<br>
        翻译引擎：Google Translate | 仅供学术参考
    </div>
</body>
</html>"""

    output_path.write_text(html, encoding="utf-8")
    logger.info(f"  ✓ HTML 生成完成: {output_path.name}")


def main():
    parser = argparse.ArgumentParser(description="论文 PDF 自动翻译流水线")
    parser.add_argument("--input", type=str, default="data/exports/latest.json",
                        help="输入的论文 JSON 文件路径")
    parser.add_argument("--top-n", type=int, default=10,
                        help="翻译排名前 N 篇论文（默认 10）")
    parser.add_argument("--output-dir", type=str, default="data/translations",
                        help="翻译结果输出目录")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"输入文件不存在: {input_path}")
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_cache = Path("data/pdf_cache")
    pdf_cache.mkdir(parents=True, exist_ok=True)

    # 读取论文数据
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    papers = data.get("papers", [])[:args.top_n]
    logger.info(f"═══ 论文翻译流水线启动 | 共 {len(papers)} 篇 ═══")

    # 生成索引文件（前端用来判断哪些论文有翻译）
    index = {}

    for i, paper in enumerate(papers, 1):
        arxiv_id = paper.get("arxiv_id", "unknown")
        title = paper.get("title", "Unknown")
        pdf_url = paper.get("pdf_url", "")

        logger.info(f"\n【{i}/{len(papers)}】{title[:60]}...")

        if not pdf_url:
            logger.warning("  ✗ 无 PDF URL，跳过")
            continue

        # 1. 下载 PDF
        pdf_file = pdf_cache / f"{arxiv_id.replace('/', '_')}.pdf"
        if not download_pdf(pdf_url, pdf_file):
            continue

        # 2. 提取文本
        pages = extract_text_by_page(pdf_file)
        if not pages:
            logger.warning("  ✗ 无法提取文本，跳过")
            continue
        logger.info(f"  → 提取到 {len(pages)} 页文本")

        # 3. 逐页翻译
        pages_zh = []
        for pi, page_text in enumerate(pages, 1):
            logger.info(f"  → 翻译第 {pi}/{len(pages)} 页...")
            zh = translate_text(page_text)
            pages_zh.append(zh)

        # 4. 生成 HTML
        html_filename = f"{arxiv_id.replace('/', '_')}.html"
        html_path = output_dir / html_filename
        generate_html(paper, pages_zh, html_path)

        index[arxiv_id] = {
            "file": html_filename,
            "title": title,
            "pages": len(pages_zh),
        }

        # 礼貌延迟，避免被 Google 限流
        time.sleep(1)

    # 5. 写入索引
    index_path = output_dir / "index.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    logger.info(f"\n✅ 翻译完成！共处理 {len(index)} 篇论文，索引写入 {index_path}")


if __name__ == "__main__":
    main()
