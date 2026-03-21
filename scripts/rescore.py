"""
scripts/rescore.py — 用当前评分公式重新计算今日排行并导出

用法：
    python scripts/rescore.py                   # 默认今天
    python scripts/rescore.py 2026-03-21        # 指定日期
"""
import json, sqlite3, sys
from datetime import date

sys.path.insert(0, ".")

from src.storage.db import save_daily_rankings, get_citation_history
from src.processing.scorer import score_papers
from src.export.json_exporter import export_daily_json, export_index_json
from src.config import DB_PATH

TODAY = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

# 读取全部论文
rows = conn.execute("SELECT * FROM papers").fetchall()
papers = []
for row in rows:
    d = dict(row)
    d["authors"] = json.loads(d["authors"] or "[]")
    d["categories"] = json.loads(d["categories"] or "[]")
    papers.append(d)
print(f"论文总数: {len(papers)}")

# 读取引用量快照
cit_rows = conn.execute(
    "SELECT arxiv_id, citation_count, influential_citation_count FROM citation_snapshots WHERE snapshot_date = ?",
    (TODAY,)
).fetchall()
citation_data = {
    r["arxiv_id"]: {
        "citation_count": r["citation_count"],
        "influential_citation_count": r["influential_citation_count"],
        "ss_paper_id": "",
    }
    for r in cit_rows
}
print(f"引用量快照: {len(citation_data)} 篇")
conn.close()

# 获取历史引用量
history = get_citation_history([p["arxiv_id"] for p in papers], days_ago=7)

# 重新评分
scored = score_papers(papers, citation_data, history)
top50 = scored[:50]
for i, p in enumerate(top50, 1):
    p["rank"] = i

# 清除旧排行并写入新排行
conn2 = sqlite3.connect(DB_PATH)
conn2.execute("DELETE FROM daily_rankings WHERE rank_date = ?", (TODAY,))
conn2.commit()
conn2.close()

save_daily_rankings(top50, rank_date=TODAY)
export_daily_json(rank_date=TODAY)
export_index_json()

print(f"\n✅ 重新评分完成（{TODAY}）！Top 5:")
for p in top50[:5]:
    print(f"  #{p['rank']} score={p['score']:.4f} | delta={p['citation_delta_7d']} | fresh={p['score_breakdown'].get('freshness_norm',0):.1f} | {p['title'][:60]}")
