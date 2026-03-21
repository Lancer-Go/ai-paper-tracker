import { useState } from 'react'
import { ExternalLink, FileText, BookOpen } from 'lucide-react'
import { getCatCss, CAT_CONFIG } from '../utils/helpers'

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
export default function PaperCard({ paper, rank, translatedIds }) {
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
