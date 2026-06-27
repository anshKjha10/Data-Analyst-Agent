import { useState } from 'react'

// ── Markdown renderer ─────────────────────────────────────────────────────────
function renderMd(text) {
  if (!text) return ''


  const inline = (s) =>
    s
      .replace(/!\[(.+?)\]\((.+?)\)/g, '<img src="$2" alt="$1" style="max-width:100%; border-radius:var(--radius-sm); border:1px solid var(--border); margin:0.8rem 0; display:block;" />')
      .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/`(.+?)`/g, '<code>$1</code>')

  const lines = text.split('\n')
  let html = ''
  let inList = false
  let listTag = 'ul'
  let tableRows = []
  let inTable = false

  const flushList = () => {
    if (inList) { html += `</${listTag}>`; inList = false }
  }
  const flushTable = () => {
    if (!tableRows.length) return
    const [header, , ...body] = tableRows
    const heads = header.split('|').map(s => s.trim()).filter(Boolean)
    html += '<table><thead><tr>'
    heads.forEach(h => { html += `<th>${inline(h)}</th>` })
    html += '</tr></thead><tbody>'
    body.forEach(row => {
      const cells = row.split('|').map(s => s.trim()).filter(Boolean)
      if (cells.length === 0) return
      html += '<tr>'
      cells.forEach(c => { html += `<td>${inline(c)}</td>` })
      html += '</tr>'
    })
    html += '</tbody></table>'
    tableRows = []
    inTable = false
  }

  for (const raw of lines) {
    const line = raw.trimEnd()

    // Detect table rows (lines containing |)
    if (/^\s*\|/.test(line) || (line.includes('|') && tableRows.length > 0)) {
      // Skip pure separator lines (--|--|--)
      flushList()
      if (/^[\s|:-]+$/.test(line)) {
        tableRows.push(line) // keep separator so we can skip it in flushTable
        inTable = true
        continue
      }
      tableRows.push(line)
      inTable = true
      continue
    }

    // Flush table if we hit a non-table line
    if (inTable) { flushTable() }

    if (!line) { flushList(); html += '<br/>'; continue }

    if (/^### /.test(line)) { flushList(); html += `<h3>${inline(line.slice(4))}</h3>`; continue }
    if (/^## /.test(line))  { flushList(); html += `<h2>${inline(line.slice(3))}</h2>`; continue }
    if (/^# /.test(line))   { flushList(); html += `<h1>${inline(line.slice(2))}</h1>`; continue }
    if (/^---+$/.test(line)) { flushList(); html += '<hr/>'; continue }
    if (/^> /.test(line))   { flushList(); html += `<blockquote>${inline(line.slice(2))}</blockquote>`; continue }

    if (/^[-*] /.test(line)) {
      if (!inList || listTag !== 'ul') { flushList(); html += '<ul>'; inList = true; listTag = 'ul' }
      html += `<li>${inline(line.replace(/^[-*] /, ''))}</li>`
      continue
    }
    if (/^\d+\. /.test(line)) {
      if (!inList || listTag !== 'ol') { flushList(); html += '<ol>'; inList = true; listTag = 'ol' }
      html += `<li>${inline(line.replace(/^\d+\. /, ''))}</li>`
      continue
    }

    flushList()
    html += `<p>${inline(line)}</p>`
  }
  flushList()
  if (inTable) flushTable()
  return html
}


const TABS = ['Insights', 'Visualizations', 'EDA', 'Review', 'Report', 'Plan', 'Debug']

export default function ResultTabs({ result }) {
  const [tab, setTab] = useState(0)

  const review       = result?.review || {}
  const reviewScore  = result?.review_score ?? 0
  const reviewPassed = result?.review_passed ?? false
  const insights     = result?.insights || {}
  const datasetInfo  = result?.dataset_info || {}
  const edaResults   = result?.eda_results || {}
  const vizList      = result?.visualizations || []
  const reportText   = result?.report || ''
  const plan         = result?.analysis_plan || {}

  const scorePct = reviewScore <= 10 ? reviewScore * 10 : reviewScore
  const shape = datasetInfo?.shape || [0, 0]
  const rowCount = Array.isArray(shape) ? shape[0] : (datasetInfo?.rows ?? '—')

  return (
    <div style={{ marginTop: '1.5rem' }}>
      <div className="section-title">Analysis Results</div>

      {/* KPI Cards */}
      <div className="grid-4" style={{ marginBottom: '1.5rem' }}>
        <div className="metric-card">
          <div className="mcard-label">QUALITY SCORE</div>
          <div className="mcard-value" style={{ color: scorePct >= 70 ? 'var(--green)' : 'var(--yellow)' }}>
            {scorePct.toFixed(0)}%
          </div>
          <div className="mcard-sub">Reviewer rating</div>
        </div>
        <div className="metric-card" style={{ borderTop: `2px solid ${reviewPassed ? 'var(--green)' : 'var(--yellow)'}` }}>
          <div className="mcard-label">REVIEW STATUS</div>
          <div className="mcard-value" style={{ fontSize: '1rem', color: reviewPassed ? 'var(--green)' : 'var(--yellow)' }}>
            {reviewPassed ? 'PASSED' : 'NEEDS REVIEW'}
          </div>
        </div>
        <div className="metric-card">
          <div className="mcard-label">CHARTS</div>
          <div className="mcard-value">{vizList.length}</div>
          <div className="mcard-sub">Generated</div>
        </div>
        <div className="metric-card">
          <div className="mcard-label">ROWS</div>
          <div className="mcard-value">{typeof rowCount === 'number' ? rowCount.toLocaleString() : rowCount}</div>
          <div className="mcard-sub">Dataset size</div>
        </div>
      </div>

      {/* Tab bar */}
      <div className="tabs-bar">
        {TABS.map((t, i) => (
          <button key={t} className={`tab-btn ${tab === i ? 'active' : ''}`} onClick={() => setTab(i)}>
            {t}
          </button>
        ))}
      </div>

      {/* ── Tab: Insights ── */}
      {tab === 0 && (
        <div>
          {insights.executive_summary && (
            <div className="card" style={{ marginBottom: '1.2rem' }}>
              <div className="section-title" style={{ fontSize: '0.9rem', marginBottom: '0.6rem' }}>Executive Summary</div>
              <p style={{ color: 'var(--text)', lineHeight: 1.7, fontSize: '0.88rem' }}>{insights.executive_summary}</p>
            </div>
          )}

          <div className="grid-2" style={{ gap: '1.2rem' }}>
            <div>
              {(insights.key_findings || []).length > 0 && (
                <>
                  <div className="section-title" style={{ fontSize: '0.9rem', margin: '0 0 0.5rem' }}>Key Findings</div>
                  {insights.key_findings.map((f, i) => (
                    <div key={i} className="insight-item purple">{f}</div>
                  ))}
                </>
              )}
              {(insights.key_trends || []).length > 0 && (
                <>
                  <div className="section-title" style={{ fontSize: '0.9rem', margin: '1rem 0 0.5rem' }}>Trends</div>
                  {insights.key_trends.map((t, i) => (
                    <div key={i} className="insight-item green">{t}</div>
                  ))}
                </>
              )}
            </div>
            <div>
              {(insights.anomalies || []).length > 0 && (
                <>
                  <div className="section-title" style={{ fontSize: '0.9rem', margin: '0 0 0.5rem' }}>Anomalies</div>
                  {insights.anomalies.map((a, i) => (
                    <div key={i} className="insight-item yellow">{a}</div>
                  ))}
                </>
              )}
              {(insights.business_risks || []).length > 0 && (
                <>
                  <div className="section-title" style={{ fontSize: '0.9rem', margin: '1rem 0 0.5rem' }}>Business Risks</div>
                  {insights.business_risks.map((r, i) => (
                    <div key={i} className="insight-item red">{r}</div>
                  ))}
                </>
              )}
            </div>
          </div>

          {(insights.recommendations || []).length > 0 && (
            <div style={{ marginTop: '1.2rem' }}>
              <div className="section-title" style={{ fontSize: '0.9rem', marginBottom: '0.75rem' }}>Recommendations</div>
              <div className="grid-3">
                {insights.recommendations.map((rec, i) => (
                  <div key={i} className="card" style={{ borderLeft: '3px solid var(--accent)', padding: '0.9rem 1.1rem' }}>
                    <p style={{ color: 'var(--text)', fontSize: '0.84rem', margin: 0 }}>{rec}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── Tab: Visualizations ── */}
      {tab === 1 && (
        vizList.length === 0
          ? <div className="empty-state"><div className="empty-icon">—</div><p>No visualizations were generated.</p></div>
          : <div className="viz-grid">
              {vizList.map((viz, i) => (
                <div key={i} className="viz-item">
                  <div className="viz-title">{viz.title || `Chart ${i + 1}`}</div>
                  {viz.image_url
                    ? <img src={viz.image_url} alt={viz.title} />
                    : <div className="card empty-state"><p style={{ fontSize: '0.8rem' }}>Image not found</p></div>
                  }
                </div>
              ))}
            </div>
      )}

      {/* ── Tab: EDA ── */}
      {tab === 2 && (
        <div>
          {Object.keys(edaResults).length === 0 && (
            <div className="empty-state"><div className="empty-icon">—</div><p>EDA results not available.</p></div>
          )}

          {/* Dataset Overview */}
          {edaResults.get_dataset_overview && (() => {
            const ov = edaResults.get_dataset_overview
            const [rows, cols] = ov.shape || [0, 0]
            return (
              <div style={{ marginBottom: '1.5rem' }}>
                <div className="section-title" style={{ fontSize: '0.9rem', marginBottom: '0.75rem' }}>Dataset Overview</div>
                <div className="grid-4" style={{ marginBottom: '0.75rem' }}>
                  {[
                    ['ROWS',       rows],
                    ['COLUMNS',    cols],
                    ['MEMORY',     `${ov.memory_mb} MB`],
                    ['DUPLICATES', edaResults.get_duplicate_count ?? '—'],
                  ].map(([lbl, val]) => (
                    <div key={lbl} className="metric-card">
                      <div className="mcard-label">{lbl}</div>
                      <div className="mcard-value" style={{ fontSize: '1.4rem' }}>{val}</div>
                    </div>
                  ))}
                </div>
                {ov.dtypes && Object.keys(ov.dtypes).length > 0 && (
                  <div style={{ overflowX: 'auto' }}>
                    <table className="data-table" style={{ fontSize: '0.78rem' }}>
                      <thead><tr><th>Column</th><th>Data Type</th></tr></thead>
                      <tbody>
                        {Object.entries(ov.dtypes).map(([col, dtype]) => (
                          <tr key={col}>
                            <td style={{ fontWeight: 600, color: 'var(--text)' }}>{col}</td>
                            <td><span className="badge badge-blue">{dtype}</span></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )
          })()}

          {/* Missing Values */}
          {edaResults.missing_value_analysis !== undefined && (() => {
            const mv = edaResults.missing_value_analysis
            const records = Array.isArray(mv) ? mv : []
            return (
              <div style={{ marginBottom: '1.5rem' }}>
                <div className="section-title" style={{ fontSize: '0.9rem', marginBottom: '0.75rem' }}>Missing Values</div>
                {records.length === 0
                  ? <div className="alert alert-success">No missing values detected</div>
                  : <table className="data-table">
                      <thead><tr><th>Column</th><th>Missing Count</th><th>Missing %</th></tr></thead>
                      <tbody>
                        {records.map((r, i) => (
                          <tr key={i}>
                            <td style={{ fontWeight: 600, color: 'var(--text)' }}>{r.index ?? r.column ?? r.Column ?? '—'}</td>
                            <td>{r['Missing Count'] ?? r.missing_count ?? '—'}</td>
                            <td>
                              <span className={`badge ${(r['Missing Percentage'] ?? 0) > 30 ? 'badge-red' : 'badge-yellow'}`}>
                                {r['Missing Percentage'] ?? r.missing_pct ?? '—'}%
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                }
              </div>
            )
          })()}

          {/* Summary Statistics */}
          {edaResults.summary_statistics && (() => {
            const raw = edaResults.summary_statistics
            const records = Array.isArray(raw) ? raw : []
            if (!records.length) return null
            const statKeys = Object.keys(records[0]).filter(k => k !== 'index')
            return (
              <div style={{ marginBottom: '1.5rem' }}>
                <div className="section-title" style={{ fontSize: '0.9rem', marginBottom: '0.75rem' }}>Summary Statistics</div>
                <div style={{ overflowX: 'auto' }}>
                  <table className="data-table" style={{ fontSize: '0.77rem' }}>
                    <thead>
                      <tr>
                        <th>Column</th>
                        {statKeys.map(k => <th key={k}>{k}</th>)}
                      </tr>
                    </thead>
                    <tbody>
                      {records.map((row, i) => (
                        <tr key={i}>
                          <td style={{ fontWeight: 600, color: 'var(--text)', fontFamily: 'Fira Code', fontSize: '0.73rem' }}>{row.index ?? `row_${i}`}</td>
                          {statKeys.map(k => (
                            <td key={k}>{typeof row[k] === 'number' ? row[k].toFixed(2) : (row[k] ?? '—')}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )
          })()}

          {/* Skewness */}
          {edaResults.get_skewness && (() => {
            const entries = Object.entries(edaResults.get_skewness).filter(([, v]) => v !== null)
            if (!entries.length) return null
            return (
              <div style={{ marginBottom: '1.5rem' }}>
                <div className="section-title" style={{ fontSize: '0.9rem', marginBottom: '0.75rem' }}>Skewness</div>
                <table className="data-table" style={{ fontSize: '0.78rem' }}>
                  <thead><tr><th>Column</th><th>Skewness</th><th>Distribution</th></tr></thead>
                  <tbody>
                    {entries.map(([col, val]) => {
                      const v = parseFloat(val)
                      const label = Math.abs(v) < 0.5 ? 'Normal' : v > 0 ? 'Right-skewed' : 'Left-skewed'
                      const cls   = Math.abs(v) < 0.5 ? 'badge-green' : Math.abs(v) < 1 ? 'badge-yellow' : 'badge-red'
                      return (
                        <tr key={col}>
                          <td style={{ fontWeight: 600, color: 'var(--text)' }}>{col}</td>
                          <td style={{ fontFamily: 'Fira Code', fontSize: '0.75rem' }}>{v.toFixed(3)}</td>
                          <td><span className={`badge ${cls}`}>{label}</span></td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            )
          })()}

          {/* Outliers */}
          {edaResults.outlier_detection && (() => {
            const entries = Object.entries(edaResults.outlier_detection)
            if (!entries.length) return null
            return (
              <div style={{ marginBottom: '1.5rem' }}>
                <div className="section-title" style={{ fontSize: '0.9rem', marginBottom: '0.75rem' }}>Outlier Detection (IQR)</div>
                <table className="data-table" style={{ fontSize: '0.78rem' }}>
                  <thead><tr><th>Column</th><th>Outlier Count</th><th>Severity</th></tr></thead>
                  <tbody>
                    {entries.map(([col, cnt]) => {
                      const n = parseInt(cnt) || 0
                      const badge = n === 0 ? 'badge-green' : n < 10 ? 'badge-yellow' : 'badge-red'
                      return (
                        <tr key={col}>
                          <td style={{ fontWeight: 600, color: 'var(--text)' }}>{col}</td>
                          <td>{n}</td>
                          <td><span className={`badge ${badge}`}>{n === 0 ? 'None' : n < 10 ? 'Low' : 'High'}</span></td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            )
          })()}

          {/* Correlation */}
          {edaResults.correlation_analysis && (() => {
            const records = Array.isArray(edaResults.correlation_analysis) ? edaResults.correlation_analysis : []
            if (!records.length) return null
            const colKeys = Object.keys(records[0]).filter(k => k !== 'index')
            return (
              <div style={{ marginBottom: '1.5rem' }}>
                <div className="section-title" style={{ fontSize: '0.9rem', marginBottom: '0.75rem' }}>Correlation Matrix</div>
                <div style={{ overflowX: 'auto' }}>
                  <table className="data-table" style={{ fontSize: '0.72rem' }}>
                    <thead>
                      <tr>
                        <th></th>
                        {colKeys.map(k => <th key={k}>{k}</th>)}
                      </tr>
                    </thead>
                    <tbody>
                      {records.map((row, i) => (
                        <tr key={i}>
                          <td style={{ fontWeight: 600, color: 'var(--text)', fontFamily: 'Fira Code', fontSize: '0.7rem' }}>
                            {row.index ?? colKeys[i] ?? `row_${i}`}
                          </td>
                          {colKeys.map(k => {
                            const v = parseFloat(row[k])
                            const abs = Math.abs(v)
                            const color = isNaN(v) ? 'var(--text-muted)' : abs > 0.7 ? 'var(--red)' : abs > 0.4 ? 'var(--yellow)' : 'var(--text-muted)'
                            return (
                              <td key={k} style={{ color, fontFamily: 'Fira Code', fontSize: '0.7rem' }}>
                                {isNaN(v) ? '—' : v.toFixed(2)}
                              </td>
                            )
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )
          })()}
        </div>
      )}

      {/* ── Tab: Review ── */}
      {tab === 3 && (
        <div>
          {Object.keys(review.scores || {}).length > 0 && (
            <div className="card" style={{ marginBottom: '1.2rem' }}>
              <div className="section-title" style={{ fontSize: '0.9rem', marginBottom: '0.75rem' }}>Dimension Scores</div>
              {Object.entries(review.scores).map(([dim, val]) => {
                const pct = (parseFloat(val) / 10) * 100
                const color = pct >= 70 ? 'var(--green)' : pct >= 50 ? 'var(--yellow)' : 'var(--red)'
                return (
                  <div key={dim} className="score-bar-wrap">
                    <div className="score-bar-header">
                      <span className="score-bar-label">{dim.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</span>
                      <span className="score-bar-val" style={{ color }}>{val}/10</span>
                    </div>
                    <div className="score-bar-track">
                      <div className="score-bar-fill" style={{ width: `${pct}%`, background: color }} />
                    </div>
                  </div>
                )
              })}
            </div>
          )}
          {review.strengths?.length > 0 && (
            <>
              <div className="section-title" style={{ fontSize: '0.9rem', marginBottom: '0.5rem' }}>Strengths</div>
              {review.strengths.map((s, i) => <div key={i} className="insight-item green">{s}</div>)}
            </>
          )}
          {review.improvements?.length > 0 && (
            <>
              <div className="section-title" style={{ fontSize: '0.9rem', margin: '1rem 0 0.5rem' }}>Improvements</div>
              {review.improvements.map((s, i) => <div key={i} className="insight-item yellow">{s}</div>)}
            </>
          )}
        </div>
      )}

      {/* ── Tab: Report ── */}
      {tab === 4 && (
        reportText
          ? <div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1rem' }}>
                <a
                  href={`data:text/markdown;charset=utf-8,${encodeURIComponent(reportText)}`}
                  download="analysis_report.md"
                  className="btn btn-green"
                >
                  Download .md
                </a>
              </div>
              <div
                className="card md-report"
                dangerouslySetInnerHTML={{ __html: renderMd(reportText) }}
              />
            </div>
          : <div className="empty-state"><p>No report generated.</p></div>
      )}

      {/* ── Tab: Plan ── */}
      {tab === 5 && (
        <div>
          {(plan?.tasks || []).map((t, i) => (
            <div key={i} className="plan-task">
              <span className="badge badge-purple" style={{ marginTop: '0.1rem', flexShrink: 0 }}>{i + 1}</span>
              <div className="plan-task-body">
                <div className="agent-name">{t.agent}</div>
                <div className="task-action">{t.action}</div>
                {t.args && <div className="task-args">{JSON.stringify(t.args)}</div>}
              </div>
            </div>
          ))}
          {!plan?.tasks?.length && <div className="empty-state"><p>No plan data.</p></div>}
        </div>
      )}

      {/* ── Tab: Debug ── */}
      {tab === 6 && (
        <div style={{ overflowX: 'auto' }}>
          <pre style={{ fontFamily: 'Fira Code', fontSize: '0.72rem', color: 'var(--text-muted)', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '1.2rem', whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}
