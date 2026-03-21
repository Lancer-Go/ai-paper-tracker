# storage/db.py — SQLite 数据库操作

import json
import sqlite3
import logging
from datetime import date, datetime
from contextlib import contextmanager
from pathlib import Path

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import DB_PATH

logger = logging.getLogger(__name__)

# 确保数据目录存在
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_conn():
    """SQLite 连接上下文管理器"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """初始化数据库表结构"""
    with get_conn() as conn:
        conn.executescript("""
        -- 论文基本信息表
        CREATE TABLE IF NOT EXISTS papers (
            arxiv_id            TEXT PRIMARY KEY,
            title               TEXT NOT NULL,
            abstract            TEXT,
            authors             TEXT,           -- JSON array
            categories          TEXT,           -- JSON array
            primary_category    TEXT,
            published_date      TEXT,           -- YYYY-MM-DD
            arxiv_url           TEXT,
            pdf_url             TEXT,
            ss_paper_id         TEXT,
            first_seen_date     TEXT,           -- 首次入库日期
            updated_at          TEXT
        );

        -- 每日引用量快照表（用于计算增量）
        CREATE TABLE IF NOT EXISTS citation_snapshots (
            arxiv_id        TEXT NOT NULL,
            snapshot_date   TEXT NOT NULL,      -- YYYY-MM-DD
            citation_count  INTEGER DEFAULT 0,
            influential_citation_count INTEGER DEFAULT 0,
            PRIMARY KEY (arxiv_id, snapshot_date)
        );

        -- 每日热度排行榜
        CREATE TABLE IF NOT EXISTS daily_rankings (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            rank_date       TEXT NOT NULL,      -- YYYY-MM-DD
            arxiv_id        TEXT NOT NULL,
            rank            INTEGER NOT NULL,
            score           REAL NOT NULL,
            citation_count  INTEGER,
            citation_delta_7d INTEGER,
            reddit_score    INTEGER,
            score_breakdown TEXT,               -- JSON
            UNIQUE (rank_date, arxiv_id)
        );

        -- 抓取日志表
        CREATE TABLE IF NOT EXISTS fetch_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            run_date    TEXT NOT NULL,
            status      TEXT NOT NULL,          -- success / partial / failed
            papers_fetched INTEGER DEFAULT 0,
            papers_scored  INTEGER DEFAULT 0,
            error_msg   TEXT,
            created_at  TEXT NOT NULL
        );
        """)
    logger.info(f"[DB] 数据库已初始化: {DB_PATH}")


def upsert_papers(papers: list[dict]):
    """批量写入/更新论文基本信息"""
    today = date.today().isoformat()
    now = datetime.now().isoformat()

    with get_conn() as conn:
        for p in papers:
            conn.execute("""
                INSERT INTO papers
                    (arxiv_id, title, abstract, authors, categories, primary_category,
                     published_date, arxiv_url, pdf_url, ss_paper_id, first_seen_date, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(arxiv_id) DO UPDATE SET
                    title = excluded.title,
                    abstract = excluded.abstract,
                    authors = excluded.authors,
                    ss_paper_id = COALESCE(excluded.ss_paper_id, papers.ss_paper_id),
                    updated_at = excluded.updated_at
            """, (
                p["arxiv_id"],
                p["title"],
                p.get("abstract", ""),
                json.dumps(p.get("authors", []), ensure_ascii=False),
                json.dumps(p.get("categories", []), ensure_ascii=False),
                p.get("primary_category", ""),
                p.get("published_date", ""),
                p.get("arxiv_url", ""),
                p.get("pdf_url", ""),
                p.get("ss_paper_id", ""),
                today,
                now,
            ))
    logger.info(f"[DB] 写入/更新 {len(papers)} 篇论文基本信息")


def save_citation_snapshots(citation_data: dict[str, dict], snapshot_date: str = None):
    """保存引用量快照（每日一次）"""
    snapshot_date = snapshot_date or date.today().isoformat()
    with get_conn() as conn:
        for arxiv_id, data in citation_data.items():
            conn.execute("""
                INSERT INTO citation_snapshots (arxiv_id, snapshot_date, citation_count, influential_citation_count)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(arxiv_id, snapshot_date) DO UPDATE SET
                    citation_count = excluded.citation_count,
                    influential_citation_count = excluded.influential_citation_count
            """, (
                arxiv_id,
                snapshot_date,
                data.get("citation_count", 0),
                data.get("influential_citation_count", 0),
            ))
    logger.info(f"[DB] 保存 {len(citation_data)} 条引用量快照（{snapshot_date}）")


def get_citation_history(arxiv_ids: list[str], days_ago: int = 7) -> dict[str, int]:
    """
    获取 N 天前的引用量快照，用于计算增量。

    Returns:
        dict, key=arxiv_id, value=N天前引用量
    """
    from datetime import timedelta
    target_date = (date.today() - timedelta(days=days_ago)).isoformat()

    with get_conn() as conn:
        placeholders = ",".join("?" * len(arxiv_ids))
        rows = conn.execute(f"""
            SELECT arxiv_id, citation_count
            FROM citation_snapshots
            WHERE arxiv_id IN ({placeholders})
              AND snapshot_date <= ?
            ORDER BY snapshot_date DESC
        """, (*arxiv_ids, target_date)).fetchall()

    # 每个 arxiv_id 取最近一条
    result = {}
    for row in rows:
        if row["arxiv_id"] not in result:
            result[row["arxiv_id"]] = row["citation_count"]
    return result


def save_daily_rankings(scored_papers: list[dict], rank_date: str = None):
    """保存每日热度排行榜"""
    rank_date = rank_date or date.today().isoformat()
    with get_conn() as conn:
        for rank, paper in enumerate(scored_papers, start=1):
            conn.execute("""
                INSERT INTO daily_rankings
                    (rank_date, arxiv_id, rank, score, citation_count, citation_delta_7d, reddit_score, score_breakdown)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(rank_date, arxiv_id) DO UPDATE SET
                    rank = excluded.rank,
                    score = excluded.score,
                    citation_count = excluded.citation_count,
                    citation_delta_7d = excluded.citation_delta_7d,
                    reddit_score = excluded.reddit_score,
                    score_breakdown = excluded.score_breakdown
            """, (
                rank_date,
                paper["arxiv_id"],
                rank,
                paper["score"],
                paper.get("citation_count", 0),
                paper.get("citation_delta_7d", 0),
                paper.get("reddit_score", 0),
                json.dumps(paper.get("score_breakdown", {})),
            ))
    logger.info(f"[DB] 保存 {len(scored_papers)} 条排行（{rank_date}）")


def get_top_papers(rank_date: str = None, limit: int = 50) -> list[dict]:
    """
    查询某天热榜 Top N 论文（附带论文详情）。

    Returns:
        论文列表，按 rank 升序
    """
    rank_date = rank_date or date.today().isoformat()
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT
                dr.rank,
                dr.score,
                dr.citation_count,
                dr.citation_delta_7d,
                dr.reddit_score,
                dr.score_breakdown,
                p.arxiv_id,
                p.title,
                p.abstract,
                p.authors,
                p.categories,
                p.primary_category,
                p.published_date,
                p.arxiv_url,
                p.pdf_url
            FROM daily_rankings dr
            JOIN papers p ON dr.arxiv_id = p.arxiv_id
            WHERE dr.rank_date = ?
            ORDER BY dr.rank ASC
            LIMIT ?
        """, (rank_date, limit)).fetchall()

    result = []
    for row in rows:
        d = dict(row)
        d["authors"] = json.loads(d["authors"] or "[]")
        d["categories"] = json.loads(d["categories"] or "[]")
        d["score_breakdown"] = json.loads(d["score_breakdown"] or "{}")
        result.append(d)
    return result


def log_run(status: str, papers_fetched: int = 0, papers_scored: int = 0, error_msg: str = ""):
    """记录一次运行日志"""
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO fetch_logs (run_date, status, papers_fetched, papers_scored, error_msg, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            date.today().isoformat(),
            status,
            papers_fetched,
            papers_scored,
            error_msg,
            datetime.now().isoformat(),
        ))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    init_db()
    print("数据库初始化成功")
    papers = get_top_papers(limit=5)
    print(f"今日热榜: {len(papers)} 篇")
    for p in papers:
        print(f"  #{p['rank']} [{p['arxiv_id']}] score={p['score']:.2f} | {p['title'][:60]}")
