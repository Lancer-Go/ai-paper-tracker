"""
translate_papers.py — 论文翻译入口（薄壳）
调用 src/processing/translator.py + src/export/html_exporter.py

支持两种模式：
  1. arXiv HTML 保真翻译（优先） — 保留图片/公式/表格
  2. PDF 纯文本降级翻译（兜底） — 旧逻辑

支持多进程并发翻译，大幅缩短总耗时。

用法：
    python translate_papers.py                  # 翻译 latest.json 中全部 50 篇
    python translate_papers.py --top-n 5        # 只翻译 Top 5
    python translate_papers.py --workers 4      # 4 个并发 worker（默认）
    python translate_papers.py --workers 1      # 串行模式（调试用）
    python translate_papers.py --input data/exports/daily_2026-03-21.json
"""

import argparse
import json
import logging
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from src.processing.translator import (
    fetch_arxiv_html,
    translate_html,
    download_pdf,
    translate_pdf_as_html,
    extract_text_by_page,
    translate_text,
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


def translate_single_paper(paper: dict, output_dir: str, pdf_cache_dir: str) -> dict:
    """
    翻译单篇论文（独立进程中执行）。

    返回结果字典:
      成功: {"arxiv_id": ..., "ok": True,  "entry": {...}, "type": "html"|"pdf"}
      失败: {"arxiv_id": ..., "ok": False, "error": "..."}
    """
    # 每个子进程需要独立初始化 logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    proc_logger = logging.getLogger(f"worker-{paper.get('arxiv_id', 'unknown')}")

    arxiv_id = paper.get("arxiv_id", "unknown")
    title = paper.get("title", "Unknown")
    pdf_url = paper.get("pdf_url", "")
    safe_id = arxiv_id.replace("/", "_")

    output_path = Path(output_dir)
    pdf_cache = Path(pdf_cache_dir)

    start_time = time.time()

    try:
        # ── 优先尝试 arXiv HTML 保真翻译 ──
        html_content = fetch_arxiv_html(arxiv_id)

        if html_content:
            proc_logger.info(f"  [{arxiv_id}] 使用 arXiv HTML 保真翻译...")
            translated_html = translate_html(html_content, arxiv_id)

            html_file = output_path / f"{safe_id}_html.html"
            html_file.write_text(translated_html, encoding="utf-8")

            elapsed = time.time() - start_time
            proc_logger.info(f"  [{arxiv_id}] ✓ 保真翻译完成 ({elapsed:.1f}s)")

            return {
                "arxiv_id": arxiv_id,
                "ok": True,
                "type": "html",
                "entry": {
                    "file": f"{safe_id}_html.html",
                    "title": title,
                    "pages": 0,
                    "type": "html",
                },
            }
        else:
            # ── PDF 图文保真翻译（新流程） ──
            if not pdf_url:
                proc_logger.warning(f"  [{arxiv_id}] ✗ 无 PDF URL，跳过")
                return {"arxiv_id": arxiv_id, "ok": False, "error": "no_pdf_url"}

            proc_logger.info(f"  [{arxiv_id}] PDF 图文保真翻译...")
            pdf_file = pdf_cache / f"{safe_id}.pdf"

            if not download_pdf(pdf_url, pdf_file):
                return {"arxiv_id": arxiv_id, "ok": False, "error": "pdf_download_failed"}

            # 新流程：PDF → Markdown(含图片) → HTML → translate_html
            translated_html = translate_pdf_as_html(
                pdf_file, arxiv_id, output_path
            )

            if translated_html:
                html_file = output_path / f"{safe_id}_html.html"
                html_file.write_text(translated_html, encoding="utf-8")

                elapsed = time.time() - start_time
                proc_logger.info(f"  [{arxiv_id}] ✓ PDF 图文翻译完成 ({elapsed:.1f}s)")

                return {
                    "arxiv_id": arxiv_id,
                    "ok": True,
                    "type": "html",
                    "entry": {
                        "file": f"{safe_id}_html.html",
                        "title": title,
                        "pages": 0,
                        "type": "html",
                    },
                }
            else:
                # 兜底：旧的纯文本翻译
                proc_logger.warning(f"  [{arxiv_id}] 图文翻译失败，降级纯文本...")
                pages = extract_text_by_page(pdf_file)
                if not pages:
                    return {"arxiv_id": arxiv_id, "ok": False, "error": "pdf_extract_empty"}

                pages_zh = [translate_text(p) for p in pages]
                pdf_out = output_path / f"{safe_id}.html"
                generate_html_pdf_fallback(paper, pages_zh, pdf_out)

                elapsed = time.time() - start_time
                proc_logger.info(f"  [{arxiv_id}] ✓ 纯文本降级翻译完成 ({elapsed:.1f}s)")

                return {
                    "arxiv_id": arxiv_id,
                    "ok": True,
                    "type": "pdf",
                    "entry": {
                        "file": f"{safe_id}.html",
                        "title": title,
                        "pages": len(pages_zh),
                        "type": "pdf",
                    },
                }

    except Exception as e:
        proc_logger.error(f"  [{arxiv_id}] ✗ 翻译异常: {e}")
        return {"arxiv_id": arxiv_id, "ok": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="论文翻译流水线 (HTML 保真 + PDF 降级)")
    parser.add_argument("--input", type=str, default="data/exports/latest.json",
                        help="输入的论文 JSON 文件路径")
    parser.add_argument("--top-n", type=int, default=50,
                        help="翻译排名前 N 篇论文（默认 50）")
    parser.add_argument("--output-dir", type=str, default="data/translations",
                        help="翻译结果输出目录")
    parser.add_argument("--workers", type=int, default=4,
                        help="并发翻译进程数（默认 4，设为 1 则串行）")
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
    logger.info(f"═══ 论文翻译流水线启动 | 共 {len(papers)} 篇 | {args.workers} 并发 ═══")

    # 读取已有索引（增量翻译，跳过已翻译的）
    index_path = output_dir / "index.json"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            index = json.load(f)
    else:
        index = {}

    # ── 过滤已缓存的论文 ──
    pending = []
    skipped = 0
    for paper in papers:
        arxiv_id = paper.get("arxiv_id", "unknown")
        if arxiv_id in index:
            existing_file = output_dir / index[arxiv_id].get("file", "")
            if existing_file.exists():
                skipped += 1
                continue
        pending.append(paper)

    logger.info(f"  ⏭️  跳过已缓存: {skipped} 篇 | 待翻译: {len(pending)} 篇")

    if not pending:
        logger.info("  ✅ 所有论文已翻译，无需处理")
        return

    stats = {"html": 0, "pdf": 0, "skipped": skipped, "failed": 0}
    consecutive_failures = 0
    pipeline_start = time.time()
    completed_count = 0

    # ── 多进程并发翻译 ──
    max_workers = min(args.workers, len(pending))
    logger.info(f"  🚀 启动 {max_workers} 个并发 worker...")

    with ProcessPoolExecutor(max_workers=max_workers) as pool:
        future_to_paper = {}
        submitted = 0

        # 分批提交：先提交一批，然后随完成情况补充提交
        # 这样可以在时间预算耗尽时提前终止
        batch_size = max_workers * 2  # 初始提前量
        submit_end = min(batch_size, len(pending))

        for i in range(submit_end):
            future = pool.submit(
                translate_single_paper,
                pending[i],
                str(output_dir),
                str(pdf_cache),
            )
            future_to_paper[future] = pending[i]
            submitted = i + 1

        for future in as_completed(future_to_paper):
            paper = future_to_paper[future]
            arxiv_id = paper.get("arxiv_id", "unknown")
            title = paper.get("title", "Unknown")
            completed_count += 1

            try:
                result = future.result(timeout=300)  # 单篇最大等待 5 分钟
            except Exception as e:
                logger.error(f"  ✗ [{arxiv_id}] Worker 异常: {e}")
                result = {"arxiv_id": arxiv_id, "ok": False, "error": str(e)}

            if result["ok"]:
                index[result["arxiv_id"]] = result["entry"]
                trans_type = result["type"]
                stats[trans_type] += 1
                consecutive_failures = 0
                logger.info(
                    f"  ✅ [{completed_count}/{len(pending)}] {title[:50]}... → {trans_type}"
                )
            else:
                stats["failed"] += 1
                consecutive_failures += 1
                logger.warning(
                    f"  ❌ [{completed_count}/{len(pending)}] {title[:50]}... → {result.get('error', 'unknown')}"
                )

            # ── 保存中间索引 ──
            with open(index_path, "w", encoding="utf-8") as f:
                json.dump(index, f, ensure_ascii=False, indent=2)

            # ── 熔断检查 ──
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                logger.error(f"⛔ 连续 {MAX_CONSECUTIVE_FAILURES} 篇失败，终止流水线")
                pool.shutdown(wait=False, cancel_futures=True)
                break

            # ── 时间预算检查 ──
            elapsed = time.time() - pipeline_start
            if elapsed > TIME_BUDGET_SECONDS:
                remaining = len(pending) - completed_count
                logger.warning(
                    f"  ⏱ 已用时 {elapsed/60:.1f} 分钟，超出预算，跳过剩余 {remaining} 篇"
                )
                pool.shutdown(wait=False, cancel_futures=True)
                break

            # ── 补充提交新任务 ──
            if submitted < len(pending):
                future = pool.submit(
                    translate_single_paper,
                    pending[submitted],
                    str(output_dir),
                    str(pdf_cache),
                )
                future_to_paper[future] = pending[submitted]
                submitted += 1

    # ── 最终写入索引 ──
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    total_elapsed = time.time() - pipeline_start
    logger.info(f"\n{'═'*50}")
    logger.info(f"✅ 翻译完成！耗时 {total_elapsed/60:.1f} 分钟 | {args.workers} 并发")
    logger.info(f"   🔬 HTML 保真: {stats['html']} 篇")
    logger.info(f"   📝 PDF 降级:  {stats['pdf']} 篇")
    logger.info(f"   ⏭️  已缓存跳过: {stats['skipped']} 篇")
    logger.info(f"   ❌ 失败:      {stats['failed']} 篇")
    logger.info(f"   索引写入: {index_path}")


if __name__ == "__main__":
    main()
