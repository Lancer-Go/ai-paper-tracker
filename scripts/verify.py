"""
scripts/verify.py — 用少量论文快速验证 OpenAlex 端到端流程

用法：
    python scripts/verify.py                # 默认今天
    python scripts/verify.py 2026-03-21     # 指定日期
"""
import sys, json, sqlite3, logging
from datetime import date

sys.path.insert(0, ".")
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

from src.config import DB_PATH

TODAY = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()

# 1. 从数据库取最新 30 篇论文
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
rows = conn.execute(
    "SELECT * FROM papers ORDER BY published_date DESC LIMIT 30"
).fetchall()
papers = []
for row in rows:
    d = dict(row)
    d["authors"] = json.loads(d["authors"] or "[]")
    d["categories"] = json.loads(d["categories"] or "[]")
    papers.append(d)
print(f"取 {len(papers)} 篇最新论文进行测试")

# 读取所有论文（用于评分）
all_rows = conn.execute("SELECT * FROM papers").fetchall()
all_papers = []
for row in all_rows:
    d = dict(row)
    d["authors"] = json.loads(d["authors"] or "[]")
    d["categories"] = json.loads(d["categories"] or "[]")
    all_papers.append(d)

# 读取已有快照
cit_rows = conn.execute(
    "SELECT arxiv_id, citation_count FROM citation_snapshots WHERE snapshot_date = ?",
    (TODAY,)
).fetchall()
existing_cit = {r["arxiv_id"]: r["citation_count"] for r in cit_rows}
conn.close()
print(f"现有引用量快照: {len(existing_cit)} 篇")

# 2. 用 OpenAlex 查这 30 篇的引用量
from src.sources.arxiv.enrichers.openalex import fetch_batch_papers
from src.storage.db import save_citation_snapshots

new_cit = fetch_batch_papers([p["arxiv_id"] for p in papers])
print(f"OpenAlex 返回: {len(new_cit)} 篇，有引用: {sum(1 for v in new_cit.values() if v['citation_count']>0)} 篇")

# 合并到数据库
if new_cit:
    save_citation_snapshots(new_cit, snapshot_date=TODAY)

# 3. 重新评分（用所有论文 + 合并的引用量数据）
conn2 = sqlite3.connect(DB_PATH)
conn2.row_factory = sqlite3.Row
cit_all = conn2.execute(
    "SELECT arxiv_id, citation_count, influential_citation_count FROM citation_snapshots WHERE snapshot_date = ?",
    (TODAY,)
).fetchall()
citation_data = {
    r["arxiv_id"]: {"citation_count": r["citation_count"], "influential_citation_count": r["influential_citation_count"], "ss_paper_id": ""}
    for r in cit_all
}
conn2.close()
print(f"总引用量快照: {len(citation_data)} 篇（{sum(1 for v in citation_data.values() if v['citation_count']>0)} 篇有引用）")

from src.storage.db import get_citation_history, save_daily_rankings
from src.processing.scorer import score_papers
from src.export.json_exporter import export_daily_json, export_index_json

history = get_citation_history([p["arxiv_id"] for p in all_papers], days_ago=7)
scored = score_papers(all_papers, citation_data, history)
top50 = scored[:50]
for i, p in enumerate(top50, 1):
    p["rank"] = i

# 覆盖排行
conn3 = sqlite3.connect(DB_PATH)
conn3.execute("DELETE FROM daily_rankings WHERE rank_date = ?", (TODAY,))
conn3.commit()
conn3.close()

save_daily_rankings(top50, rank_date=TODAY)
export_daily_json(rank_date=TODAY)
export_index_json()

print(f"\n✅ Top 10 热榜 ({TODAY}):")
for p in top50[:10]:
    print(f"  #{p['rank']:>2} score={p['score']:.2f} | 引用={p['citation_count']:>5} | {p['title'][:65]}")
