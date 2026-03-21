import { useState } from 'react'
import { ExternalLink, FileText, BookOpen, Github, Code } from 'lucide-react'
import { getCatCss, CAT_CONFIG } from '../utils/helpers'

// ── 评分条 ──────────────────────────────────────────────
function ScoreBar({ value, color, label, icon }) {
  return (
    <div className="breakdown-item">
      <div className="breakdown-header">
        <span className="breakdown-label">{icon} {label}</span>
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
export default function PaperCard({ paper, rank, translationIndex }) {
  const [expanded, setExpanded] = useState(false)
  const safeId = paper.arxiv_id.replace('/', '_')
  const translationInfo = translationIndex[safeId]
  // 旧版 index 条目可能缺少 type 字段，有 translationInfo 则默认为 'pdf'
  const translationType = translationInfo ? (translationInfo.type || 'pdf') : undefined

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
            {paper.author_h_index > 0 && (
              <div className="metric">
                <span className="metric-icon">👤</span>
                <span className="metric-value">h={paper.author_h_index}</span>
              </div>
            )}
            {paper.has_code && (
              <div className="metric">
                <span className="metric-icon">💻</span>
                <span className="metric-value">{paper.github_stars > 0 ? `⭐${paper.github_stars.toLocaleString()}` : '有代码'}</span>
              </div>
            )}
            {paper.hn_buzz > 0 && (
              <div className="metric">
                <span className="metric-icon">🔥</span>
                <span className="metric-value">{paper.hn_buzz}</span>
                <span style={{ fontSize: '0.72rem', color: '#94a3b8' }}>HN</span>
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
            {paper.github_url && (
              <a
                className="action-btn action-btn-secondary"
                style={{ background: 'rgba(34, 197, 94, 0.1)', color: '#22c55e', borderColor: 'rgba(34, 197, 94, 0.3)' }}
                href={paper.github_url}
                target="_blank"
                rel="noopener noreferrer"
              >
                <Code size={13} /> GitHub ⭐{(paper.github_stars || 0).toLocaleString()}
              </a>
            )}
            {translationType === 'html' ? (
              <a
                className="action-btn action-btn-secondary"
                style={{ background: 'rgba(168, 85, 247, 0.15)', color: '#a855f7', borderColor: 'rgba(168, 85, 247, 0.4)', fontWeight: 600 }}
                href={`data/translations/${translationInfo.file}`}
                target="_blank"
                rel="noopener noreferrer"
                title="保留图片、公式、表格的高保真中文翻译"
              >
                <BookOpen size={13} /> 🔬 保真翻译
              </a>
            ) : translationType === 'pdf' ? (
              <a
                className="action-btn action-btn-secondary"
                style={{ background: 'rgba(245, 158, 11, 0.12)', color: '#f59e0b', borderColor: 'rgba(245, 158, 11, 0.3)' }}
                href={`data/translations/${translationInfo.file}`}
                target="_blank"
                rel="noopener noreferrer"
                title="基于 PDF 提取的纯文本翻译版"
              >
                <BookOpen size={13} /> 📝 简版翻译
              </a>
            ) : (
              <span
                className="action-btn action-btn-secondary"
                style={{ background: 'rgba(100, 116, 139, 0.08)', color: '#475569', borderColor: 'rgba(100, 116, 139, 0.15)', cursor: 'not-allowed', opacity: 0.5 }}
                title="翻译暂未生成，系统每天 14:00 自动翻译"
              >
                <BookOpen size={13} /> 暂无翻译
              </span>
            )}
          </div>

          {/* 评分拆解 — 8维度 */}
          {paper.score_breakdown && (
            <div style={{ marginTop: 14, padding: '12px', background: 'rgba(0,0,0,0.2)', borderRadius: 8 }}>
              <div style={{ fontSize: '0.72rem', color: '#4a5568', marginBottom: 8, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>评分拆解</div>
              <div className="breakdown-list">
                <ScoreBar value={paper.score_breakdown.velocity_norm} color="#6366f1" label="引用速度" icon="📈" />
                <ScoreBar value={paper.score_breakdown.mass_norm} color="#22d3ee" label="引用总量" icon="📚" />
                <ScoreBar value={paper.score_breakdown.author_norm} color="#f59e0b" label="作者影响" icon="👤" />
                <ScoreBar value={paper.score_breakdown.code_norm} color="#22c55e" label="有代码" icon="💻" />
                <ScoreBar value={paper.score_breakdown.stars_norm} color="#eab308" label="GitHub ⭐" icon="⭐" />
                <ScoreBar value={paper.score_breakdown.freshness_norm} color="#a78bfa" label="新鲜度" icon="🕐" />
                <ScoreBar value={paper.score_breakdown.buzz_norm} color="#f472b6" label="社区讨论" icon="💬" />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
