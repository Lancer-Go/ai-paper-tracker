"""
translate.py — 论文翻译入口（薄壳）
调用 src/processing/translator.py + src/export/html_exporter.py

用法：
    python translate.py                  # 翻译 latest.json 中全部 50 篇论文
    python translate.py --top-n 5        # 只翻译 Top 5
    python translate.py --input data/exports/daily_2026-03-21.json
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path

from src.processing.translator import download_pdf, extract_text_by_page, translate_text
from src.export.html_exporter import generate_html

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="论文 PDF 自动翻译流水线")
    parser.add_argument("--input", type=str, default="data/exports/latest.json",
                        help="输入的论文 JSON 文件路径")
    parser.add_argument("--top-n", type=int, default=50,
                        help="翻译排名前 N 篇论文（默认 50，即全部）")
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
