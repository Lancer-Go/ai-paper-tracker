"""
src/sources/arxiv/enrichers/paperswithcode.py — Papers With Code + GitHub Stars

查询论文是否有配套开源代码，以及代码仓库的 GitHub 星标数。
- Papers With Code API（免费，CC-BY-SA）
- GitHub REST API（免费，60 次/小时无需 Token）
"""

import logging
import time
import urllib.request
import json
import ssl
import re

logger = logging.getLogger(__name__)

PWC_API_URL = "https://paperswithcode.com/api/v1/papers"
GITHUB_API_URL = "https://api.github.com/repos"

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE


def _http_get_json(url: str, headers: dict = None) -> dict | None:
    """通用 HTTP GET JSON"""
    hdrs = {"User-Agent": "ai-paper-tracker/2.0"}
    if headers:
        hdrs.update(headers)
    try:
        req = urllib.request.Request(url, headers=hdrs)
        with urllib.request.urlopen(req, timeout=15, context=_SSL_CTX) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        logger.debug(f"  [PwC] HTTP 错误 ({url[:60]}): {e}")
        return None


def _extract_github_repo(url: str) -> str | None:
    """从 URL 提取 GitHub owner/repo"""
    match = re.search(r"github\.com/([^/]+/[^/]+)", url)
    if match:
        repo = match.group(1).rstrip("/").split("#")[0].split("?")[0]
        # 去掉常见后缀如 .git
        repo = repo.removesuffix(".git")
        return repo
    return None


def fetch_paper_code(arxiv_id: str) -> dict:
    """
    查询单篇论文的代码信息。

    Returns:
        {
            "has_code": bool,
            "github_url": str | None,
            "github_stars": int,
            "framework": str | None,
        }
    """
    result = {
        "has_code": False,
        "github_url": None,
        "github_stars": 0,
        "framework": None,
    }

    # Step 1: 查 Papers With Code
    # PwC API 用 arXiv ID 查询格式：arxiv:2501.00001
    url = f"{PWC_API_URL}/?arxiv_id={arxiv_id}"
    data = _http_get_json(url)

    if not data or not data.get("results"):
        return result

    paper = data["results"][0]
    paper_id = paper.get("id", "")

    # Step 2: 查代码仓库
    repos_url = f"{PWC_API_URL}/{paper_id}/repositories/"
    repos_data = _http_get_json(repos_url)

    if not repos_data or not repos_data.get("results"):
        return result

    # 取星标最多的仓库
    best_repo = None
    best_stars = -1

    for repo in repos_data.get("results", []):
        repo_url = repo.get("url", "")
        stars = repo.get("stars", 0) or 0
        if stars > best_stars:
            best_stars = stars
            best_repo = repo

    if best_repo:
        result["has_code"] = True
        result["github_url"] = best_repo.get("url", "")
        result["github_stars"] = best_repo.get("stars", 0) or 0
        result["framework"] = best_repo.get("framework", None)

    # Step 3: 如果 PwC 没返回 stars，尝试直接查 GitHub API
    if result["has_code"] and result["github_stars"] == 0 and result["github_url"]:
        repo_path = _extract_github_repo(result["github_url"])
        if repo_path:
            gh_data = _http_get_json(f"{GITHUB_API_URL}/{repo_path}")
            if gh_data:
                result["github_stars"] = gh_data.get("stargazers_count", 0)

    return result


def batch_fetch_code_info(
    papers: list[dict],
    delay: float = 0.5,
    max_papers: int = 50,
) -> dict[str, dict]:
    """
    批量查询论文的代码信息。

    Args:
        papers: 论文列表
        delay: 请求间隔
        max_papers: 最多查询篇数（GitHub API 无 Token 限 60 次/小时）

    Returns:
        {arxiv_id: {"has_code": bool, "github_stars": int, ...}, ...}
    """
    results = {}
    to_query = papers[:max_papers]
    found = 0

    logger.info(f"[PwC] 查询 {len(to_query)} 篇论文的代码信息")

    for i, paper in enumerate(to_query):
        arxiv_id = paper.get("arxiv_id", "")
        info = fetch_paper_code(arxiv_id)
        results[arxiv_id] = info

        if info["has_code"]:
            found += 1
            logger.debug(
                f"  [PwC] {arxiv_id}: ⭐ {info['github_stars']} | {info['github_url']}"
            )

        if i < len(to_query) - 1:
            time.sleep(delay)

    logger.info(f"[PwC] 完成：{found}/{len(to_query)} 篇有开源代码")
    return results
