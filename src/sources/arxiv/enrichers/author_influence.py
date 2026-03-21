"""
src/sources/arxiv/enrichers/author_influence.py — 作者影响力（h-index）

通过 OpenAlex API 查询论文作者的学术影响力，取最高 h-index。
API 文档：https://docs.openalex.org/api-entities/authors
"""

import logging
import time
import urllib.request
import urllib.parse
import json
import ssl
import os
import math

logger = logging.getLogger(__name__)

OPENALEX_API = "https://api.openalex.org"
_EMAIL = os.getenv("OPENALEX_EMAIL", "")

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

# 缓存：作者名 → h_index（同一次运行内去重）
_author_cache: dict[str, int] = {}


def _http_get_json(url: str) -> dict | None:
    """通用 HTTP GET JSON"""
    hdrs = {"User-Agent": "ai-paper-tracker/2.0"}
    try:
        req = urllib.request.Request(url, headers=hdrs)
        with urllib.request.urlopen(req, timeout=15, context=_SSL_CTX) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        logger.debug(f"  [Author] HTTP 错误: {e}")
        return None


def _get_author_h_index(author_name: str) -> int:
    """
    通过 OpenAlex 搜索作者并返回其 h-index。
    使用 summary_stats.h_index 字段（OpenAlex 直接提供）。
    """
    if author_name in _author_cache:
        return _author_cache[author_name]

    # 搜索作者
    params = urllib.parse.urlencode({
        "search": author_name,
        "per_page": 1,
        "select": "id,display_name,summary_stats",
    })
    mailto = f"&mailto={_EMAIL}" if _EMAIL else ""
    url = f"{OPENALEX_API}/authors?{params}{mailto}"

    data = _http_get_json(url)
    if not data or not data.get("results"):
        _author_cache[author_name] = 0
        return 0

    author = data["results"][0]
    stats = author.get("summary_stats", {})
    h_index = stats.get("h_index", 0) or 0

    _author_cache[author_name] = h_index
    return h_index


def get_max_author_h_index(authors: list[str], max_check: int = 3) -> int:
    """
    取论文作者列表中 h-index 最高的值。
    只检查前 max_check 个作者（通常第一作者和最后作者最重要）。

    Args:
        authors: 作者名列表
        max_check: 最多检查几位作者

    Returns:
        最高 h-index 值
    """
    if not authors:
        return 0

    # 检查第一作者 + 最后作者 + 中间（如果有的话）
    candidates = []
    if len(authors) <= max_check:
        candidates = authors
    else:
        candidates = [authors[0], authors[-1]]  # 第一和最后作者
        if max_check > 2 and len(authors) > 2:
            candidates.append(authors[1])  # 第二作者

    max_h = 0
    for name in candidates:
        h = _get_author_h_index(name)
        max_h = max(max_h, h)
        time.sleep(0.2)  # 友好限速

    return max_h


def batch_fetch_author_influence(
    papers: list[dict],
    max_papers: int = 50,
) -> dict[str, int]:
    """
    批量查询论文的作者影响力。

    Args:
        papers: 论文列表（需有 authors 字段）
        max_papers: 最多查询篇数

    Returns:
        {arxiv_id: max_h_index, ...}
    """
    results = {}
    to_query = papers[:max_papers]
    total_queries = 0

    logger.info(f"[Author] 查询 {len(to_query)} 篇论文的作者影响力")

    for paper in to_query:
        arxiv_id = paper.get("arxiv_id", "")
        authors = paper.get("authors", [])
        h = get_max_author_h_index(authors)
        results[arxiv_id] = h
        if h > 0:
            total_queries += 1

    logger.info(f"[Author] 完成：{total_queries}/{len(to_query)} 篇有作者 h-index 数据")
    logger.info(f"[Author] 作者缓存池：{len(_author_cache)} 位作者")
    return results
