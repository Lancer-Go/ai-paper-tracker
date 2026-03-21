"""
scripts/fetch_citations.py — 补充引用量快照，然后重新评分导出

用法：
    python scripts/fetch_citations.py               # 默认今天
    python scripts/fetch_citations.py 2026-03-21     # 指定日期
"""
import sys, sqlite3
from datetime import date

sys.path.insert(0, ".")

from src.config import DB_PATH
from src.sources.arxiv.enrichers.semantic_scholar import fetch_all_citations
from src.storage.db import save_citation_snapshots

TODAY = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()

# 读取已有论文 ID
conn = sqlite3.connect(DB_PATH)
ids = [r[0] for r in conn.execute("SELECT arxiv_id FROM papers").fetchall()]
conn.close()
print(f"准备查询 {len(ids)} 篇论文引用量...")

results = fetch_all_citations(ids)
print(f"获取引用量: {len(results)} 篇")
non_zero = {k: v for k, v in results.items() if v.get("citation_count", 0) > 0}
print(f"有引用量的论文: {len(non_zero)} 篇")
save_citation_snapshots(results, snapshot_date=TODAY)

# 重新评分
print("\n重新评分...")
import subprocess
subprocess.run([sys.executable, "scripts/rescore.py", TODAY])
