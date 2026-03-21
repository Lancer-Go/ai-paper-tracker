import { useState, useEffect } from 'react'

/**
 * 加载论文数据、日期列表、翻译索引的 Hook
 */
export function usePapers() {
  const [papers, setPapers] = useState([])
  const [availableDates, setAvailableDates] = useState([])
  const [selectedDate, setSelectedDate] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [dataInfo, setDataInfo] = useState({ date: '', total: 0 })
  const [translatedIds, setTranslatedIds] = useState(new Set())

  const base = import.meta.env.BASE_URL || '/'

  // 加载日期列表
  useEffect(() => {
    fetch(`${base}data/exports/index.json`)
      .then(r => r.json())
      .then(data => {
        setAvailableDates(data.available_dates || [])
        setSelectedDate(data.latest || '')
      })
      .catch(() => {
        setSelectedDate('latest')
      })
  }, [])

  // 加载翻译索引
  useEffect(() => {
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
      .catch(() => {
        setError('暂无数据，请先运行 python run.py 生成今日热榜')
        setLoading(false)
      })
  }, [selectedDate])

  return {
    papers,
    availableDates,
    selectedDate,
    setSelectedDate,
    loading,
    error,
    dataInfo,
    translatedIds,
  }
}
