import { useMemo } from 'react'
import { Layers } from 'lucide-react'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import { getCatColor } from '../utils/helpers'
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

export default function CategorySidebar({ papers }) {
  const { t } = useI18n()
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
      <div className="sidebar-title"><Layers size={14} /> {t('domainDist')}</div>

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
