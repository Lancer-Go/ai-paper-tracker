import json
import logging
from datetime import date
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Try to import for title/abstract translations
try:
    from deep_translator import GoogleTranslator
except ImportError:
    GoogleTranslator = None

from src.config import EXPORT_DIR, TOP_N
from src.storage.db import get_top_papers

logger = logging.getLogger(__name__)

def translate_field(text: str) -> str:
    if not text or not GoogleTranslator: return ""
    try:
        if len(text) > 4000: text = text[:4000]
        return GoogleTranslator(source='auto', target='zh-CN').translate(text)
    except Exception:
        return ""

def _translate_paper(p):
    if "title_zh" not in p or not p["title_zh"]:
        p["title_zh"] = translate_field(p.get("title", ""))
    if "abstract_zh" not in p or not p["abstract_zh"]:
        p["abstract_zh"] = translate_field(p.get("abstract", ""))
    return p

def export_daily_json(rank_date: str = None, top_n: int = TOP_N) -> str:
    """
    导出某天热榜数据为 JSON 文件。
    """
    rank_date = rank_date or date.today().isoformat()

    # 确保导出目录存在
    export_dir = Path(EXPORT_DIR)
    export_dir.mkdir(parents=True, exist_ok=True)

    papers = get_top_papers(rank_date=rank_date, limit=top_n)

    # Translate missing titles and abstracts
    if GoogleTranslator:
        logger.info(f"[导出] 正在补充 {len(papers)} 篇论文的标题与摘要翻译...")
        with ThreadPoolExecutor(max_workers=8) as executor:
            papers = list(executor.map(_translate_paper, papers))

    output = {
        "date": rank_date,
        "total": len(papers),
        "generated_at": __import__("datetime").datetime.now().isoformat(),
        "papers": papers,
    }

    out_path = export_dir / f"daily_{rank_date}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)

    logger.info(f"[导出] 已导出 {len(papers)} 篇 → {out_path}")

    # 同时更新 latest.json（前端默认加载此文件）
    latest_path = export_dir / "latest.json"
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)

    logger.info(f"[导出] 已更新 latest.json")
    return str(out_path)


def export_index_json() -> str:
    """
    导出 index.json，包含所有可用日期列表，供前端日期选择器使用。

    Returns:
        导出文件路径
    """
    export_dir = Path(EXPORT_DIR)
    export_dir.mkdir(parents=True, exist_ok=True)

    # 扫描所有 daily_*.json 文件
    dates = sorted(
        [f.stem.replace("daily_", "") for f in export_dir.glob("daily_*.json")],
        reverse=True,
    )

    index = {"available_dates": dates, "latest": dates[0] if dates else ""}
    out_path = export_dir / "index.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    logger.info(f"[导出] index.json 更新，共 {len(dates)} 天数据")
    return str(out_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    path = export_daily_json()
    print(f"导出路径: {path}")
    export_index_json()
