# crawler/openalex_fetcher.py — 用 OpenAlex API 查询论文引用量
#
# OpenAlex 优势：
#   - 完全免费，无需 API Key，无需注册
#   - 加 mailto 参数进入"礼貌池"：10 req/s，每天 100,000 次
#   - 通过 arXiv DOI 直接查询（格式：10.48550/arXiv.{id}）

import ssl
import json
import time
import logging
import urllib.request
import urllib.error
from typing import Optional

# Windows SSL 绕过
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

import os

logger = logging.getLogger(__name__)

OPENALEX_BASE = "https://api.openalex.org"
# 礼貌池邮箱（任意邮箱即可，获得更宽松速率）
POLITE_EMAIL = os.getenv("OPENALEX_EMAIL", "ai-paper-tracker@example.com")


def _get(url: str, timeout: int = 20) -> Optional[dict]:
    """GET 请求 OpenAlex，遇 429 退避重试"""
    sep = "&" if "?" in url else "?"
    full_url = f"{url}{sep}mailto={POLITE_EMAIL}"
    req = urllib.request.Request(
        full_url,
        headers={"User-Agent": "ai-paper-tracker/1.0 (mailto:ai-paper-tracker@example.com)"}
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 30 * (attempt + 1)
                logger.info(f"[OA] 限流，等待 {wait}s ...")
                time.sleep(wait)
            elif e.code == 404:
                return None   # 论文未被 OpenAlex 收录，正常情况
            else:
                logger.debug(f"[OA] HTTP {e.code}: {full_url[:80]}")
                return None
        except Exception as e:
            logger.debug(f"[OA] 请求异常: {e}")
            time.sleep(3)
    return None


def _arxiv_doi(arxiv_id: str) -> str:
    """将 arXiv ID 转为 DOI 格式（去除版本号）"""
    clean_id = arxiv_id.split("v")[0] if "v" in arxiv_id else arxiv_id
    return f"10.48550/arXiv.{clean_id}"


def fetch_single_paper(arxiv_id: str) -> Optional[dict]:
    """
    用 arXiv ID 查询单篇论文引用量（通过 DOI 路径）。

    Args:
        arxiv_id: 如 '2303.08774'

    Returns:
        {"citation_count": int, "influential_citation_count": int, "ss_paper_id": str}
        或 None（未被 OpenAlex 收录）
    """
    doi = _arxiv_doi(arxiv_id)
    # OpenAlex DOI 路径格式: /works/doi:{doi}
    url = f"{OPENALEX_BASE}/works/doi:{doi}?select=id,cited_by_count"
    data = _get(url)
    if not data or "cited_by_count" not in data:
        return None
    return {
        "citation_count": data.get("cited_by_count") or 0,
        "influential_citation_count": 0,  # OpenAlex 不区分影响性引用
        "reference_count": 0,
        "ss_paper_id": data.get("id", "").replace("https://openalex.org/", "OA:"),
    }


def fetch_batch_papers(arxiv_ids: list[str]) -> dict[str, dict]:
    """
    批量查询引用量（礼貌池：1s/篇，基本不触发限流）。

    Args:
        arxiv_ids: arXiv ID 列表

    Returns:
        dict, key=arxiv_id, value=引用量数据
    """
    if not arxiv_ids:
        return {}

    output = {}
    total = len(arxiv_ids)
    logger.info(f"[OA] 查询 {total} 篇引用量（间隔 1s）")

    for i, arxiv_id in enumerate(arxiv_ids):
        data = fetch_single_paper(arxiv_id)
        if data:
            output[arxiv_id] = data
            cite = data["citation_count"]
            if cite > 0:
                logger.info(f"  [{i+1}/{total}] {arxiv_id}: {cite:,} 引用")
        if i < total - 1:
            time.sleep(1.0)  # 1 req/s，礼貌池绰绰有余

    not_found = total - len(output)
    logger.info(f"[OA] 获取 {len(output)}/{total} 篇（{not_found} 篇未被收录/太新）")
    return output


def fetch_all_citations(
    arxiv_ids: list[str],
    batch_size: int = 50,
    inter_batch_delay: float = 5.0,
) -> dict[str, dict]:
    """
    分批查询所有论文引用量。

    Args:
        arxiv_ids: 所有 arXiv ID
        batch_size: 每批数量（50 篇 ≈ 50s）
        inter_batch_delay: 批次间等待秒数

    Returns:
        合并后的引用量字典
    """
    all_results = {}
    total = len(arxiv_ids)
    batches = (total + batch_size - 1) // batch_size

    for i in range(0, total, batch_size):
        batch_num = i // batch_size + 1
        batch = arxiv_ids[i: i + batch_size]
        logger.info(f"[OA] 批次 {batch_num}/{batches}，{len(batch)} 篇")
        batch_result = fetch_batch_papers(batch)
        all_results.update(batch_result)
        if i + batch_size < total:
            logger.info(f"[OA] 批次间休息 {inter_batch_delay}s ...")
            time.sleep(inter_batch_delay)

    return all_results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    print("测试 OpenAlex 引用量查询...")
    r1 = fetch_single_paper("2303.08774")
    print(f"LLaMA (2303.08774):   {r1}")
    r2 = fetch_single_paper("2307.09288")
    print(f"LLaMA 2 (2307.09288): {r2}")
