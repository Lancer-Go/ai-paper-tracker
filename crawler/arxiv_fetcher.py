# crawler/arxiv_fetcher.py — 从 arXiv API 抓取最新论文

import ssl
import time
import logging

# Windows 企业代理环境下可能缺少根证书，创建不验证 SSL 的上下文
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from typing import Optional

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import ARXIV_BASE_URL, ARXIV_CATEGORIES, ARXIV_MAX_RESULTS_PER_CATEGORY

logger = logging.getLogger(__name__)

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}


def _parse_arxiv_id(url: str) -> str:
    """从 arXiv 链接中提取 ID，例如 http://arxiv.org/abs/2501.12345v1 → 2501.12345"""
    arxiv_id = url.split("/abs/")[-1]
    # 去掉版本号
    if "v" in arxiv_id:
        arxiv_id = arxiv_id.rsplit("v", 1)[0]
    return arxiv_id


def _parse_entry(entry: ET.Element) -> Optional[dict]:
    """解析单条 arXiv 记录为 dict"""
    try:
        arxiv_id = _parse_arxiv_id(
            entry.find("atom:id", NS).text.strip()
        )
        title = entry.find("atom:title", NS).text.strip().replace("\n", " ")
        summary = entry.find("atom:summary", NS).text.strip().replace("\n", " ")
        published_str = entry.find("atom:published", NS).text.strip()
        published = datetime.fromisoformat(published_str.replace("Z", "+00:00"))

        authors = [
            a.find("atom:name", NS).text.strip()
            for a in entry.findall("atom:author", NS)
        ]

        # 类别
        categories = [
            c.attrib.get("term", "")
            for c in entry.findall("atom:category", NS)
        ]
        primary_category = entry.find("arxiv:primary_category", NS)
        primary = primary_category.attrib.get("term", "") if primary_category is not None else (categories[0] if categories else "")

        return {
            "arxiv_id": arxiv_id,
            "title": title,
            "abstract": summary,
            "authors": authors,
            "categories": categories,
            "primary_category": primary,
            "published_date": published.date().isoformat(),
            "arxiv_url": f"https://arxiv.org/abs/{arxiv_id}",
            "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}",
        }
    except Exception as e:
        logger.warning(f"解析 arXiv 记录失败: {e}")
        return None


def fetch_papers_by_category(
    category: str,
    max_results: int = ARXIV_MAX_RESULTS_PER_CATEGORY,
    days_back: int = 7,
) -> list[dict]:
    """
    抓取指定类别近 N 天的最新论文。

    Args:
        category: arXiv 类别，如 'cs.AI'
        max_results: 最多返回条数
        days_back: 往回看几天

    Returns:
        论文 dict 列表
    """
    since_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y%m%d")
    
    params = urllib.parse.urlencode({
        "search_query": f"cat:{category} AND submittedDate:[{since_date}0000 TO 99991231235959]",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    })
    url = f"{ARXIV_BASE_URL}?{params}"
    
    logger.info(f"[arXiv] 抓取 {category}，近 {days_back} 天，最多 {max_results} 篇")
    
    try:
        with urllib.request.urlopen(url, timeout=30, context=_SSL_CTX) as resp:
            content = resp.read()
    except Exception as e:
        logger.error(f"[arXiv] 请求失败 ({category}): {e}")
        return []

    root = ET.fromstring(content)
    entries = root.findall("atom:entry", NS)
    
    papers = []
    for entry in entries:
        paper = _parse_entry(entry)
        if paper:
            papers.append(paper)
    
    logger.info(f"[arXiv] {category} 获取 {len(papers)} 篇论文")
    return papers


def fetch_all_categories(
    categories: list[str] = ARXIV_CATEGORIES,
    max_per_category: int = ARXIV_MAX_RESULTS_PER_CATEGORY,
    days_back: int = 7,
    delay: float = 3.0,
) -> list[dict]:
    """
    遍历所有类别抓取论文。

    Args:
        categories: 类别列表
        max_per_category: 每类最多条数
        days_back: 往回看几天
        delay: 类别间请求延迟（秒），避免触发限流

    Returns:
        所有类别论文合并列表（含重复，需后续去重）
    """
    all_papers = []
    for cat in categories:
        papers = fetch_papers_by_category(cat, max_per_category, days_back)
        all_papers.extend(papers)
        if cat != categories[-1]:
            time.sleep(delay)
    logger.info(f"[arXiv] 全类别共抓取 {len(all_papers)} 篇（含重复）")
    return all_papers


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    papers = fetch_papers_by_category("cs.AI", max_results=5, days_back=7)
    for p in papers:
        print(f"[{p['arxiv_id']}] {p['title'][:80]}...")
