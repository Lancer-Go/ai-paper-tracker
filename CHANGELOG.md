# 📋 Changelog — AI 论文热度追踪平台

所有项目功能层面的版本变更记录。格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/)。

---

## [v2.2.1] - 2026-03-21
### 修复
- 🐛 **图片不显示**：新增 `_fix_relative_urls()` 将 arXiv 相对路径转为绝对 URL
- 🐛 **中英对照切换无效**：移除 inline `style="display:none"`，改用 CSS `!important` 类规则控制可见性
- 🐛 **GitHub Actions 翻译超时**：批量合并翻译（~10 节点/批，API 调用减少 ~10x）+ 45 分钟时间预算自动停止

---

## [v2.2.0] - 2026-03-21
### 新增
- 🔬 **arXiv HTML 保真翻译**：优先抓取 arXiv 原生 HTML，保留图片、公式 (MathJax)、表格结构进行翻译
  - 白底学术主题 CSS 注入，阅读体验大幅提升
  - 顶部导航栏：返回热榜 / 中英对照 / arXiv 原文 / PDF 下载
  - `🔄 中英对照` 一键切换开关
- 📝 **PDF 降级翻译**：无 HTML 版本时自动回退 PDF 纯文本翻译，顶部醒目 Alert 提示
- 🎨 **前端三态翻译按钮**：
  - 🟣 紫色 `🔬 保真翻译` — HTML 保真版
  - 🟠 橙色 `📝 简版翻译` — PDF 降级版
  - ⚪ 灰色 `暂无翻译` — 未翻译
- 🛡️ **连续失败熔断**：连续 5 篇翻译失败自动终止流水线
- ⏭️ **增量翻译缓存**：已翻译的论文自动跳过，中间索引实时保存
- 📄 **产品文档体系**：完成翻译流水线升级的需求拆解、功能结构、PRD、质量走查全套文档

### 变更
- `translator.py` — 重写为 HTML 优先 + PDF 降级双通道引擎
- `html_exporter.py` — 重写 PDF 降级版使用白底主题，与保真版视觉一致
- `translate_papers.py` — 升级为 HTML-first 流水线入口，含熔断和增量缓存
- `usePapers.js` — 暴露完整翻译索引对象（含 `type` 字段）
- `PaperCard.jsx` / `App.jsx` — 三态翻译按钮

---

## [v2.1.0] - 2026-03-21
### 新增
- 📊 **8 维度热度评分体系**：全面升级评分算法，从 3 维度扩展到 7 个核心维度
  - 📈 **引用速度**（Citation Velocity）：增量 ÷ 天数，对新论文更友好
  - 👤 **作者影响力**：通过 OpenAlex 查询作者 h-index，顶级团队论文获得加分
  - 💻 **代码可用性**：Papers With Code API，有开源代码的论文排名更靠前
  - ⭐ **GitHub Stars**：代码仓库星标数，反映工程界关注度
  - 💬 **社区讨论**：Hacker News Algolia API 替代不可用的 Reddit
  - 🕐 **指数衰减新鲜度**：从线性改为 `e^(-t/14)` 更符合实际关注曲线
- 🔌 **3 个新 Enricher 模块**：
  - `src/sources/arxiv/enrichers/hackernews.py` — HN Algolia 搜索
  - `src/sources/arxiv/enrichers/paperswithcode.py` — PwC + GitHub Stars
  - `src/sources/arxiv/enrichers/author_influence.py` — OpenAlex Author h-index
- 🎨 前端论文卡片新增 7 维度评分拆解条 + GitHub 按钮 + 作者/HN/代码徽标

### 修复
- 🐛 **翻译按钮不可点击**：`usePapers.js` 解析 `index.json` 格式不匹配（前端期望数组，后端写字典）
- 🐛 **CI 数据文件被覆盖**：`keep_files: false` 导致 push 触发的构建清除翻译数据 → 改为 `true`

---

## [v2.0.0] - 2026-03-21
### 重构
- 🏗️ **项目架构重构**：从扁平脚本升级为分层模块化架构
  - 后端代码统一移入 `src/` 目录，按职责分层（`sources/`、`processing/`、`storage/`、`export/`）
  - 引入**数据源插件化设计**（`src/sources/base.py` 抽象基类），为未来添加新资讯源预留扩展点
  - 清理根目录散落脚本 → 移入 `scripts/`，删除临时测试文件
  - 移除所有 `sys.path.insert` hack，改为标准 `src.` 包导入
- 📄 **翻译管线拆分**：`translate_papers.py` 核心逻辑提取到 `src/processing/translator.py` + `src/export/html_exporter.py`
- ⚛️ **前端组件化**：488 行单文件 `App.jsx` 拆分为 `PaperCard`、`CategorySidebar`、`CitationTrend` 组件 + `usePapers` Hook

### 修复
- 🐛 修复 GitHub Actions 30 分钟超时导致每日任务失败的问题（job timeout 30→90 分钟）

---

## [v1.2.0] - 2026-03-21
### 新增
- 📄 **PDF 全文中文翻译流水线**：每日自动下载 Top 50 论文 PDF，通过 PyMuPDF 提取文本 + Google Translate 翻译，生成精美深色主题 HTML 页面
- 🔘 前端新增「中文翻译」按钮，可直接跳转至预翻译的全中文论文页面
- 📦 新增 `translate_papers.py` 翻译引擎脚本

### 变更
- CI 流水线新增翻译工序（`daily_fetch.yml`），翻译结果随页面一同部署
- 翻译按钮从 Google Translate 网页跳转 → Kimi AI 伴读 → 最终改为静态预翻译直链
- 翻译数量从 Top 10 调整为全部 50 篇（超时从 20min 增至 60min）
- CI 中论文抓取和数据提交步骤在代码 push 触发时自动跳过，仅定时/手动触发时执行

### 修复
- 修复翻译按钮指向 arXiv 摘要页（`/abs/`）而非全文页（`/html/`）的问题

### 依赖
- 新增 `PyMuPDF>=1.25.0`
- 新增 `deep-translator>=1.11.0`

---

## [v1.1.0] - 2026-03-20
### 新增
- 🌐 前端 React + Vite 可视化热榜页面
- 📊 多维度热度评分算法（引用增量、跨学科广度、新鲜度加权）
- 🔍 分类筛选功能（cs.AI、cs.LG、cs.CV 等多学科标签过滤）
- 📈 Top 10 引用趋势图可视化
- 🤖 GitHub Actions 每日自动抓取 + 部署到 GitHub Pages
- 🗃️ SQLite 本地数据持久化 + JSON 导出

### 数据源
- arXiv API 论文数据
- OpenAlex API 引用量数据（替换 Semantic Scholar）
- Reddit 社区讨论量（可选）
