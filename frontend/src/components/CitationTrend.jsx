import { useMemo } from 'react'
import { TrendingUp } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { useI18n } from '../contexts/I18nContext'

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

export default function CitationTrend({ papers }) {
  const { t } = useI18n()
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
      <div className="sidebar-title"><TrendingUp size={14} /> {t('top10Citations')}</div>
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
            <Bar dataKey="citations" name={t('citation')} fill="#6366f1" radius={[0, 3, 3, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
