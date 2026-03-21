"""
run.py — 主入口：全流程一键运行
用法：
    python run.py              # 正常运行今日数据
    python run.py --dry-run    # 仅抓取&打印，不写数据库
    python run.py --date 2026-03-20  # 为指定日期运行
"""

import argparse
import logging
import sys
from datetime import date

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("data/run.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="AI 论文热度追踪系统")
    parser.add_argument("--dry-run", action="store_true", help="仅采集&评分，不写数据库")
    parser.add_argument("--date", type=str, default=None, help="指定日期 YYYY-MM-DD，默认今天")
    parser.add_argument("--skip-reddit", action="store_true", help="跳过 Reddit 数据采集")
    parser.add_argument("--days-back", type=int, default=7, help="arXiv 往回看天数，默认 7")
    parser.add_argument("--top-n", type=int, default=100, help="热榜 Top N，默认 100")
    args = parser.parse_args()

    run_date = args.date or date.today().isoformat()
    logger.info(f"═══ AI 论文热度追踪 | 运行日期: {run_date} ═══")

    # ── Step 0: 初始化数据库 ────────────────────────────────
    from storage.db import (
        init_db, upsert_papers, save_citation_snapshots,
        get_citation_history, save_daily_rankings, log_run
    )
    from pathlib import Path
    Path("data/exports").mkdir(parents=True, exist_ok=True)

    if not args.dry_run:
        init_db()

    # ── Step 1: arXiv 抓取 ──────────────────────────────────
    logger.info("【1/5】arXiv 论文抓取")
    from crawler.arxiv_fetcher import fetch_all_categories
    raw_papers = fetch_all_categories(days_back=args.days_back)
    logger.info(f"  → 原始论文: {len(raw_papers)} 篇（含重复）")

    # ── Step 2: 去重 ────────────────────────────────────────
    logger.info("【2/5】去重")
    from processor.deduper import deduplicate
    papers = deduplicate(raw_papers)
    logger.info(f"  → 去重后: {len(papers)} 篇")

    if not papers:
        logger.warning("无有效论文，退出")
        if not args.dry_run:
            log_run("failed", 0, 0, "无有效论文")
        return

    # ── Step 3: OpenAlex 引用量（惰性补充，每次最多 100 篇） ─────
    logger.info("》3/5「OpenAlex 引用量查询（免费无需 Key）")
    arxiv_ids = [p["arxiv_id"] for p in papers]

    # 只查询已入库且从未有过引用量快照的论文（避免重复查）
    import sqlite3 as _sqlite3
    from config import DB_PATH as _DB_PATH
    if not args.dry_run:
        with _sqlite3.connect(_DB_PATH) as _conn:
            existing = {r[0] for r in _conn.execute(
                "SELECT DISTINCT arxiv_id FROM citation_snapshots"
            ).fetchall()}
        ids_to_fetch = [i for i in arxiv_ids if i not in existing][:100]
    else:
        ids_to_fetch = arxiv_ids[:10]  # dry-run 仅测 10 篇

    citation_data = {}
    if ids_to_fetch:
        from crawler.openalex_fetcher import fetch_batch_papers
        logger.info(f"  → 查询 {len(ids_to_fetch)} 篇（新论文查完一次即缓存）")
        new_cit = fetch_batch_papers(ids_to_fetch)
        citation_data.update(new_cit)
        if not args.dry_run and new_cit:
            save_citation_snapshots(new_cit)

    # 读取所有已有快照（包含过去积累的）
    if not args.dry_run:
        with _sqlite3.connect(_DB_PATH) as _conn:
            rows = _conn.execute("""
                SELECT arxiv_id, MAX(citation_count) as citation_count,
                       MAX(influential_citation_count) as influential_citation_count
                FROM citation_snapshots GROUP BY arxiv_id
            """).fetchall()
        for row in rows:
            if row[0] not in citation_data:
                citation_data[row[0]] = {"citation_count": row[1], "influential_citation_count": row[2], "ss_paper_id": ""}

    logger.info(f"  → 引用量数据: {len(citation_data)} 篇")

    # 获取 7 天前历史引用量（用于增量计算）
    citation_history = {}
    if not args.dry_run:
        citation_history = get_citation_history(arxiv_ids, days_ago=7)
        logger.info(f"  → 历史引用量快照: {len(citation_history)} 篇")

    # ── Step 4: Reddit 数据（可选）──────────────────────────
    reddit_data = {}
    if not args.skip_reddit:
        logger.info("【4/5】Reddit 讨论量采集（可选）")
        try:
            from crawler.reddit_fetcher import RedditFetcher
            fetcher = RedditFetcher()
            # 只对 Top 候选论文查 Reddit，节省配额
            candidates = sorted(papers, key=lambda p: citation_data.get(p["arxiv_id"], {}).get("citation_count", 0), reverse=True)[:50]
            reddit_data = fetcher.batch_fetch(candidates)
            logger.info(f"  → Reddit 数据: {sum(1 for v in reddit_data.values() if v > 0)} 篇有讨论")
        except Exception as e:
            logger.info(f"  → Reddit 跳过: {e}")
    else:
        logger.info("【4/5】Reddit 采集已跳过（--skip-reddit）")

    # ── Step 5: 评分 & 排行 ─────────────────────────────────
    logger.info("【5/5】热度评分")
    from processor.scorer import score_papers
    scored = score_papers(papers, citation_data, citation_history, reddit_data)
    top_papers = scored[: args.top_n]

    logger.info(f"\n{'─'*60}")
    logger.info(f"📊 今日 Top 10 热门论文（{run_date}）")
    logger.info(f"{'─'*60}")
    for p in top_papers[:10]:
        logger.info(
            f"  #{p.get('rank', '?'):>2} [{p['arxiv_id']}] score={p['score']:.2f} | 引用增量: +{p.get('citation_delta_7d', 0)}"
        )
        logger.info(f"      {p['title'][:75]}")
    logger.info(f"{'─'*60}")

    if args.dry_run:
        logger.info("[dry-run] 不写数据库，运行完成")
        return

    # ── 写数据库 ────────────────────────────────────────────
    # 给每篇论文补充排名字段
    for i, p in enumerate(top_papers, start=1):
        p["rank"] = i

    upsert_papers(papers)
    save_citation_snapshots(citation_data, snapshot_date=run_date)
    save_daily_rankings(top_papers, rank_date=run_date)

    # ── 导出 JSON ───────────────────────────────────────────
    from api.export import export_daily_json, export_index_json
    export_daily_json(rank_date=run_date, top_n=args.top_n)
    export_index_json()

    log_run("success", papers_fetched=len(papers), papers_scored=len(top_papers))
    logger.info("✅ 全流程完成！")


if __name__ == "__main__":
    main()
