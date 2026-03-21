# crawler/semantic_scholar.py — 查询 Semantic Scholar 引用量数据
# 策略：优先 POST 批量，失败则降级为逐篇 GET（间隔 3s，避免限流）

import ssl
import time
import json
import logging
import urllib.request
import urllib.error
from typing import Optional

# Windows SSL 绕过
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import SS_API_KEY, SS_BASE_URL, SS_BATCH_SIZE

logger = logging.getLogger(__name__)

FIELDS = "citationCount,influentialCitationCount,referenceCount,year,publicationDate"


def _build_headers() -> dict:
    headers = {"Content-Type": "application/json"}
    if SS_API_KEY:
        headers["x-api-key"] = SS_API_KEY
    return headers


def _get_json(url: str, headers: dict, timeout: int = 20) -> Optional[dict]:
    """GET 请求，遇到 429 时退避等待"""
    req = urllib.request.Request(url, headers=headers)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 60 * (attempt + 1)  # 60s / 120s / 180s
                logger.info(f"[SS] 限流，等待 {wait}s ...")
                time.sleep(wait)
            elif e.code == 404:
                return None
            else:
                logger.debug(f"[SS] HTTP {e.code}: {url}")
                return None
        except Exception as e:
            logger.debug(f"[SS] 请求异常: {e}")
            time.sleep(5)
    return None


def _post_json(url: str, payload: dict, headers: dict, timeout: int = 30) -> Optional[list]:
    """POST 请求（批量接口）"""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 429:
            logger.info("[SS] POST 限流，将降级为 GET")
        else:
            logger.debug(f"[SS] POST HTTP {e.code}")
        return None
    except Exception as e:
        logger.debug(f"[SS] POST 异常: {e}")
        return None


def fetch_single_paper(arxiv_id: str) -> Optional[dict]:
    """查询单篇论文引用量（GET，无 Key 也可用，但每秒 ≈1 次）"""
    headers = _build_headers()
    url = f"{SS_BASE_URL}/paper/ArXiv:{arxiv_id}?fields={FIELDS}"
    data = _get_json(url, headers)
    if not data:
        return None
    return {
        "citation_count": data.get("citationCount") or 0,
        "influential_citation_count": data.get("influentialCitationCount") or 0,
        "reference_count": data.get("referenceCount") or 0,
        "ss_paper_id": data.get("paperId", ""),
    }


def fetch_citation_batch(arxiv_ids: list[str]) -> dict[str, dict]:
    """
    批量查询引用量：优先 POST（有 Key 时有效），失败则逐篇 GET。

    无 Key 时建议 batch_size ≤ 20，GET 间隔 ≥ 3s。
    """
    if not arxiv_ids:
        return {}

    # ── 尝试 POST ──────────────────────────────────────────
    headers = _build_headers()
    url = f"{SS_BASE_URL}/paper/batch?fields={FIELDS},externalIds"
    payload = {"ids": [f"ArXiv:{aid}" for aid in arxiv_ids]}

    logger.info(f"[SS] POST 批量查询 {len(arxiv_ids)} 篇")
    result = _post_json(url, payload, headers)

    output = {}
    if result and isinstance(result, list):
        for item in result:
            if not item:
                continue
            try:
                ext = item.get("externalIds") or {}
                aid = ext.get("ArXiv", "")
                if not aid:
                    continue
                output[aid] = {
                    "citation_count": item.get("citationCount") or 0,
                    "influential_citation_count": item.get("influentialCitationCount") or 0,
                    "reference_count": item.get("referenceCount") or 0,
                    "ss_paper_id": item.get("paperId", ""),
                }
            except Exception:
                continue

    # ── 降级：逐篇 GET ─────────────────────────────────────
    if not output:
        logger.info(f"[SS] POST 无效，降级 GET（间隔 3s），共 {len(arxiv_ids)} 篇")
        for i, aid in enumerate(arxiv_ids):
            data = fetch_single_paper(aid)
            if data:
                output[aid] = data
                if data["citation_count"] > 0:
                    logger.info(f"  [{i+1}/{len(arxiv_ids)}] {aid}: {data['citation_count']} 引用")
            if i < len(arxiv_ids) - 1:
                time.sleep(3.0)  # 无 Key：3s 间隔，约 20/分钟，不易触发限流

    logger.info(f"[SS] 获取 {len(output)}/{len(arxiv_ids)} 篇引用数据")
    return output


def fetch_all_citations(
    arxiv_ids: list[str],
    batch_size: int = 20,          # 无 Key 时每批 20 篇
    inter_batch_delay: float = 10.0,  # 批次间额外等待 10s
) -> dict[str, dict]:
    """
    分批查询所有论文引用量，批次间多等一会儿。

    Args:
        arxiv_ids: 所有 arXiv ID
        batch_size: 每批数量（有 Key 可调到 100）
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
        logger.info(f"[SS] 批次 {batch_num}/{batches}，共 {len(batch)} 篇")
        batch_result = fetch_citation_batch(batch)
        all_results.update(batch_result)
        if i + batch_size < total:
            logger.info(f"[SS] 批次间休息 {inter_batch_delay}s ...")
            time.sleep(inter_batch_delay)

    return all_results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    # 测试经典论文
    test_ids = ["2303.08774", "2307.09288"]  # LLaMA, LLaMA 2
    results = fetch_all_citations(test_ids, batch_size=2)
    for aid, data in results.items():
        print(f"[{aid}] 引用量: {data['citation_count']:,}")
