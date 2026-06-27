import { useState, useEffect } from 'react'
import ResultTabs from './ResultTabs'

export default function HistoryPage() {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState(null)

  useEffect(() => {
    fetch('/api/history')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          setHistory(data)
        }
        setLoading(false)
      })
      .catch(err => {
        console.error(err)
        setLoading(false)
      })
  }, [])

  const toggleExpand = async (index, id) => {
    if (expanded === index) {
      setExpanded(null)
      return
    }

    const entry = history[index]
    if (!entry.result) {
      try {
        const res = await fetch(`/api/history/${id}`)
        const data = await res.json()
        if (data && data.result) {
          setHistory(prev => prev.map((item, idx) => idx === index ? { ...item, result: data.result } : item))
        }
      } catch (err) {
        console.error(err)
      }
    }
    setExpanded(index)
  }

  if (loading) {
    return (
      <div>
        <div style={{ marginBottom: '1.5rem' }}>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>Analysis History</h2>
          <p>Loading runs...</p>
        </div>
      </div>
    )
  }

  if (history.length === 0) {
    return (
      <div>
        <div style={{ marginBottom: '1.5rem' }}>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>Analysis History</h2>
          <p>Previous runs in this session</p>
        </div>
        <div className="empty-state card">
          <div className="empty-icon" style={{ fontSize: '1.5rem', marginBottom: '0.5rem', color: 'var(--border)' }}>—</div>
          <p>No analyses run yet. Head to Analysis to get started.</p>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>Analysis History</h2>
        <p>{history.length} run{history.length !== 1 ? 's' : ''} in this session</p>
      </div>

      {history.map((entry, i) => {
        const score = (entry.score ?? 0) <= 10 ? (entry.score ?? 0) * 10 : (entry.score ?? 0)
        const color = entry.passed ? 'var(--green)' : 'var(--yellow)'
        const isOpen = expanded === i

        return (
          <div key={entry.id || i} style={{ marginBottom: '0.6rem' }}>
            <div
              className={`history-card ${entry.passed ? 'passed' : 'failed'}`}
              onClick={() => toggleExpand(i, entry.id)}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 600, color: 'var(--text)', fontSize: '0.88rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {entry.file}
                  </div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: '0.15rem' }}>
                    Comprehensive analysis
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1.2rem', flexShrink: 0 }}>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '1.4rem', fontWeight: 800, color, lineHeight: 1 }}>{score.toFixed(0)}</div>
                    <div style={{ fontSize: '0.6rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>SCORE/100</div>
                  </div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 700 }}>{isOpen ? '▲' : '▼'}</div>
                </div>
              </div>
            </div>

            {isOpen && entry.result && (
              <div className="card" style={{ borderRadius: '0 0 var(--radius) var(--radius)', borderTop: 'none', marginTop: '-1px', background: 'var(--bg-base)' }}>
                <ResultTabs result={entry.result} />
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
