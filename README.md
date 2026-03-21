# AI 论文热度追踪系统

> 基于 arXiv + Semantic Scholar，每日自动生成 AI 领域学术热榜

## 项目结构

```
ai-paper-tracker/
├── crawler/
│   ├── arxiv_fetcher.py       # arXiv 原始论文抓取
│   ├── semantic_scholar.py    # Semantic Scholar 引用量查询
│   └── reddit_fetcher.py      # Reddit 社区信号（可选）
├── processor/
│   ├── deduper.py             # 去重
│   └── scorer.py              # 热度评分（引用增量 × 0.5 + 总量 × 0.3 + Reddit × 0.2）
├── storage/
│   └── db.py                  # SQLite 数据库
├── api/
│   └── export.py              # 导出每日 JSON
├── frontend/                  # Vite + React 可视化网页
├── .github/workflows/
│   └── daily_fetch.yml        # GitHub Actions 定时任务
├── config.py                  # 全局配置
├── run.py                     # 主入口
└── requirements.txt
```

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 初始化数据库并采集（首次运行）
```bash
python run.py
```

### 3. 查看结果（命令行）
```bash
python -c "from storage.db import get_top_papers; [print(f'#{p[\"rank\"]} {p[\"title\"][:60]}') for p in get_top_papers(limit=10)]"
```

### 4. 启动前端
```bash
cd frontend
npm run dev
# 打开 http://localhost:5173
```

## 参数说明

```bash
python run.py --help

# 常用选项：
python run.py                          # 正常运行（今天）
python run.py --dry-run                # 仅抓取&打印，不写数据库
python run.py --date 2026-03-20        # 为指定日期运行
python run.py --skip-reddit            # 跳过 Reddit 采集
python run.py --days-back 14           # 往回看 14 天的论文
python run.py --top-n 100              # 热榜展示 Top 100
```

## 环境变量（可选，可提高 API 配额）

| 变量名 | 说明 |
|--------|------|
| `SEMANTIC_SCHOLAR_API_KEY` | Semantic Scholar API Key（免费申请，提高请求限额） |
| `REDDIT_CLIENT_ID` | Reddit App Client ID（开启社区信号） |
| `REDDIT_CLIENT_SECRET` | Reddit App Client Secret |

## 热度评分公式

```
热度得分 =
    引用量增量(近7日) × 0.50 ← 近期学术影响力增速
  + 引用总量(对数)    × 0.30 ← 累计学术积累
  + Reddit 讨论量    × 0.20 ← 社区关注度（可选）
```

所有指标均做 Min-Max 归一化到 [0, 100] 后加权求和。

## GitHub Pages 自动部署

1. 在仓库 Settings → Pages 中将 Source 设为 `gh-pages` 分支
2. 推送代码后，Actions 将在每天 UTC 06:00（北京 14:00）自动运行

## AI 自动化运维指南

如果您在本地修改了代码或新增了文档，无需手动敲打任何繁琐的 Git 命令。
只需在 AI 对话框中输入：**“更新项目”** （或使用指令 **/update-project**）
AI 将自动帮您总结修改的内容，执行 add, commit 动作并 push 推送到远端云库，同时自动化触发网页版的实时更新！
