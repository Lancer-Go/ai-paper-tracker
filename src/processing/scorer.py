# src/processing/scorer.py — 8 维度热度评分计算
#
# 评分维度：
#   1. Citation Velocity  (25%) — 引用速度 = 增量 ÷ 论文年龄天数
#   2. Citation Mass      (15%) — 引用总量（对数）
#   3. Author Influence   (10%) — 作者最高 h-index（对数）
#   4. Code Available      (5%) — 有无开源代码（0/100）
#   5. GitHub Stars       (15%) — 代码仓库星标数（对数）
#   6. Freshness          (15%) — 发布新鲜度（指数衰减）
#   7. Social Buzz        (15%) — 社区讨论热度（HN points + comments）
#
# 权重设计：
#   - 学术影响力 50% = velocity(25) + mass(15) + author(10)
#   - 工程影响力 20% = code(5) + stars(15)
#   - 时效与关注 30% = freshness(15) + social(15)

import math
import logging
from typing import Optional
from datetime import date

from src.config import SCORE_WEIGHTS

logger = logging.getLogger(__name__)


def _min_max_normalize(values: list[float]) -> list[float]:
    """将一组值 Min-Max 归一化到 [0, 100]"""
    if not values:
        return []
    min_v = min(values)
    max_v = max(values)
    if max_v == min_v:
        return [50.0] * len(values)
    return [(v - min_v) / (max_v - min_v) * 100 for v in values]


def _safe_log(x: float) -> float:
    """安全对数，防止 log(0)"""
    return math.log(x + 1)


def calculate_citation_delta(
    current_count: int,
    previous_count: Optional[int],
) -> int:
    """计算引用增量。若无历史数据，以当前引用量的 10% 估算。"""
    if previous_count is None:
        return max(0, int(current_count * 0.10))
    return max(0, current_count - previous_count)


def _citation_velocity(delta: int, published_date: str) -> float:
    """
    引用速度 = 引用增量 ÷ 论文年龄天数。
    对新论文天然友好：3天获得5次引用 → 速度 1.67/天 >> 180天获得5次 → 0.03/天
    """
    try:
        pub = date.fromisoformat(published_date)
        days_old = max(1, (date.today() - pub).days)  # 至少1天
        return delta / days_old
    except Exception:
        return float(delta)


def _freshness_score(published_date: str) -> float:
    """
    指数衰减新鲜度：f(t) = 100 × e^(-t/14)
    - 1天 → 93,  7天 → 61,  14天 → 37,  30天 → 12,  60天 → 1
    """
    try:
        pub = date.fromisoformat(published_date)
        days_old = max(0, (date.today() - pub).days)
        return 100.0 * math.exp(-days_old / 14.0)
    except Exception:
        return 50.0


def _breadth_score(categories: list[str]) -> float:
    """跨领域宽度（保留作为辅助信息，不参与主评分）"""
    n = len(categories) if categories else 1
    return min(100.0, (n - 1) / 4.0 * 100)


def score_papers(
    papers: list[dict],
    citation_data: dict[str, dict],
    citation_history: dict[str, int],
    hn_data: Optional[dict[str, int]] = None,
    code_data: Optional[dict[str, dict]] = None,
    author_data: Optional[dict[str, int]] = None,
) -> list[dict]:
    """
    对论文列表计算 8 维度热度得分并排序。

    Args:
        papers: 论文列表
        citation_data: OpenAlex 引用量数据
        citation_history: 7天前的引用量快照
        hn_data: Hacker News buzz_score {arxiv_id: int}
        code_data: Papers With Code {arxiv_id: {"has_code": bool, "github_stars": int}}
        author_data: 作者 h-index {arxiv_id: int}

    Returns:
        论文列表，附加 score 字段，按 score 降序排列
    """
    if not papers:
        return []

    hn_data = hn_data or {}
    code_data = code_data or {}
    author_data = author_data or {}

    W = SCORE_WEIGHTS

    # ── Step 1: 计算原始各维度值 ───────────────────────────
    raw_velocity = []
    raw_mass = []
    raw_author = []
    raw_code = []
    raw_stars = []
    raw_freshness = []
    raw_buzz = []

    for paper in papers:
        arxiv_id = paper["arxiv_id"]
        ss = citation_data.get(arxiv_id, {})

        current_count = ss.get("citation_count", 0)
        previous_count = citation_history.get(arxiv_id)
        delta = calculate_citation_delta(current_count, previous_count)

        # 引用速度
        raw_velocity.append(
            _citation_velocity(delta, paper.get("published_date", ""))
        )
        # 引用总量（对数）
        raw_mass.append(_safe_log(current_count))
        # 作者 h-index（对数）
        raw_author.append(_safe_log(author_data.get(arxiv_id, 0)))
        # 有无代码（0 或 100）
        ci = code_data.get(arxiv_id, {})
        raw_code.append(100.0 if ci.get("has_code", False) else 0.0)
        # GitHub Stars（对数）
        raw_stars.append(_safe_log(ci.get("github_stars", 0)))
        # 新鲜度
        raw_freshness.append(
            _freshness_score(paper.get("published_date", ""))
        )
        # HN 讨论热度
        raw_buzz.append(float(hn_data.get(arxiv_id, 0)))

    # ── Step 2: 归一化 ──────────────────────────────────────
    norm_velocity = _min_max_normalize(raw_velocity)
    norm_mass = _min_max_normalize(raw_mass)
    norm_author = _min_max_normalize(raw_author)
    norm_code = raw_code                 # 已经是 0/100
    norm_stars = _min_max_normalize(raw_stars)
    norm_freshness = raw_freshness       # 已经是 0~100
    norm_buzz = _min_max_normalize(raw_buzz)

    # ── Step 3: 加权求和 ────────────────────────────────────
    results = []
    for i, paper in enumerate(papers):
        arxiv_id = paper["arxiv_id"]
        ss = citation_data.get(arxiv_id, {})
        ci = code_data.get(arxiv_id, {})

        current_count = ss.get("citation_count", 0)
        previous_count = citation_history.get(arxiv_id)
        delta = calculate_citation_delta(current_count, previous_count)

        score = (
            norm_velocity[i]  * W.get("citation_velocity", 25) / 100
            + norm_mass[i]    * W.get("citation_mass", 15)     / 100
            + norm_author[i]  * W.get("author_influence", 10)  / 100
            + norm_code[i]    * W.get("code_available", 5)     / 100
            + norm_stars[i]   * W.get("github_stars", 15)      / 100
            + norm_freshness[i] * W.get("freshness", 15)       / 100
            + norm_buzz[i]    * W.get("social_buzz", 15)       / 100
        )

        enriched = {
            **paper,
            "citation_count": current_count,
            "influential_citation_count": ss.get("influential_citation_count", 0),
            "citation_delta_7d": delta,
            "citation_velocity": round(raw_velocity[i], 4),
            "author_h_index": author_data.get(arxiv_id, 0),
            "has_code": ci.get("has_code", False),
            "github_stars": ci.get("github_stars", 0),
            "github_url": ci.get("github_url", ""),
            "hn_buzz": hn_data.get(arxiv_id, 0),
            "ss_paper_id": ss.get("ss_paper_id", ""),
            "score": round(score, 4),
            "score_breakdown": {
                "velocity_norm": round(norm_velocity[i], 2),
                "mass_norm": round(norm_mass[i], 2),
                "author_norm": round(norm_author[i], 2),
                "code_norm": round(norm_code[i], 2),
                "stars_norm": round(norm_stars[i], 2),
                "freshness_norm": round(norm_freshness[i], 2),
                "buzz_norm": round(norm_buzz[i], 2),
            },
        }
        results.append(enriched)

    results.sort(key=lambda x: x["score"], reverse=True)
    logger.info(f"[评分] 完成 {len(results)} 篇论文评分（8 维度）")

    if results:
        top = results[0]
        logger.info(
            f"[评分] Top 1: [{top['arxiv_id']}] score={top['score']:.2f} "
            f"| 引用={top['citation_count']} | 速度={top['citation_velocity']:.2f}/d "
            f"| h={top['author_h_index']} | ⭐={top['github_stars']} "
            f"| HN={top['hn_buzz']} | {top['title'][:50]}"
        )

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    test_papers = [
        {
            "arxiv_id": "2501.00001", "title": "New Paper (no citations)",
            "abstract": "", "authors": ["John Doe"], "categories": ["cs.AI", "cs.LG"],
            "primary_category": "cs.AI", "published_date": "2026-03-20",
            "arxiv_url": "", "pdf_url": ""
        },
        {
            "arxiv_id": "2501.00002", "title": "Established Paper (many citations)",
            "abstract": "", "authors": ["Jane Smith"], "categories": ["cs.LG"],
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
    hn_data = {"2501.00002": 120}
    code_data = {"2501.00002": {"has_code": True, "github_stars": 500}}
    author_data = {"2501.00002": 45}

    results = score_papers(
        test_papers, citation_data, citation_history,
        hn_data=hn_data, code_data=code_data, author_data=author_data
    )
    for r in results:
        print(
            f"[{r['arxiv_id']}] score={r['score']:.4f} "
            f"| 速度={r['citation_velocity']:.2f}/d "
            f"| h={r['author_h_index']} "
            f"| ⭐={r['github_stars']} "
            f"| HN={r['hn_buzz']} "
            f"| {r['title']}"
        )
