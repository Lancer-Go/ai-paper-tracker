# config.py — 项目全局配置

import os

# ── arXiv ──────────────────────────────────────────────
ARXIV_CATEGORIES = [
    "cs.AI",   # 人工智能
    "cs.LG",   # 机器学习
    "cs.CV",   # 计算机视觉
    "cs.CL",   # 计算语言学 / NLP
    "cs.RO",   # 机器人
    "cs.NE",   # 神经网络与进化计算
    "stat.ML", # 统计机器学习
    "q-bio.NC",# 神经认知科学（计算神经科学、认知心理学）
    "econ.GN", # 经济学通论（含行为心理、屡约理论相关研究）
]
ARXIV_MAX_RESULTS_PER_CATEGORY = 100  # 每类每日最多抓取条数
ARXIV_BASE_URL = "http://export.arxiv.org/api/query"

# ── Semantic Scholar ────────────────────────────────────
SS_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")  # 可选，可提高请求限额
SS_BASE_URL = "https://api.semanticscholar.org/graph/v1"
SS_BATCH_SIZE = 100  # 每批查询论文数

# ── Reddit（可选）──────────────────────────────────────
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = "ai-paper-tracker/1.0"
REDDIT_SUBREDDIT = "MachineLearning"

# ── 热度评分权重 ────────────────────────────────────────
SCORE_WEIGHTS = {
    "citation_delta_7d": 0.50,  # 近7日引用增量
    "citation_total_log": 0.30,  # 引用总量对数
    "reddit_score": 0.20,        # Reddit 讨论热度（可选，无数据则置0）
}

# ── 数据库 ──────────────────────────────────────────────
_PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))  # ai-paper-tracker/
DB_PATH = os.path.join(_PROJECT_ROOT, "data", "papers.db")
EXPORT_DIR = os.path.join(_PROJECT_ROOT, "data", "exports")

# ── 其他 ────────────────────────────────────────────────
TOP_N = 50          # 每日热榜展示 Top N
LOOKBACK_DAYS = 7   # 引用增量统计窗口（天）
