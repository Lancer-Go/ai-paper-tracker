/**
 * 类别配置表 & 工具函数
 */

export const CAT_CONFIG = {
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

export const CAT_ALL = 'all'

export function getCatCss(cat) {
  return (CAT_CONFIG[cat] || {}).css || 'cat-default'
}

export function getCatColor(cat) {
  return (CAT_CONFIG[cat] || {}).color || '#94a3b8'
}
