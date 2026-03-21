"""
translate_papers.py — 论文翻译入口（薄壳）
调用 src/processing/translator.py + src/export/html_exporter.py

支持两种模式：
  1. arXiv HTML 保真翻译（优先） — 保留图片/公式/表格
  2. PDF 纯文本降级翻译（兜底） — 旧逻辑

用法：
    python translate_papers.py                  # 翻译 latest.json 中全部 50 篇
    python translate_papers.py --top-n 5        # 只翻译 Top 5
    python translate_papers.py --input data/exports/daily_2026-03-21.json
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path

from src.processing.translator import (
    fetch_arxiv_html,
    translate_html,
    download_pdf,
    extract_text_by_page,
    translate_text,
    inject_degraded_alert,
)
from src.export.html_exporter import generate_html_pdf_fallback

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# 连续失败上限，超过后终止流水线
MAX_CONSECUTIVE_FAILURES = 5
# 全局时间预算（秒）：45 分钟，留 15 分钟给后续步骤（build/deploy/commit）
TIME_BUDGET_SECONDS = 45 * 60


def main():
    parser = argparse.ArgumentParser(description="论文翻译流水线 (HTML 保真 + PDF 降级)")
    parser.add_argument("--input", type=str, default="data/exports/latest.json",
                        help="输入的论文 JSON 文件路径")
    parser.add_argument("--top-n", type=int, default=50,
                        help="翻译排名前 N 篇论文（默认 50）")
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

    # 读取已有索引（增量翻译，跳过已翻译的）
    index_path = output_dir / "index.json"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            index = json.load(f)
    else:
        index = {}

    consecutive_failures = 0
    stats = {"html": 0, "pdf": 0, "skipped": 0, "failed": 0}
    pipeline_start = time.time()

    for i, paper in enumerate(papers, 1):
        arxiv_id = paper.get("arxiv_id", "unknown")
        title = paper.get("title", "Unknown")
        pdf_url = paper.get("pdf_url", "")
        safe_id = arxiv_id.replace("/", "_")

        logger.info(f"\n【{i}/{len(papers)}】{title[:60]}...")

        # ── 时间预算检查 ──
        elapsed = time.time() - pipeline_start
        if elapsed > TIME_BUDGET_SECONDS:
            remaining = len(papers) - i + 1
            logger.warning(f"  ⏱ 已用时 {elapsed/60:.1f} 分钟，超出 {TIME_BUDGET_SECONDS//60} 分钟预算，跳过剩余 {remaining} 篇")
            break

        # ── 缓存检查：已翻译则跳过 ──
        html_cache_file = output_dir / f"{safe_id}_html.html"
        pdf_cache_file = output_dir / f"{safe_id}.html"
        
        if arxiv_id in index:
            existing_type = index[arxiv_id].get("type", "pdf")
            existing_file = output_dir / index[arxiv_id].get("file", "")
            if existing_file.exists():
                logger.info(f"  ↳ 已有 {existing_type} 翻译缓存，跳过")
                stats["skipped"] += 1
                continue

        start_time = time.time()

        # ── 优先尝试 arXiv HTML 保真翻译 ──
        try:
            html_content = fetch_arxiv_html(arxiv_id)
            
            if html_content:
                # HTML 保真翻译
                logger.info(f"  → 使用 arXiv HTML 保真翻译...")
                translated_html = translate_html(html_content, arxiv_id)
                
                html_cache_file.write_text(translated_html, encoding="utf-8")
                
                elapsed = time.time() - start_time
                logger.info(f"  ✓ 保真翻译完成: {html_cache_file.name} ({elapsed:.1f}s)")
                
                index[arxiv_id] = {
                    "file": f"{safe_id}_html.html",
                    "title": title,
                    "pages": 0,
                    "type": "html",
                }
                stats["html"] += 1
                consecutive_failures = 0
                
            else:
                # ── PDF 降级翻译 ──
                if not pdf_url:
                    logger.warning("  ✗ 无 PDF URL，跳过")
                    stats["failed"] += 1
                    consecutive_failures += 1
                    continue
                
                logger.info(f"  → 降级到 PDF 翻译...")
                pdf_file = pdf_cache / f"{safe_id}.pdf"
                
                if not download_pdf(pdf_url, pdf_file):
                    stats["failed"] += 1
                    consecutive_failures += 1
                    continue

                pages = extract_text_by_page(pdf_file)
                if not pages:
                    logger.warning("  ✗ 无法提取文本，跳过")
                    stats["failed"] += 1
                    consecutive_failures += 1
                    continue
                    
                logger.info(f"  → 提取到 {len(pages)} 页文本")

                # 逐页翻译
                pages_zh = []
                for pi, page_text in enumerate(pages, 1):
                    logger.info(f"  → 翻译第 {pi}/{len(pages)} 页...")
                    zh = translate_text(page_text)
                    pages_zh.append(zh)

                # 生成 HTML（带降级 Alert）
                generate_html_pdf_fallback(paper, pages_zh, pdf_cache_file)
                
                elapsed = time.time() - start_time
                logger.info(f"  ✓ PDF 降级翻译完成: {pdf_cache_file.name} ({elapsed:.1f}s)")
                
                index[arxiv_id] = {
                    "file": f"{safe_id}.html",
                    "title": title,
                    "pages": len(pages_zh),
                    "type": "pdf",
                }
                stats["pdf"] += 1
                consecutive_failures = 0
                
        except Exception as e:
            logger.error(f"  ✗ 翻译异常: {e}")
            stats["failed"] += 1
            consecutive_failures += 1
        
        # ── 连续失败熔断 ──
        if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
            logger.error(f"⛔ 连续 {MAX_CONSECUTIVE_FAILURES} 篇失败，终止流水线")
            break
        
        # 保存中间索引 （防止中途崩溃丢失进度）
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        
        # 礼貌延迟
        time.sleep(1)

    # ── 最终写入索引 ──
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    logger.info(f"\n{'═'*50}")
    logger.info(f"✅ 翻译完成！统计:")
    logger.info(f"   🔬 HTML 保真: {stats['html']} 篇")
    logger.info(f"   📝 PDF 降级:  {stats['pdf']} 篇")
    logger.info(f"   ⏭️  已缓存跳过: {stats['skipped']} 篇")
    logger.info(f"   ❌ 失败:      {stats['failed']} 篇")
    logger.info(f"   索引写入: {index_path}")


if __name__ == "__main__":
    main()
