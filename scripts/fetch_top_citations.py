# -*- coding: utf-8 -*-
"""
fetch_top_citations.py
对排名靠前的论文拉取引用量快照并重新评分
用法：python fetch_top_citations.py [limit]
"""
import sys, json, sqlite3, time, logging
sys.path.insert(0, ".")
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 100
TODAY = "2026-03-21"
DB_PATH = "data/papers.db"

# 读取已有论文（按最新日期排序，优先查新论文）
conn = sqlite3.connect(DB_PATH)
rows = conn.execute(
    "SELECT arxiv_id, published_date FROM papers ORDER BY published_date DESC LIMIT ?",
    (LIMIT,)
).fetchall()
ids = [r[0] for r in rows]
conn.close()
print(f"将查询 {len(ids)} 篇论文的引用量...")

# 逐篇 GET 查询
from crawler.semantic_scholar import fetch_single_paper
from storage.db import save_citation_snapshots

results = {}
for i, arxiv_id in enumerate(ids):
    data = fetch_single_paper(arxiv_id)
    if data:
        results[arxiv_id] = data
        cite = data["citation_count"]
        if cite > 0:
            print(f"  [{i+1}/{len(ids)}] {arxiv_id}: {cite} 引用")
    if i < len(ids) - 1:
        time.sleep(0.8)

print(f"\n共获取 {len(results)} 篇，有引用量: {sum(1 for v in results.values() if v['citation_count']>0)} 篇")
save_citation_snapshots(results, snapshot_date=TODAY)

# 重新评分导出
print("\n开始重新评分...")
conn2 = sqlite3.connect(DB_PATH)
conn2.row_factory = sqlite3.Row
papers = []
for row in conn2.execute("SELECT * FROM papers").fetchall():
    d = dict(row)
    d["authors"] = json.loads(d["authors"] or "[]")
    d["categories"] = json.loads(d["categories"] or "[]")
    papers.append(d)

# 合并所有引用量快照（今天的）
cit_rows = conn2.execute(
    "SELECT arxiv_id, citation_count, influential_citation_count FROM citation_snapshots WHERE snapshot_date = ?",
    (TODAY,)
).fetchall()
citation_data = {
    r["arxiv_id"]: {"citation_count": r["citation_count"], "influential_citation_count": r["influential_citation_count"], "ss_paper_id": ""}
    for r in cit_rows
}
conn2.close()
print(f"引用量快照: {len(citation_data)} 篇")

from storage.db import get_citation_history, save_daily_rankings
from processor.scorer import score_papers
from api.export import export_daily_json, export_index_json

history = get_citation_history([p["arxiv_id"] for p in papers], days_ago=7)
scored = score_papers(papers, citation_data, history)
top50 = scored[:50]
for i, p in enumerate(top50, 1):
    p["rank"] = i

# 覆盖今天的排行
conn3 = sqlite3.connect(DB_PATH)
conn3.execute("DELETE FROM daily_rankings WHERE rank_date = ?", (TODAY,))
conn3.commit()
conn3.close()

save_daily_rankings(top50, rank_date=TODAY)
export_daily_json(rank_date=TODAY)
export_index_json()

print("\n✅ Top 10 热榜:")
for p in top50[:10]:
    print(f"  #{p['rank']:>2} score={p['score']:.2f} | 引用={p['citation_count']:>5} | {p['title'][:65]}")
