# crawler/reddit_fetcher.py — 可选：从 Reddit r/MachineLearning 抓取讨论量
# 注意：需要配置 REDDIT_CLIENT_ID 和 REDDIT_CLIENT_SECRET 环境变量

import json
import time
import logging
import urllib.request
import urllib.parse
from typing import Optional

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT, REDDIT_SUBREDDIT

logger = logging.getLogger(__name__)


class RedditFetcher:
    """通过 Reddit OAuth 获取帖子数据"""

    TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
    API_BASE = "https://oauth.reddit.com"

    def __init__(self):
        self._token: Optional[str] = None
        self._token_expires = 0.0

    def _get_token(self) -> Optional[str]:
        """获取/刷新 OAuth Token"""
        if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
            logger.info("[Reddit] 未配置 Client ID/Secret，跳过 Reddit 数据采集")
            return None

        if self._token and time.time() < self._token_expires:
            return self._token

        credentials = f"{REDDIT_CLIENT_ID}:{REDDIT_CLIENT_SECRET}".encode()
        import base64
        encoded = base64.b64encode(credentials).decode()

        data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode()
        req = urllib.request.Request(
            self.TOKEN_URL,
            data=data,
            headers={
                "Authorization": f"Basic {encoded}",
                "User-Agent": REDDIT_USER_AGENT,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read())
                self._token = result.get("access_token")
                expires_in = result.get("expires_in", 3600)
                self._token_expires = time.time() + expires_in - 60
                logger.info("[Reddit] Token 获取成功")
                return self._token
        except Exception as e:
            logger.warning(f"[Reddit] Token 获取失败: {e}")
            return None

    def search_paper(self, arxiv_id: str, title: str) -> int:
        """
        搜索某篇论文在 r/MachineLearning 的讨论帖子，返回总评论数。

        Args:
            arxiv_id: 论文 arXiv ID
            title: 论文标题（用于搜索）

        Returns:
            讨论评论总数（无结果则为 0）
        """
        token = self._get_token()
        if not token:
            return 0

        # 先用 arXiv ID 搜，再用标题前50字搜
        for query in [arxiv_id, title[:50]]:
            score = self._search_query(query, token)
            if score > 0:
                return score
        return 0

    def _search_query(self, query: str, token: str) -> int:
        params = urllib.parse.urlencode({
            "q": query,
            "restrict_sr": "true",
            "sort": "relevance",
            "limit": 5,
            "t": "month",
        })
        url = f"{self.API_BASE}/r/{REDDIT_SUBREDDIT}/search?{params}"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "User-Agent": REDDIT_USER_AGENT,
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                posts = data.get("data", {}).get("children", [])
                total_comments = sum(
                    p.get("data", {}).get("num_comments", 0) for p in posts
                )
                return total_comments
        except Exception as e:
            logger.debug(f"[Reddit] 搜索失败 ({query}): {e}")
            return 0

    def batch_fetch(self, papers: list[dict], delay: float = 1.0) -> dict[str, int]:
        """
        批量获取论文 Reddit 讨论量。

        Args:
            papers: 论文列表，每项需含 arxiv_id 和 title
            delay: 每次请求间隔秒数

        Returns:
            dict, key=arxiv_id, value=reddit讨论量
        """
        results = {}
        for i, paper in enumerate(papers):
            arxiv_id = paper["arxiv_id"]
            title = paper["title"]
            score = self.search_paper(arxiv_id, title)
            results[arxiv_id] = score
            if i < len(papers) - 1:
                time.sleep(delay)
        logger.info(f"[Reddit] 处理 {len(results)} 篇论文，有讨论: {sum(1 for v in results.values() if v > 0)} 篇")
        return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    fetcher = RedditFetcher()
    score = fetcher.search_paper("2303.08774", "LLaMA: Open and Efficient Foundation Language Models")
    print(f"Reddit 讨论量: {score}")
