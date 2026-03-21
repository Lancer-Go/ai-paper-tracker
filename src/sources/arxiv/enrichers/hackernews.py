"""
src/sources/arxiv/enrichers/hackernews.py — Hacker News 社区讨论量采集

通过 HN Algolia API 搜索论文在 Hacker News 上的讨论。
API 文档：https://hn.algolia.com/api
限制：10,000 次/小时（免费、无需 Key）
"""

import logging
import time
import urllib.parse
import urllib.request
import json
import ssl

logger = logging.getLogger(__name__)

HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search"

# 忽略 SSL 验证（部分企业网络环境需要）
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE


def _search_hn(query: str) -> dict:
    """搜索 HN，返回原始 JSON 响应"""
    params = urllib.parse.urlencode({
        "query": query,
        "tags": "story",          # 只搜 story（排除 comment）
        "hitsPerPage": 5,         # 最多取 5 条
    })
    url = f"{HN_SEARCH_URL}?{params}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ai-paper-tracker/2.0"})
        with urllib.request.urlopen(req, timeout=10, context=_SSL_CTX) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        logger.debug(f"  [HN] 搜索失败 ({query[:40]}): {e}")
        return {}


def fetch_hn_buzz(arxiv_id: str, title: str = "") -> dict:
    """
    查询单篇论文的 HN 讨论热度。

    Returns:
        {"points": int, "comments": int, "stories": int, "buzz_score": int}
    """
    total_points = 0
    total_comments = 0
    story_count = 0

    # 策略1：按 arXiv ID 搜索（精确匹配）
    data = _search_hn(arxiv_id)
    hits = data.get("hits", [])

    # 策略2：如果没有结果，用论文标题搜索（模糊匹配）
    if not hits and title:
        # 取标题前 8 个词，避免太长
        short_title = " ".join(title.split()[:8])
        data = _search_hn(short_title)
        hits = data.get("hits", [])

    for hit in hits:
        total_points += hit.get("points", 0) or 0
        total_comments += hit.get("num_comments", 0) or 0
        story_count += 1

    buzz_score = total_points + total_comments * 2  # 评论权重高于点赞

    return {
        "points": total_points,
        "comments": total_comments,
        "stories": story_count,
        "buzz_score": buzz_score,
    }


def batch_fetch_hn_buzz(papers: list[dict], delay: float = 0.3) -> dict[str, int]:
    """
    批量查询论文的 HN 讨论热度。

    Args:
        papers: 论文列表（需有 arxiv_id 和 title 字段）
        delay: 请求间隔（秒），0.3s = ~200 次/分钟，远低于限制

    Returns:
        {arxiv_id: buzz_score, ...}
    """
    results = {}
    total = len(papers)
    found = 0

    logger.info(f"[HN] 查询 {total} 篇论文的 Hacker News 讨论量")

    for i, paper in enumerate(papers):
        arxiv_id = paper.get("arxiv_id", "")
        title = paper.get("title", "")

        buzz = fetch_hn_buzz(arxiv_id, title)
        results[arxiv_id] = buzz["buzz_score"]

        if buzz["buzz_score"] > 0:
            found += 1
            logger.debug(f"  [HN] {arxiv_id}: {buzz['buzz_score']} (点赞={buzz['points']}, 评论={buzz['comments']})")

        if i < total - 1:
            time.sleep(delay)

    logger.info(f"[HN] 完成：{found}/{total} 篇有 HN 讨论")
    return results
