import { useState, useMemo } from 'react'
import { Search } from 'lucide-react'
import { usePapers } from './hooks/usePapers'
import { CAT_CONFIG, CAT_ALL } from './utils/helpers'
import PaperCard from './components/PaperCard'
import CategorySidebar from './components/CategorySidebar'
import CitationTrend from './components/CitationTrend'
import './index.css'

export default function App() {
  const {
    papers, availableDates, selectedDate, setSelectedDate,
    loading, error, dataInfo, translationIndex,
  } = usePapers()

  const [search, setSearch] = useState('')
  const [catFilter, setCatFilter] = useState(CAT_ALL)

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
                    <PaperCard key={paper.arxiv_id} paper={paper} rank={paper.rank || i + 1} translationIndex={translationIndex} />
                  ))}
                </div>
              )}
            </div>
            {/* Sidebar */}
            <aside className="sidebar">
              <CategorySidebar papers={filtered} />
              <CitationTrend papers={filtered} />
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
