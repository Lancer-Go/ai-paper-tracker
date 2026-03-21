"""
src/export/html_exporter.py — 生成翻译后的 HTML 页面

提取自 translate_papers.py，负责将翻译后的文本渲染为精美 HTML。
"""

import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


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
