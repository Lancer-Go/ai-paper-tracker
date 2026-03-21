"""
src/export/html_exporter.py — 生成翻译后的 HTML 页面

提供两种导出模式：
  1. HTML 保真模式：由 translator.py 直接输出（inject_theme_and_nav 已内嵌）
  2. PDF 降级模式：generate_html_pdf_fallback() — 从纯文本生成带降级警告的 HTML
"""

import re
import logging
from pathlib import Path

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def sanitize_filename(name: str) -> str:
    """清理文件名中的非法字符"""
    return re.sub(r'[<>:"/\\|?*]', '_', name)[:80]


def generate_html_pdf_fallback(paper: dict, pages_zh: list[str], output_path: Path):
    """
    PDF 降级模式：生成一份带降级警告的翻译 HTML 文件。
    使用白底学术主题，与 HTML 保真版保持视觉一致。
    """
    title = paper.get("title", "未知标题")
    arxiv_id = paper.get("arxiv_id", "")
    authors = ", ".join(paper.get("authors", []))
    categories = ", ".join(paper.get("categories", []))
    pdf_url = paper.get("pdf_url", "")
    arxiv_url = paper.get("arxiv_url", f"https://arxiv.org/abs/{arxiv_id}")

    pages_html = ""
    for i, page_text in enumerate(pages_zh, 1):
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
    <title>{title} - 中文翻译（简版）</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Georgia', 'Times New Roman', 'SimSun', serif;
            background: #ffffff;
            color: #333333;
            min-height: 100vh;
            padding-top: 56px;
            line-height: 1.8;
        }}
        
        /* 导航栏 - 与保真版一致 */
        #ai-tracker-nav {{
            position: fixed;
            top: 0; left: 0; right: 0;
            height: 48px;
            background: #1a1a2e;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px;
            z-index: 99999;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }}
        #ai-tracker-nav a {{
            color: #e0e0e0;
            text-decoration: none;
            font-size: 13px;
            padding: 6px 14px;
            border-radius: 6px;
            transition: background 0.2s;
        }}
        #ai-tracker-nav a:hover {{ background: rgba(255,255,255,0.1); }}
        #ai-tracker-nav .nav-left {{ display: flex; align-items: center; gap: 8px; }}
        #ai-tracker-nav .nav-right {{ display: flex; align-items: center; gap: 6px; }}
        
        /* 降级警告 */
        .degraded-alert {{
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffc107;
            border-radius: 8px;
            padding: 12px 20px;
            margin: 16px 20px;
            font-size: 14px;
            line-height: 1.5;
        }}
        .degraded-alert a {{ color: #0d6efd; }}
        
        /* 论文头部 */
        .header {{
            padding: 32px 40px;
            border-bottom: 1px solid #eee;
        }}
        .header h1 {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 12px;
            line-height: 1.4;
        }}
        .meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            font-size: 0.82rem;
            color: #666;
        }}
        .meta a {{ color: #6366f1; text-decoration: none; }}
        .meta a:hover {{ text-decoration: underline; }}
        .badge {{
            display: inline-block;
            background: #f0f0ff;
            color: #6366f1;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
        }}
        
        .container {{ max-width: 900px; margin: 0 auto; padding: 32px 20px; }}
        .page {{
            background: #fafafa;
            border: 1px solid #eee;
            border-radius: 12px;
            margin-bottom: 24px;
            overflow: hidden;
        }}
        .page-header {{
            background: #f5f5ff;
            padding: 10px 24px;
            font-size: 0.78rem;
            color: #888;
            font-weight: 600;
        }}
        .page-content {{
            padding: 24px;
            font-size: 0.95rem;
            line-height: 1.85;
            color: #444;
        }}
        .page-content p {{ margin-bottom: 14px; }}
        .footer {{
            text-align: center;
            padding: 40px;
            color: #aaa;
            font-size: 0.78rem;
        }}
        .footer a {{ color: #6366f1; text-decoration: none; }}

        @media (max-width: 640px) {{
            .header {{ padding: 20px 16px; }}
            .header h1 {{ font-size: 1.15rem; }}
            .container {{ padding: 16px 10px; }}
        }}
    </style>
</head>
<body>
    <div id="ai-tracker-nav">
        <div class="nav-left">
            <a href="javascript:history.back()">← 返回热榜</a>
        </div>
        <div class="nav-right">
            <a href="{arxiv_url}" target="_blank">🔗 arXiv 原文</a>
            <a href="{pdf_url}" target="_blank">📥 PDF 下载</a>
        </div>
    </div>
    
    <div class="degraded-alert">
        ⚠️ <strong>注</strong>：本文无 arXiv 原生 HTML 版本，当前为基于 PDF 提取的纯文本翻译版，
        可能会丢失部分图表和排版。建议查看 <a href="{pdf_url}" target="_blank">原版 PDF</a> 获取完整内容。
    </div>
    
    <div class="header">
        <h1>📄 {title}</h1>
        <div class="meta">
            <span>👤 {authors}</span>
            <span class="badge">🏷️ {categories}</span>
            <span>📋 arXiv: <a href="{arxiv_url}" target="_blank">{arxiv_id}</a></span>
        </div>
    </div>
    <div class="container">
        {pages_html}
    </div>
    <div class="footer">
        由 <a href="https://github.com/Lancer-Go/ai-paper-tracker">AI 论文热榜</a> 自动翻译生成<br>
        翻译引擎：Google Translate | 仅供学术参考 | <strong>简版翻译（PDF 降级）</strong>
    </div>
</body>
</html>"""

    output_path.write_text(html, encoding="utf-8")
    logger.info(f"  ✓ PDF 降级 HTML 生成完成: {output_path.name}")
