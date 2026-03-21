# 📋 Changelog — AI 论文热度追踪平台

所有项目功能层面的版本变更记录。格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/)。

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
