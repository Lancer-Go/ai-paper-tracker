"""
src/processing/translator.py — 论文翻译核心逻辑

支持两种翻译模式：
  1. arXiv HTML 保真翻译（优先） — 保留图片、公式、表格
  2. PDF 纯文本降级翻译（兜底） — 旧逻辑保留
"""

import time
import logging
import re
from pathlib import Path
from typing import Optional

import httpx
import fitz  # PyMuPDF
from bs4 import BeautifulSoup, NavigableString, Tag
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

# ── 常量 ──────────────────────────────────────────────────────
MAX_CHUNK = 4900          # Google 免费翻译单次上限约 5000 字符
DOWNLOAD_TIMEOUT = 60     # 下载 PDF/HTML 超时（秒）
RETRY_WAIT = 2            # 翻译失败后重试等待（秒）
MAX_RETRIES = 3           # 每段最大重试次数
TRANSLATE_DELAY = 0.3     # 每个翻译请求之间的友好延迟
BATCH_SEPARATOR = "\n999888777\n"  # 批量翻译分隔符（纯数字，Google 不会翻译）
BATCH_MAX_CHARS = 4500    # 单次批量翻译的最大字符数

# arXiv HTML 中需要跳过的标签（不翻译其内部文本）[R02]
SKIP_TAGS = frozenset([
    'math', 'script', 'style', 'code', 'pre', 'svg',
    'figure',  # figure 内的 figcaption 会单独处理
])

# arXiv HTML 中需要跳过的 CSS 类名
SKIP_CLASSES = frozenset([
    'ltx_Math', 'ltx_equation', 'ltx_ref', 'ltx_cite',
    'ltx_bib', 'ltx_bibliography', 'ltx_authors',
])

# 需要翻译文本的标签名
TRANSLATE_TAGS = frozenset([
    'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'li', 'td', 'th', 'caption', 'figcaption',
    'span', 'div', 'blockquote', 'dt', 'dd',
])

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


# ═══════════════════════════════════════════════════════════════
# Part 1: arXiv HTML 保真翻译
# ═══════════════════════════════════════════════════════════════

def fetch_arxiv_html(arxiv_id: str) -> Optional[str]:
    """
    探测并下载 arXiv HTML 版本。
    返回 HTML 字符串，如果不存在返回 None。
    """
    # 尝试多个可能的版本后缀
    urls_to_try = [
        f"https://arxiv.org/html/{arxiv_id}v1",
        f"https://arxiv.org/html/{arxiv_id}",
    ]
    
    headers = {"User-Agent": USER_AGENT}
    
    for url in urls_to_try:
        try:
            with httpx.Client(timeout=DOWNLOAD_TIMEOUT, follow_redirects=True) as client:
                resp = client.get(url, headers=headers)
                if resp.status_code == 200 and '<html' in resp.text[:500].lower():
                    logger.info(f"  ✓ arXiv HTML 可用: {url}")
                    return resp.text
        except Exception as e:
            logger.debug(f"  探测 {url} 失败: {e}")
    
    logger.info(f"  ↳ arXiv HTML 不可用，将降级到 PDF 翻译")
    return None


def _should_skip_node(tag: Tag) -> bool:
    """判断一个标签节点是否应该跳过翻译"""
    # 标签名在跳过列表中
    if tag.name and tag.name.lower() in SKIP_TAGS:
        return True
    
    # CSS 类名匹配
    classes = tag.get('class', [])
    if isinstance(classes, str):
        classes = classes.split()
    for cls in classes:
        if cls in SKIP_CLASSES:
            return True
    
    return False


def _is_translatable_text(text: str) -> bool:
    """判断文本是否值得翻译（排除纯数字、符号、极短文本）"""
    cleaned = text.strip()
    if len(cleaned) < 3:
        return False
    # 纯数字或纯标点
    if re.match(r'^[\d\s\.\,\;\:\-\(\)\[\]\{\}\/\\]+$', cleaned):
        return False
    # 已经是中文
    if re.search(r'[\u4e00-\u9fff]', cleaned):
        return False
    return True


def translate_html(html_content: str, arxiv_id: str) -> str:
    """
    对 arXiv HTML 进行保真翻译：
    - 修复相对路径为绝对路径（图片、CSS、JS）
    - 遍历 DOM，仅翻译文本节点
    - 保留公式、图片、表格结构
    - 为中英对照保存原文到 data-original 属性
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # ── 修复所有相对路径为绝对路径 ──
    _fix_relative_urls(soup, arxiv_id)
    
    translator = GoogleTranslator(source="en", target="zh-CN")
    
    # 收集所有需要翻译的文本节点
    text_nodes = []
    _collect_text_nodes(soup, text_nodes)
    
    logger.info(f"  → 发现 {len(text_nodes)} 个可翻译文本节点")
    
    # 批量翻译：将文本合并成 chunks 以减少 API 调用
    if text_nodes:
        _batch_translate_nodes(text_nodes, translator)
    
    # 注入自定义主题和导航栏
    _inject_theme_and_nav(soup, arxiv_id)
    
    return str(soup)


def _fix_relative_urls(soup: BeautifulSoup, arxiv_id: str):
    """
    将 arXiv HTML 中的相对路径转为绝对路径。
    处理三种情况：
    - 根路径: /static/browse/... → https://arxiv.org/static/browse/...
    - 论文相对路径: 2603.19229v1/x1.png → https://arxiv.org/html/2603.19229v1/x1.png
    - CSS url(): url(/static/...) → url(https://arxiv.org/static/...)
    """
    ARXIV_BASE = "https://arxiv.org"
    HTML_BASE = f"https://arxiv.org/html/"
    
    # 修复 img, script, link, source, video, audio 的 src 属性
    for tag in soup.find_all(src=True):
        src = tag['src']
        if src.startswith(('http://', 'https://', 'data:', '//')):
            continue  # 已经是绝对路径或 data URI
        if src.startswith('/'):
            tag['src'] = ARXIV_BASE + src
        else:
            tag['src'] = HTML_BASE + src
    
    # 修复 link 的 href 属性（CSS 等静态资源）
    for tag in soup.find_all('link', href=True):
        href = tag['href']
        if href.startswith(('http://', 'https://', 'data:', '//')):
            continue
        if href.startswith('/'):
            tag['href'] = ARXIV_BASE + href
        else:
            tag['href'] = HTML_BASE + href
    
    # 修复 a 标签指向论文内部锚点的相对链接
    for tag in soup.find_all('a', href=True):
        href = tag['href']
        if href.startswith(('#', 'http://', 'https://', 'javascript:', 'mailto:')):
            continue
        if href.startswith('/'):
            tag['href'] = ARXIV_BASE + href
        else:
            tag['href'] = HTML_BASE + href
    
    # 修复内联 style 中的 url() 引用
    for tag in soup.find_all(style=True):
        style = tag['style']
        if 'url(' in style:
            tag['style'] = re.sub(
                r'url\([\"\']?(/[^\"\')]+)[\"\']?\)',
                lambda m: f'url({ARXIV_BASE}{m.group(1)})',
                style
            )
    
    logger.info(f"  ✓ 已修复所有相对路径为 arxiv.org 绝对路径")


def _collect_text_nodes(element, result: list):
    """递归收集需要翻译的文本节点"""
    if isinstance(element, NavigableString):
        # 纯文本节点
        if isinstance(element, str) and _is_translatable_text(str(element)):
            parent = element.parent
            if parent and isinstance(parent, Tag):
                # 检查所有祖先是否需要跳过
                if not _any_ancestor_skipped(parent):
                    result.append(element)
        return
    
    if isinstance(element, Tag):
        if _should_skip_node(element):
            return  # 跳过整个子树
        
        for child in list(element.children):
            _collect_text_nodes(child, result)


def _any_ancestor_skipped(tag: Tag) -> bool:
    """检查标签的所有祖先是否有需要跳过的"""
    current = tag
    while current:
        if isinstance(current, Tag) and _should_skip_node(current):
            return True
        current = current.parent
    return False


def _batch_translate_nodes(text_nodes: list, translator):
    """批量翻译文本节点：将多个短文本合并为一次 API 调用，减少请求数 ~10x"""
    from html import escape
    total = len(text_nodes)
    translated_count = 0
    
    # 过滤有效节点
    valid_nodes = []
    for node in text_nodes:
        text = str(node).strip()
        if text and len(text) >= 3:
            valid_nodes.append((node, text))
    
    logger.info(f"    → 有效节点: {len(valid_nodes)}/{total}")
    
    # 将节点分批：每批累计字符数不超过 BATCH_MAX_CHARS
    batches = []
    current_batch = []
    current_chars = 0
    
    for node, text in valid_nodes:
        text_len = len(text) + len(BATCH_SEPARATOR)
        if current_chars + text_len > BATCH_MAX_CHARS and current_batch:
            batches.append(current_batch)
            current_batch = []
            current_chars = 0
        current_batch.append((node, text))
        current_chars += text_len
    if current_batch:
        batches.append(current_batch)
    
    logger.info(f"    → 分为 {len(batches)} 个批次（平均 {len(valid_nodes)//max(len(batches),1)} 节点/批）")
    
    for batch_idx, batch in enumerate(batches):
        # 合并批次中的所有文本
        originals = [text for _, text in batch]
        merged_text = BATCH_SEPARATOR.join(originals)
        
        # 翻译合并文本
        zh_merged = _translate_with_retry(merged_text, translator)
        
        if zh_merged:
            # 按分隔符拆分翻译结果
            # Google Translate 可能改变分隔符格式，尝试多种匹配
            zh_parts = re.split(r'\s*999888777\s*', zh_merged)
            
            if len(zh_parts) == len(originals):
                # 完美匹配：逐一替换
                for (node, original_text), zh_text in zip(batch, zh_parts):
                    zh_text = zh_text.strip()
                    if zh_text and zh_text != original_text:
                        safe_original = escape(original_text)
                        new_tag = BeautifulSoup(
                            f'<span class="translated-text">{zh_text}</span>'
                            f'<span class="original-text">{safe_original}</span>',
                            'html.parser'
                        )
                        node.replace_with(new_tag)
                        translated_count += 1
            else:
                # 分隔符被破坏：降级为逐个翻译
                logger.warning(f"    ⚠ 批次 {batch_idx+1} 分隔符失效（期望 {len(originals)} 段，得到 {len(zh_parts)} 段），降级逐个翻译")
                for node, original_text in batch:
                    zh_text = _translate_with_retry(original_text, translator)
                    if zh_text and zh_text != original_text:
                        safe_original = escape(original_text)
                        new_tag = BeautifulSoup(
                            f'<span class="translated-text">{zh_text}</span>'
                            f'<span class="original-text">{safe_original}</span>',
                            'html.parser'
                        )
                        node.replace_with(new_tag)
                        translated_count += 1
                    time.sleep(TRANSLATE_DELAY)
        
        # 友好限速
        if batch_idx < len(batches) - 1:
            time.sleep(TRANSLATE_DELAY)
        
        # 进度日志
        done = sum(len(b) for b in batches[:batch_idx+1])
        if (batch_idx + 1) % 5 == 0 or batch_idx == len(batches) - 1:
            logger.info(f"    → 翻译进度: {done}/{len(valid_nodes)} ({translated_count} 已替换)")
    
    logger.info(f"    ✓ 翻译完成: {translated_count}/{len(valid_nodes)} 个节点已替换")


def _translate_with_retry(text: str, translator, max_retries=MAX_RETRIES) -> Optional[str]:
    """带重试的翻译调用"""
    for attempt in range(max_retries):
        try:
            # 如果文本过长，分段翻译
            if len(text) > MAX_CHUNK:
                chunks = split_text(text)
                results = []
                for chunk in chunks:
                    result = translator.translate(chunk)
                    results.append(result or "")
                    time.sleep(TRANSLATE_DELAY)
                return "\n".join(results)
            else:
                return translator.translate(text) or ""
        except Exception as e:
            if attempt < max_retries - 1:
                wait = RETRY_WAIT * (2 ** attempt)  # 指数退避
                logger.warning(f"    ⚠ 翻译重试 {attempt+1}/{max_retries}，等待 {wait}s: {e}")
                time.sleep(wait)
            else:
                logger.error(f"    ✗ 翻译失败（已重试 {max_retries} 次）: {e}")
                return None


def _inject_theme_and_nav(soup: BeautifulSoup, arxiv_id: str):
    """注入白底学术主题 CSS 和顶部导航栏"""
    
    # ── 白底学术主题 CSS ──
    theme_css = """
    <style id="ai-tracker-theme">
        /* 白底学术主题覆盖 */
        body {
            background: #ffffff !important;
            color: #333333 !important;
            font-family: 'Georgia', 'Times New Roman', 'SimSun', serif !important;
            line-height: 1.8 !important;
            padding-top: 56px !important;  /* 为固定导航栏留空 */
        }
        
        /* 翻译文本样式 */
        .translated-text { }
        .original-text { display: none !important; color: #999; font-size: 0.85em; font-style: italic; }
        body.bilingual .original-text { display: block !important; margin-top: 4px; }
        
        /* 导航栏样式 */
        #ai-tracker-nav {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 48px;
            background: #1a1a2e;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px;
            z-index: 99999;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        #ai-tracker-nav a, #ai-tracker-nav button {
            color: #e0e0e0;
            text-decoration: none;
            font-size: 13px;
            padding: 6px 14px;
            border-radius: 6px;
            border: none;
            cursor: pointer;
            background: transparent;
            transition: background 0.2s;
        }
        #ai-tracker-nav a:hover, #ai-tracker-nav button:hover {
            background: rgba(255,255,255,0.1);
        }
        #ai-tracker-nav .nav-left { display: flex; align-items: center; gap: 8px; }
        #ai-tracker-nav .nav-right { display: flex; align-items: center; gap: 6px; }
        #ai-tracker-nav .toggle-btn {
            background: rgba(99,102,241,0.3);
            border: 1px solid rgba(99,102,241,0.5);
            color: #a5b4fc;
            font-weight: 500;
        }
        #ai-tracker-nav .toggle-btn.active {
            background: rgba(99,102,241,0.6);
            color: #fff;
        }
        
        /* 降级 Alert */
        .ai-tracker-degraded-alert {
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffc107;
            border-radius: 8px;
            padding: 12px 20px;
            margin: 16px 20px;
            font-size: 14px;
            line-height: 1.5;
        }
        
        /* 图片自适应 */
        img { max-width: 100%; height: auto; }
        
        /* 表格样式增强 */
        table { border-collapse: collapse; max-width: 100%; overflow-x: auto; display: block; }
        td, th { padding: 8px 12px; border: 1px solid #ddd; }
    </style>
    """
    
    # ── 顶部导航栏 HTML ──
    nav_html = f"""
    <div id="ai-tracker-nav">
        <div class="nav-left">
            <a href="javascript:history.back()" title="返回热榜">← 返回热榜</a>
        </div>
        <div class="nav-right">
            <button class="toggle-btn" id="bilingualToggle" onclick="toggleBilingual()">
                🔄 中英对照
            </button>
            <a href="https://arxiv.org/abs/{arxiv_id}" target="_blank">🔗 arXiv 原文</a>
            <a href="https://arxiv.org/pdf/{arxiv_id}" target="_blank">📥 PDF 下载</a>
        </div>
    </div>
    """
    
    # ── 中英对照切换 JS ──
    toggle_js = """
    <script id="ai-tracker-toggle">
    function toggleBilingual() {
        document.body.classList.toggle('bilingual');
        var btn = document.getElementById('bilingualToggle');
        if (document.body.classList.contains('bilingual')) {
            btn.classList.add('active');
            btn.textContent = '🔄 仅中文';
        } else {
            btn.classList.remove('active');
            btn.textContent = '🔄 中英对照';
        }
    }
    </script>
    """
    
    # 注入到 HTML 中
    head = soup.find('head')
    if head:
        head.append(BeautifulSoup(theme_css, 'html.parser'))
    else:
        soup.insert(0, BeautifulSoup(f'<head>{theme_css}</head>', 'html.parser'))
    
    body = soup.find('body')
    if body:
        body.insert(0, BeautifulSoup(nav_html, 'html.parser'))
        body.append(BeautifulSoup(toggle_js, 'html.parser'))
    

def inject_degraded_alert(soup: BeautifulSoup):
    """为 PDF 降级版本注入警告 Alert [R04]"""
    alert_html = """
    <div class="ai-tracker-degraded-alert">
        ⚠️ <strong>注</strong>：本文无 arXiv 原生 HTML 版本，当前为基于 PDF 提取的纯文本翻译版，可能会丢失部分图表和排版。
        建议查看 <a href="javascript:void(0)" onclick="window.open(document.querySelector('#ai-tracker-nav a[href*=pdf]').href)">原版 PDF</a> 获取完整内容。
    </div>
    """
    nav = soup.find(id='ai-tracker-nav')
    if nav:
        nav.insert_after(BeautifulSoup(alert_html, 'html.parser'))


# ═══════════════════════════════════════════════════════════════
# Part 2: PDF 降级翻译（保留原有逻辑）
# ═══════════════════════════════════════════════════════════════

def download_pdf(url: str, dest: Path) -> bool:
    """下载 PDF 到本地路径，成功返回 True"""
    if dest.exists() and dest.stat().st_size > 1000:
        logger.info(f"  ↳ PDF 已缓存: {dest.name}")
        return True
    try:
        headers = {"User-Agent": USER_AGENT}
        with httpx.Client(timeout=DOWNLOAD_TIMEOUT, follow_redirects=True) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            dest.write_bytes(resp.content)
        logger.info(f"  ↳ 下载完成: {dest.name} ({len(resp.content) / 1024:.0f} KB)")
        return True
    except Exception as e:
        logger.warning(f"  ✗ 下载失败 {url}: {e}")
        return False


def extract_text_by_page(pdf_path: Path) -> list[str]:
    """使用 PyMuPDF 提取 PDF 每页的文本内容"""
    pages = []
    try:
        doc = fitz.open(str(pdf_path))
        for page in doc:
            text = page.get_text("text")
            if text.strip():
                pages.append(text.strip())
        doc.close()
    except Exception as e:
        logger.warning(f"  ✗ PDF 解析失败: {e}")
    return pages


def split_text(text: str, max_len: int = MAX_CHUNK) -> list[str]:
    """将长文本按段落边界拆分为不超过 max_len 的块"""
    paragraphs = text.split("\n")
    chunks, current = [], ""
    for para in paragraphs:
        if len(current) + len(para) + 1 > max_len:
            if current:
                chunks.append(current)
            while len(para) > max_len:
                chunks.append(para[:max_len])
                para = para[max_len:]
            current = para
        else:
            current = current + "\n" + para if current else para
    if current:
        chunks.append(current)
    return chunks


def translate_text(text: str) -> str:
    """使用 Google 免费翻译将英文文本翻译为中文，自动分块"""
    if not text.strip():
        return ""
    translator = GoogleTranslator(source="en", target="zh-CN")
    chunks = split_text(text)
    translated_parts = []
    for i, chunk in enumerate(chunks):
        for attempt in range(MAX_RETRIES):
            try:
                result = translator.translate(chunk)
                translated_parts.append(result or "")
                break
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_WAIT * (attempt + 1))
                else:
                    logger.warning(f"    ✗ 翻译块 {i+1}/{len(chunks)} 失败: {e}")
                    translated_parts.append(f"[翻译失败] {chunk[:200]}...")
        time.sleep(TRANSLATE_DELAY)
    return "\n".join(translated_parts)
