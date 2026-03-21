"""
数据源抽象基类 — 所有资讯源必须实现此接口

未来添加新数据源（如 GitHub Trending、RSS 新闻等），
只需在 src/sources/ 下新建一个目录并实现 BaseSource 即可。
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseSource(ABC):
    """数据源抽象接口"""

    @property
    @abstractmethod
    def name(self) -> str:
        """数据源名称（如 'arxiv', 'github', 'rss'）"""
        ...

    @abstractmethod
    def fetch(self, **kwargs) -> list[dict]:
        """
        抓取原始数据，返回标准化的条目列表。
        每个条目至少包含: id, title, url, published_date
        """
        ...

    def enrich(self, items: list[dict], **kwargs) -> list[dict]:
        """
        补充元数据（引用量、讨论量等）。
        默认实现为原样返回，子类可覆盖。
        """
        return items

    def deduplicate(self, items: list[dict]) -> list[dict]:
        """
        去重。默认按 id 字段去重，子类可覆盖。
        """
        seen = set()
        unique = []
        for item in items:
            item_id = item.get("id") or item.get("arxiv_id", "")
            if item_id not in seen:
                seen.add(item_id)
                unique.append(item)
        return unique
