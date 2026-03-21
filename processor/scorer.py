# processor/scorer.py — 热度评分计算
#
# 评分维度（适用于新旧论文）：
#   1. 引用增量（7天）  — 核心学术热度，对老论文有效
#   2. 引用总量（对数）  — 累积学术影响力，对老论文有效
#   3. 新鲜度            — 越新发布越靠前，专门保护新论文
#   4. 参考文献数（对数）— 越完整的研究引用越多文献
#   5. 跨领域宽度        — 出现在越多 arXiv 类别，越可能跨学科影响
#   6. Reddit 讨论量（可选）— 社区关注度
#
# 权重设计原则：
#   - 对于零引用的新论文，维度 3/4/5 保证它们仍能区分排序
#   - 对于有引用的老论文，维度 1/2 主导排序

import math
import logging
from typing import Optional

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import SCORE_WEIGHTS

logger = logging.getLogger(__name__)


def _min_max_normalize(values: list[float]) -> list[float]:
    """将一组值 Min-Max 归一化到 [0, 100]"""
    if not values:
        return []
    min_v = min(values)
    max_v = max(values)
    if max_v == min_v:
        return [50.0] * len(values)  # 全部相同，统一给 50
    return [(v - min_v) / (max_v - min_v) * 100 for v in values]


def _safe_log(x: float) -> float:
    """安全对数，防止 log(0)"""
    return math.log(x + 1)


def calculate_citation_delta(
    current_count: int,
    previous_count: Optional[int],
) -> int:
    """
    计算引用增量。若无历史数据，以当前引用量的 10% 估算（保守估计）。
    """
    if previous_count is None:
        return max(0, int(current_count * 0.10))
    return max(0, current_count - previous_count)


def _freshness_score(published_date: str, max_days: int = 60) -> float:
    """
    论文新鲜度分：越新发布越高（0~100）。
    30 天内的论文得满分区间，60 天后线性衰减。
    """
    try:
        from datetime import date
        pub = date.fromisoformat(published_date)
        days_old = (date.today() - pub).days
        if days_old <= 3:
            return 100.0
        elif days_old <= max_days:
            return max(0.0, (max_days - days_old) / max_days * 100)
        else:
            return 0.0
    except Exception:
        return 50.0


def _breadth_score(categories: list[str]) -> float:
    """
    跨领域宽度：出现在越多 arXiv 类别，跨学科影响越广。
    1 个类别 → 0，5+ 个类别 → 100
    """
    n = len(categories) if categories else 1
    return min(100.0, (n - 1) / 4.0 * 100)


def score_papers(
    papers: list[dict],
    citation_data: dict[str, dict],
    citation_history: dict[str, int],  # arxiv_id → 7天前的引用量
    reddit_data: Optional[dict[str, int]] = None,
) -> list[dict]:
    """
    对论文列表计算热度得分并排序。

    Args:
        papers: 论文列表（已去重）
        citation_data: 引用量数据（来自 OpenAlex），key=arxiv_id
        citation_history: 7天前的引用量快照，key=arxiv_id
        reddit_data: Reddit 讨论量，key=arxiv_id（可选）

    Returns:
        论文列表，附加 score 字段，按 score 降序排列
    """
    if not papers:
        return []

    reddit_data = reddit_data or {}

    # ── Step 1: 为每篇论文计算原始各维度值 ──────────────────
    raw_deltas    = []
    raw_totals    = []
    raw_reddits   = []
    raw_freshness = []
    raw_refs      = []   # 参考文献数（对数）
    raw_breadth   = []   # 跨领域宽度

    for paper in papers:
        arxiv_id = paper["arxiv_id"]
        ss = citation_data.get(arxiv_id, {})

        current_count = ss.get("citation_count", 0)
        previous_count = citation_history.get(arxiv_id)
        delta = calculate_citation_delta(current_count, previous_count)

        raw_deltas.append(delta)
        raw_totals.append(_safe_log(current_count))
        raw_reddits.append(float(reddit_data.get(arxiv_id, 0)))
        raw_freshness.append(_freshness_score(paper.get("published_date", "")))
        raw_refs.append(_safe_log(ss.get("reference_count", 0)))
        raw_breadth.append(_breadth_score(paper.get("categories", [])))

    # ── Step 2: 归一化 ──────────────────────────────────────
    norm_deltas    = _min_max_normalize(raw_deltas)
    norm_totals    = _min_max_normalize(raw_totals)
    norm_reddits   = _min_max_normalize(raw_reddits)
    norm_freshness = raw_freshness            # 已在 [0,100]
    norm_refs      = _min_max_normalize(raw_refs)
    norm_breadth   = raw_breadth              # 已在 [0,100]

    # ── 权重配置 ────────────────────────────────────────────
    # 总和 = 100
    # 对新论文：freshness(20) + refs(10) + breadth(5) 合计 35 分有效
    # 对老论文：citation_delta(35) + citation_total(25) 主导
    W = {
        "citation_delta":  35,  # 引用增量（近 7 天）
        "citation_total":  25,  # 累积引用（对数）
        "reddit":          10,  # 社区讨论
        "freshness":       20,  # 新鲜度（新论文的主要得分来源）
        "refs":            5,   # 参考文献数（论文完整性）
        "breadth":         5,   # 跨领域宽度
    }

    # ── Step 3: 加权求和 ────────────────────────────────────
    results = []
    for i, paper in enumerate(papers):
        arxiv_id = paper["arxiv_id"]
        ss = citation_data.get(arxiv_id, {})

        score = (
            norm_deltas[i]    * W["citation_delta"] / 100
            + norm_totals[i]  * W["citation_total"] / 100
            + norm_reddits[i] * W["reddit"]         / 100
            + norm_freshness[i] * W["freshness"]    / 100
            + norm_refs[i]    * W["refs"]            / 100
            + norm_breadth[i] * W["breadth"]         / 100
        )

        enriched = {
            **paper,
            "citation_count": ss.get("citation_count", 0),
            "influential_citation_count": ss.get("influential_citation_count", 0),
            "citation_delta_7d": raw_deltas[i],
            "reddit_score": int(raw_reddits[i]),
            "ss_paper_id": ss.get("ss_paper_id", ""),
            "score": round(score, 4),
            "score_breakdown": {
                "citation_delta_norm": round(norm_deltas[i], 2),
                "citation_total_norm": round(norm_totals[i], 2),
                "reddit_norm": round(norm_reddits[i], 2),
                "freshness_norm": round(norm_freshness[i], 2),
                "refs_norm": round(norm_refs[i], 2),
                "breadth_norm": round(norm_breadth[i], 2),
            }
        }
        results.append(enriched)

    # 按 score 降序
    results.sort(key=lambda x: x["score"], reverse=True)
    logger.info(f"[评分] 完成 {len(results)} 篇论文评分")

    if results:
        top = results[0]
        logger.info(
            f"[评分] Top 1: [{top['arxiv_id']}] score={top['score']:.2f} "
            f"| 引用={top['citation_count']} | 新鲜度={top['score_breakdown']['freshness_norm']:.0f}"
            f" | {top['title'][:55]}"
        )

    return results


if __name__ == "__main__":
    # 简单测试
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    test_papers = [
        {
            "arxiv_id": "2501.00001", "title": "New Paper (no citations)",
            "abstract": "", "authors": [], "categories": ["cs.AI", "cs.LG"],
            "primary_category": "cs.AI", "published_date": "2026-03-20",
            "arxiv_url": "", "pdf_url": ""
        },
        {
            "arxiv_id": "2501.00002", "title": "Established Paper (many citations)",
            "abstract": "", "authors": [], "categories": ["cs.LG"],
            "primary_category": "cs.LG", "published_date": "2025-10-01",
            "arxiv_url": "", "pdf_url": ""
        },
    ]
    citation_data = {
        "2501.00001": {"citation_count": 0, "influential_citation_count": 0,
                        "reference_count": 45, "ss_paper_id": ""},
        "2501.00002": {"citation_count": 200, "influential_citation_count": 40,
                        "reference_count": 60, "ss_paper_id": "def"},
    }
    citation_history = {"2501.00001": 0, "2501.00002": 150}
    results = score_papers(test_papers, citation_data, citation_history)
    for r in results:
        print(f"[{r['arxiv_id']}] score={r['score']:.4f} | 引用={r['citation_count']} | 新鲜={r['score_breakdown']['freshness_norm']:.0f} | {r['title']}")
