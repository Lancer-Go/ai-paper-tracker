# processor/deduper.py — 按 arXiv ID 去重

import logging

logger = logging.getLogger(__name__)


def deduplicate(papers: list[dict]) -> list[dict]:
    """
    对论文列表按 arXiv ID 去重，保留最先出现的记录。

    Args:
        papers: 原始论文列表（可含重复）

    Returns:
        去重后的论文列表
    """
    seen = set()
    result = []
    for paper in papers:
        arxiv_id = paper.get("arxiv_id", "")
        if not arxiv_id:
            continue
        if arxiv_id not in seen:
            seen.add(arxiv_id)
            result.append(paper)

    removed = len(papers) - len(result)
    logger.info(f"[去重] 原始 {len(papers)} 篇 → 去重后 {len(result)} 篇（移除 {removed} 条重复）")
    return result
