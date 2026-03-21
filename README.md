# AI 论文热度追踪系统

> 基于 arXiv + OpenAlex，每日自动生成 AI 领域学术热榜

## 项目结构

```
ai-paper-tracker/
├── src/                           ← 后端源代码
│   ├── config.py                  # 全局配置
│   ├── sources/                   # 数据源（插件化，可扩展）
│   │   ├── base.py                #   抽象基类
│   │   └── arxiv/                 #   arXiv 数据源
│   │       ├── fetcher.py         #     论文抓取
│   │       ├── reddit_fetcher.py  #     Reddit 讨论量（可选）
│   │       └── enrichers/         #     数据丰富插件
│   │           ├── openalex.py    #       OpenAlex 引用量（免费首选）
│   │           ├── hackernews.py  #       Hacker News 社区讨论
│   │           ├── paperswithcode.py #   Papers With Code + GitHub Stars
│   │           ├── author_influence.py # 作者 h-index（OpenAlex）
│   │           └── semantic_scholar.py  #  Semantic Scholar（备用）
│   ├── processing/                # 数据处理
│   │   ├── deduper.py             #   去重
│   │   ├── scorer.py              #   热度评分
│   │   └── translator.py          #   翻译引擎
│   ├── storage/                   # 存储层
│   │   └── db.py                  #   SQLite 数据库
│   └── export/                    # 导出层
│       ├── json_exporter.py       #   JSON 数据导出
│       └── html_exporter.py       #   翻译 HTML 生成
│
├── frontend/                      ← 前端 Vite + React
│   └── src/
│       ├── App.jsx                #   主页面
│       ├── components/            #   UI 组件
│       │   ├── PaperCard.jsx      #     论文卡片
│       │   ├── CategorySidebar.jsx #    类别分布
│       │   └── CitationTrend.jsx  #     引用趋势
│       ├── hooks/                 #   自定义 Hooks
│       │   └── usePapers.js       #     数据加载
│       └── utils/                 #   工具函数
│           └── helpers.js         #     类别配置
│
├── scripts/                       ← 运维/调试脚本
├── data/                          ← 数据目录
├── docs/                          ← 业务文档
├── .github/workflows/             ← CI 自动化
│   └── daily_fetch.yml
├── run.py                         ← 主入口
├── translate_papers.py            ← 翻译入口
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
python -c "from src.storage.db import get_top_papers; [print(f'#{p[\"rank\"]} {p[\"title\"][:60]}') for p in get_top_papers(limit=10)]"
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

## 热度评分公式（8 维度 v2.1）

```
热度得分 =
    📈 引用速度(增量÷天数)  × 25%  ← 近期引文加速度
  + 📚 引用总量(对数)       × 15%  ← 累计学术积累
  + 👤 作者影响力(h-index)  × 10%  ← 顶级团队加分
  + 💻 有代码              ×  5%  ← Papers With Code
  + ⭐ GitHub Stars(对数)  × 15%  ← 工程界关注度
  + 🕐 新鲜度(指数衰减)     × 15%  ← 越新越高
  + 💬 社区讨论(HN)        × 15%  ← Hacker News 热度
```

所有指标均做 Min-Max 归一化到 [0, 100] 后加权求和。

### 数据源
| 维度 | 数据源 | 费用 |
|:---|:---|:---|
| 引用量 + 作者 h-index | OpenAlex API | 免费 |
| 代码 + Stars | Papers With Code + GitHub API | 免费 |
| 社区讨论 | Hacker News Algolia API | 免费 |
| Reddit | Reddit API | 可选（需申请） |

## GitHub Pages 自动部署

1. 在仓库 Settings → Pages 中将 Source 设为 `gh-pages` 分支
2. 推送代码后，Actions 将在每天 UTC 06:00（北京 14:00）自动运行

## AI 自动化运维指南

如果您在本地修改了代码或新增了文档，无需手动敲打任何繁琐的 Git 命令。
只需在 AI 对话框中输入：**"更新项目"** （或使用指令 **/update-project**）
AI 将自动帮您总结修改的内容，执行 add, commit 动作并 push 推送到远端云库，同时自动化触发网页版的实时更新！

<!-- PROJECT-DOCS-INDEX-START -->
---

## 📚 项目百科大纲（基于 `/update-project-readme` 自动扫描）

### 核心业务文档 (`docs/`)
| 文档 | 核心内容 |
|:---|:---|
| `01_公司与业务介绍.md` | 项目定位：面向 AI 研究者的全自动学术热度追踪平台 |
| `02_项目定义与背景信息.md` | 技术背景、行业痛点与系统设计目标 |
| `03_常用术语与名词表.md` | arXiv ID、引用速度、热度评分等核心概念定义 |
| `04_核心业务流程.md` | 完整数据管线：抓取 → 去重 → 引用量查询 → 评分 → 导出 |
| `05_数据模型与业务对象.md` | Paper、CitationSnapshot、DailyRanking 等数据结构定义 |
| `06_系统功能清单与集成.md` | 前端展示端 + 后端自动化端的模块划分与外部依赖清单 |

### 产品演进文档 (`产品文档/`)
| 文档 | 核心内容 |
|:---|:---|
| `翻译流水线升级_需求拆解.md` | 针对 HTML 保真翻译特性的需求结构剖析 |
| `翻译流水线升级_功能结构.md` | 新版双通道引擎与三态按钮交互架构 |
| `翻译流水线升级PRD.md` | 完整实现路径、流程图与数据流设计规范 |
| `翻译流水线升级PRD_质量走查报告.md` | SOP 内审环节输出的逻辑覆盖度质检单 |

### 当前已上线功能亮点
| 功能 | 描述 |
|:---|:---|
| 📊 每日热榜 | 基于引用速度、作者影响力、代码热度、社区讨论等 **8 维度**加权排名 |
| 🔍 分类筛选 | 支持 cs.AI、cs.LG、cs.CV 等多学科标签过滤 |
| 📄 结构保真翻译 | 突破纯文本限制，保留原刊 HTML 的图片、MathJax 公式及表格排版 |
| 🔘 三态翻译机制 | 核心组件升级，支持保真版(紫) / 降级版(橙) / 暂无(灰)一键智能回退分发 |
| 📈 引用趋势图 | 可视化展示 Top 10 论文的引用量变化曲线 |
| 💬 多源社区信号 | Hacker News 讨论热度（替代 Reddit） |
| 💻 代码可用性 | Papers With Code + GitHub Stars 自动采集 |
| 🤖 全自动化运维 | GitHub Actions 每天定时抓取 + 翻译 + 部署，零人工干预 |

<!-- PROJECT-DOCS-INDEX-END -->
