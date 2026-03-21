import { useState, useEffect, useMemo } from 'react'
import { Search, BookOpen, TrendingUp, Calendar, ExternalLink, FileText, Layers } from 'lucide-react'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis } from 'recharts'
import './index.css'

// ── 类别配置 ───────────────────────────────────────────
const CAT_CONFIG = {
  'cs.AI':    { label: 'cs.AI',    color: '#818cf8', css: 'cat-cs-AI'   },
  'cs.LG':    { label: 'cs.LG',    color: '#22d3ee', css: 'cat-cs-LG'   },
  'cs.CV':    { label: 'cs.CV',    color: '#f472b6', css: 'cat-cs-CV'   },
  'cs.CL':    { label: 'cs.CL',    color: '#10b981', css: 'cat-cs-CL'   },
  'cs.RO':    { label: 'cs.RO',    color: '#f59e0b', css: 'cat-cs-RO'   },
  'cs.NE':    { label: 'cs.NE',    color: '#ef4444', css: 'cat-cs-NE'   },
  'stat.ML':  { label: 'stat.ML',  color: '#a855f7', css: 'cat-stat-ML' },
  'q-bio.NC': { label: '🧠 Neuro', color: '#06b6d4', css: 'cat-qbio-NC' },
  'econ.GN':  { label: '🧪 Psych', color: '#d97706', css: 'cat-econ-GN' },
}
const CAT_ALL = 'all'

function getCatCss(cat) {
  return (CAT_CONFIG[cat] || {}).css || 'cat-default'
}

function getCatColor(cat) {
  return (CAT_CONFIG[cat] || {}).color || '#94a3b8'
}

// ── 自定义 Tooltip ──────────────────────────────────────
function CustomTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    return (
      <div style={{ background: '#1a2235', border: '1px solid #2a3650', borderRadius: 8, padding: '8px 12px', fontSize: 12 }}>
        <p style={{ color: '#e2e8f0', fontWeight: 600 }}>{label}</p>
        {payload.map((p, i) => (
          <p key={i} style={{ color: p.color }}>{p.name}: {p.value}</p>
        ))}
      </div>
    )
  }
  return null
}

// ── 评分条 ──────────────────────────────────────────────
function ScoreBar({ value, color, label }) {
  return (
    <div className="breakdown-item">
      <div className="breakdown-header">
        <span className="breakdown-label">{label}</span>
        <span className="breakdown-value">{(value || 0).toFixed(1)}</span>
      </div>
      <div className="breakdown-bar">
        <div className="breakdown-fill" style={{ width: `${value || 0}%`, background: color }} />
      </div>
    </div>
  )
}

// ── 类别标签 ─────────────────────────────────────────────
function CatTag({ cat }) {
  const cfg = CAT_CONFIG[cat]
  return <span className={`category-tag ${getCatCss(cat)}`}>{cfg ? cfg.label : cat}</span>
}

// ── 论文卡片 ─────────────────────────────────────────────
function PaperCard({ paper, rank, translatedIds }) {
  const [expanded, setExpanded] = useState(false)
  const hasTranslation = translatedIds.has(paper.arxiv_id.replace('/', '_'))

  const rankClass = rank === 1 ? 'rank-1' : rank === 2 ? 'rank-2' : rank === 3 ? 'rank-3' : 'rank-other'

  return (
    <div
      className={`paper-card ${expanded ? 'expanded' : ''}`}
      onClick={() => setExpanded(e => !e)}
    >
      <div className="card-header">
        {/* Rank */}
        <div className="rank-badge">
          <span className={`rank-number ${rankClass}`}>
            {rank <= 3 ? ['🥇','🥈','🥉'][rank - 1] : `#${rank}`}
          </span>
        </div>

        {/* Main */}
        <div className="card-main">
          <div className="paper-title">{paper.title}</div>
          <div className="paper-meta">
            <CatTag cat={paper.primary_category} />
            <span className="paper-date">{paper.published_date}</span>
          </div>
          <div className="metrics-row">
            <div className="metric">
              <span className="metric-icon">📚</span>
              <span className="metric-value">{(paper.citation_count || 0).toLocaleString()}</span>
              <span style={{ fontSize: '0.72rem', color: '#94a3b8' }}>引用</span>
              {paper.citation_delta_7d > 0 && (
                <span className="metric-delta">+{paper.citation_delta_7d}</span>
              )}
            </div>
            {paper.reddit_score > 0 && (
              <div className="metric">
                <span className="metric-icon">💬</span>
                <span className="metric-value">{paper.reddit_score}</span>
                <span style={{ fontSize: '0.72rem', color: '#94a3b8' }}>讨论</span>
              </div>
            )}
          </div>
        </div>

        {/* Score */}
        <div className="score-section">
          <div className="score-value">{(paper.score * 100).toFixed(1)}</div>
          <div className="score-label">热度分</div>
        </div>
      </div>

      {/* Expanded */}
      {expanded && (
        <div className="expanded-content" onClick={e => e.stopPropagation()}>
          {paper.abstract && (
            <p className="abstract-text">{paper.abstract}</p>
          )}
          {paper.authors && paper.authors.length > 0 && (
            <p className="authors-text">
              ✍️ {paper.authors.slice(0, 5).join(', ')}{paper.authors.length > 5 ? ` 等 ${paper.authors.length} 人` : ''}
            </p>
          )}
          <div className="action-btns">
            <a
              className="action-btn action-btn-primary"
              href={paper.arxiv_url}
              target="_blank"
              rel="noopener noreferrer"
            >
              <ExternalLink size={13} /> arXiv
            </a>
            <a
              className="action-btn action-btn-secondary"
              href={paper.pdf_url}
              target="_blank"
              rel="noopener noreferrer"
            >
              <FileText size={13} /> PDF
            </a>
            {hasTranslation ? (
              <a
                className="action-btn action-btn-secondary"
                style={{ background: 'rgba(168, 85, 247, 0.1)', color: '#a855f7', borderColor: 'rgba(168, 85, 247, 0.3)' }}
                href={`data/translations/${paper.arxiv_id.replace('/', '_')}.html`}
                target="_blank"
                rel="noopener noreferrer"
                title="阅读由系统自动翻译的全中文论文"
              >
                <BookOpen size={13} /> 中文翻译
              </a>
            ) : (
              <span
                className="action-btn action-btn-secondary"
                style={{ background: 'rgba(100, 116, 139, 0.08)', color: '#475569', borderColor: 'rgba(100, 116, 139, 0.15)', cursor: 'not-allowed', opacity: 0.5 }}
                title="翻译暂未生成，系统每天 14:00 自动翻译"
              >
                <BookOpen size={13} /> 中文翻译
              </span>
            )}
          </div>

          {/* 评分拆解 */}
          {paper.score_breakdown && (
            <div style={{ marginTop: 14, padding: '12px', background: 'rgba(0,0,0,0.2)', borderRadius: 8 }}>
              <div style={{ fontSize: '0.72rem', color: '#4a5568', marginBottom: 8, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>评分拆解</div>
              <div className="breakdown-list">
                <ScoreBar value={paper.score_breakdown.citation_delta_norm} color="#6366f1" label="引用增量 (7日)" />
                <ScoreBar value={paper.score_breakdown.citation_total_norm} color="#22d3ee" label="引用总量" />
                <ScoreBar value={paper.score_breakdown.reddit_norm} color="#f472b6" label="社区讨论" />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ── 侧边栏：类别分布 ────────────────────────────────────
function CategorySidebar({ papers }) {
  const catStats = useMemo(() => {
    const counts = {}
    papers.forEach(p => {
      const cat = p.primary_category || 'other'
      counts[cat] = (counts[cat] || 0) + 1
    })
    return Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 7)
  }, [papers])

  const max = catStats[0]?.[1] || 1

  const pieData = catStats.map(([cat, count]) => ({
    name: cat, value: count, color: getCatColor(cat)
  }))

  return (
    <div className="sidebar-card">
      <div className="sidebar-title"><Layers size={14} /> 领域分布</div>

      {/* Pie 图 */}
      {pieData.length > 0 && (
        <div className="chart-wrapper" style={{ height: 160, marginBottom: 16 }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={45}
                outerRadius={72}
                paddingAngle={2}
                dataKey="value"
              >
                {pieData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Bar list */}
      <div className="cat-bar-list">
        {catStats.map(([cat, count]) => (
          <div key={cat} className="cat-bar-item">
            <div className="cat-bar-header">
              <span className="cat-bar-name">{cat}</span>
              <span className="cat-bar-count">{count}</span>
            </div>
            <div className="cat-bar-track">
              <div
                className="cat-bar-fill"
                style={{ width: `${(count / max) * 100}%`, background: getCatColor(cat) }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// ── 侧边栏：引用趋势 ─────────────────────────────────────
function CitationTrendSidebar({ papers }) {
  const data = useMemo(() => {
    return papers
      .slice(0, 10)
      .map(p => ({
        name: p.arxiv_id,
        shortTitle: p.title.slice(0, 20) + '…',
        citations: p.citation_count || 0,
        delta: p.citation_delta_7d || 0,
      }))
  }, [papers])

  return (
    <div className="sidebar-card">
      <div className="sidebar-title"><TrendingUp size={14} /> Top 10 引用量</div>
      <div className="chart-wrapper" style={{ height: 200 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ left: 0, right: 20, top: 0, bottom: 0 }}>
            <XAxis type="number" hide />
            <YAxis
              type="category"
              dataKey="name"
              width={70}
              tick={{ fontSize: 10, fill: '#4a5568' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="citations" name="引用量" fill="#6366f1" radius={[0, 3, 3, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

// ── 主 App ───────────────────────────────────────────────
export default function App() {
  const [papers, setPapers] = useState([])
  const [availableDates, setAvailableDates] = useState([])
  const [selectedDate, setSelectedDate] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [catFilter, setCatFilter] = useState(CAT_ALL)
  const [dataInfo, setDataInfo] = useState({ date: '', total: 0 })
  const [translatedIds, setTranslatedIds] = useState(new Set())

  // 加载日期列表
  useEffect(() => {
    const base = import.meta.env.BASE_URL || '/'
    fetch(`${base}data/exports/index.json`)
      .then(r => r.json())
      .then(data => {
        setAvailableDates(data.available_dates || [])
        setSelectedDate(data.latest || '')
      })
      .catch(() => {
        // 没有 index.json 时默认加载 latest.json
        setSelectedDate('latest')
      })
  }, [])

  // 加载翻译索引
  useEffect(() => {
    const base = import.meta.env.BASE_URL || '/'
    fetch(`${base}data/translations/index.json`)
      .then(r => r.ok ? r.json() : { translations: [] })
      .then(data => {
        const ids = new Set((data.translations || []).map(t => t.arxiv_id.replace('/', '_')))
        setTranslatedIds(ids)
      })
      .catch(() => setTranslatedIds(new Set()))
  }, [])

  // 加载论文数据
  useEffect(() => {
    if (!selectedDate) return
    setLoading(true)
    setError('')

    const base = import.meta.env.BASE_URL || '/'
    const url = selectedDate === 'latest'
      ? `${base}data/exports/latest.json`
      : `${base}data/exports/daily_${selectedDate}.json`

    fetch(url)
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json()
      })
      .then(data => {
        setPapers(data.papers || [])
        setDataInfo({ date: data.date || selectedDate, total: data.total || 0 })
        setLoading(false)
      })
      .catch(err => {
        setError('暂无数据，请先运行 python run.py 生成今日热榜')
        setLoading(false)
      })
  }, [selectedDate])

  // 过滤
  const filtered = useMemo(() => {
    return papers.filter(p => {
      const matchCat = catFilter === CAT_ALL || p.primary_category === catFilter
      const q = search.toLowerCase()
      const matchSearch = !q || p.title.toLowerCase().includes(q) || (p.abstract || '').toLowerCase().includes(q)
      return matchCat && matchSearch
    })
  }, [papers, catFilter, search])

  const totalCitations = papers.reduce((s, p) => s + (p.citation_count || 0), 0)

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-logo">
          <div className="header-logo-icon">🤖</div>
          AI 论文热榜
        </div>
        <div className="header-meta">
          {dataInfo.date && <span>📅 {dataInfo.date}</span>}
          <span className="header-badge">每日更新</span>
        </div>
      </header>

      {/* Hero */}
      <section className="hero">
        <h1 className="hero-title">AI 学术热度追踪</h1>
        <p className="hero-subtitle">基于学术引用量，每日自动聚合 arXiv 最新 AI 论文热榜</p>

        {!loading && papers.length > 0 && (
          <div className="stats-bar">
            <div className="stat-item">
              <div className="stat-value">{papers.length}</div>
              <div className="stat-label">今日论文</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{totalCitations.toLocaleString()}</div>
              <div className="stat-label">总引用量</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{Object.keys(CAT_CONFIG).length}</div>
              <div className="stat-label">覆盖领域</div>
            </div>
          </div>
        )}
      </section>

      {/* Controls */}
      <div className="controls">
        <div className="search-box">
          <Search size={14} className="search-icon" />
          <input
            placeholder="搜索论文标题、关键词..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>

        <div className="filter-group">
          <button
            className={`filter-btn ${catFilter === CAT_ALL ? 'active' : ''}`}
            onClick={() => setCatFilter(CAT_ALL)}
          >全部</button>
          {Object.keys(CAT_CONFIG).map(cat => (
            <button
              key={cat}
              className={`filter-btn ${catFilter === cat ? 'active' : ''}`}
              onClick={() => setCatFilter(cat)}
            >{cat}</button>
          ))}
        </div>

        {availableDates.length > 1 && (
          <select
            className="date-select"
            value={selectedDate}
            onChange={e => setSelectedDate(e.target.value)}
          >
            {availableDates.map(d => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        )}
      </div>

      {/* Main */}
      <main className="main-content">
        {loading ? (
          <div className="loading-state">
            <div className="spinner" />
            <p>正在加载热榜数据...</p>
          </div>
        ) : error ? (
          <div className="empty-state">
            <div className="empty-icon">📭</div>
            <p style={{ fontWeight: 600, marginBottom: 8 }}>{error}</p>
            <p style={{ fontSize: '0.85rem', color: '#4a5568' }}>
              运行 <code style={{ background: '#1a2235', padding: '2px 8px', borderRadius: 4 }}>python run.py</code> 开始采集
            </p>
          </div>
        ) : (
          <div className="layout-grid">
            {/* Paper List */}
            <div>
              {filtered.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">🔍</div>
                  <p>没有找到匹配的论文</p>
                </div>
              ) : (
                <div className="paper-list">
                  {filtered.map((paper, i) => (
                    <PaperCard key={paper.arxiv_id} paper={paper} rank={paper.rank || i + 1} translatedIds={translatedIds} />
                  ))}
                </div>
              )}
            </div>
            {/* Sidebar */}
            <aside className="sidebar">
              <CategorySidebar papers={filtered} />
              <CitationTrendSidebar papers={filtered} />
            </aside>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="footer">
        数据来源：arXiv API · Semantic Scholar API &nbsp;|&nbsp; 每日 UTC 06:00 自动更新
      </footer>
    </div>
  )
}
