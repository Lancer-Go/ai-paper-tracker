"""补充引用量快照，然后重新评分导出"""
import sys, sqlite3
sys.path.insert(0, ".")

DB_PATH = "data/papers.db"
TODAY = "2026-03-21"

# 读取已有论文 ID
conn = sqlite3.connect(DB_PATH)
ids = [r[0] for r in conn.execute("SELECT arxiv_id FROM papers").fetchall()]
conn.close()
print(f"准备查询 {len(ids)} 篇论文引用量...")

from crawler.semantic_scholar import fetch_all_citations
from storage.db import save_citation_snapshots
results = fetch_all_citations(ids)
print(f"获取引用量: {len(results)} 篇")
non_zero = {k: v for k, v in results.items() if v.get("citation_count", 0) > 0}
print(f"有引用量的论文: {len(non_zero)} 篇")
save_citation_snapshots(results, snapshot_date=TODAY)

# 重新执行 rescore
exec(open("rescore.py").read())
