import { useState, useMemo } from 'react'
import { Search } from 'lucide-react'
import { usePapers } from './hooks/usePapers'
import { CAT_CONFIG, CAT_ALL } from './utils/helpers'
import PaperCard from './components/PaperCard'
import CategorySidebar from './components/CategorySidebar'
import CitationTrend from './components/CitationTrend'
import { I18nToggle } from './components/I18nToggle'
import { AnalyticsWidget } from './components/AnalyticsWidget'
import { useI18n } from './contexts/I18nContext'
import './index.css'

export default function App() {
  const {
    papers, availableDates, selectedDate, setSelectedDate,
    loading, error, dataInfo, translationIndex,
  } = usePapers()
  
  const { t } = useI18n()

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
      <header className="header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div className="header-logo">
          <div className="header-logo-icon">🤖</div>
          {t('appTitle')}
        </div>
        <div className="header-meta" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          {dataInfo.date && <span>📅 {dataInfo.date}</span>}
          <span className="header-badge">{t('dailyUpdate')}</span>
          <I18nToggle />
        </div>
      </header>

      {/* Hero */}
      <section className="hero">
        <h1 className="hero-title">{t('heroTitle')}</h1>
        <p className="hero-subtitle">{t('heroSub')}</p>

        {!loading && papers.length > 0 && (
          <div className="stats-bar">
            <div className="stat-item">
              <div className="stat-value">{papers.length}</div>
              <div className="stat-label">{t('statToday')}</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{totalCitations.toLocaleString()}</div>
              <div className="stat-label">{t('statCitation')}</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{Object.keys(CAT_CONFIG).length}</div>
              <div className="stat-label">{t('statDomain')}</div>
            </div>
          </div>
        )}
      </section>

      {/* Controls */}
      <div className="controls">
        <div className="search-box">
          <Search size={14} className="search-icon" />
          <input
            placeholder={t('searchPh')}
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>

        <div className="filter-group">
          <button
            className={`filter-btn ${catFilter === CAT_ALL ? 'active' : ''}`}
            onClick={() => setCatFilter(CAT_ALL)}
          >{t('filterAll')}</button>
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
            <p>{t('loading')}</p>
          </div>
        ) : error ? (
          <div className="empty-state">
            <div className="empty-icon">📭</div>
            <p style={{ fontWeight: 600, marginBottom: 8 }}>{error}</p>
            <p style={{ fontSize: '0.85rem', color: '#4a5568' }}>
              {t('emptyError')}
            </p>
          </div>
        ) : (
          <div className="layout-grid">
            {/* Paper List */}
            <div>
              {filtered.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">🔍</div>
                  <p>{t('emptySearch')}</p>
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
      <footer className="footer" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px', paddingBottom: '32px' }}>
        <div>{t('dataSource')}</div>
        <div style={{ width: '100%', maxWidth: '400px' }}>
          <AnalyticsWidget todayVisitors={423} hasError={false} />
        </div>
      </footer>
    </div>
  )
}
