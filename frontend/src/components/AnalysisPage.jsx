import { useState, useRef, useCallback } from 'react'
import PipelineStepper from './PipelineStepper'
import ResultTabs from './ResultTabs'
import { getUserId } from '../utils/userId'

const DEFAULT_QUERY = 'Provide a comprehensive analysis of this dataset. Identify key trends, anomalies, correlations, business insights, risks, and actionable recommendations.'

const UploadIcon = () => (
  <svg viewBox="0 0 24 24" style={{ width: 24, height: 24, stroke: 'currentColor', fill: 'none', strokeWidth: 1.8, strokeLinecap: 'round', strokeLinejoin: 'round' }}>
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
    <polyline points="17 8 12 3 7 8"/>
    <line x1="12" y1="3" x2="12" y2="15"/>
  </svg>
)

const FileIcon = () => (
  <svg viewBox="0 0 24 24" style={{ width: 24, height: 24, stroke: 'currentColor', fill: 'none', strokeWidth: 1.8, strokeLinecap: 'round', strokeLinejoin: 'round' }}>
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
    <polyline points="14 2 14 8 20 8"/>
    <line x1="16" y1="13" x2="8" y2="13"/>
    <line x1="16" y1="17" x2="8" y2="17"/>
  </svg>
)

export default function AnalysisPage() {
  const [file, setFile]         = useState(null)
  const [preview, setPreview]   = useState(null)
  const [dragOver, setDragOver] = useState(false)
  const [running, setRunning]   = useState(false)
  const [step, setStep]         = useState(-1)
  const [stepLabel, setStepLabel] = useState('')
  const [result, setResult]     = useState(null)
  const [error, setError]       = useState(null)
  const pollRef = useRef(null)

  const handleFile = useCallback((f) => {
    if (!f) return
    setFile(f)
    setPreview(null)
    if (f.name.endsWith('.csv')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        const lines = e.target.result.split('\n').slice(0, 6)
        const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''))
        const rows = lines.slice(1).map(l => l.split(',').map(c => c.trim().replace(/^"|"$/g, '')))
        setPreview({ headers, rows: rows.filter(r => r.length === headers.length).slice(0, 5) })
      }
      reader.readAsText(f)
    }
  }, [])

  const onDrop = (e) => {
    e.preventDefault(); setDragOver(false)
    const f = e.dataTransfer.files[0]
    if (f && (f.name.endsWith('.csv') || f.name.endsWith('.xlsx'))) handleFile(f)
  }

  const runAnalysis = async () => {
    if (!file) return
    setRunning(true); setStep(0); setStepLabel('Loading dataset')
    setResult(null); setError(null)
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('query', DEFAULT_QUERY)
      formData.append('user_id', getUserId())
      const res = await fetch('/api/analyze', { method: 'POST', body: formData })
      const { job_id, error: err } = await res.json()
      if (err) throw new Error(err)
      pollRef.current = setInterval(async () => {
        try {
          const poll = await fetch(`/api/jobs/${job_id}`)
          const data = await poll.json()
          setStep(data.step ?? 0)
          setStepLabel(data.step_label ?? '')
          if (data.status === 'done') {
            clearInterval(pollRef.current)
            setResult(data.result)
            setRunning(false)
            setStep(8)
          } else if (data.status === 'error') {
            clearInterval(pollRef.current)
            setError(data.error || 'Unknown error')
            setRunning(false)
          }
        } catch (pollErr) {
          clearInterval(pollRef.current)
          setError(String(pollErr))
          setRunning(false)
        }
      }, 1500)
    } catch (e) {
      setError(String(e)); setRunning(false)
    }
  }

  return (
    <div>
      {/* Page header */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.35rem', fontWeight: 700, marginBottom: '0.2rem' }}>Analysis Dashboard</h2>
        <p style={{ fontSize: '0.82rem' }}>Upload a dataset — the AI pipeline runs all analysis automatically</p>
      </div>

      {/* Upload zone — full content width */}
      <div
        className={`upload-zone ${dragOver ? 'drag-over' : ''} ${file ? 'has-file' : ''}`}
        style={{ marginBottom: file ? '1.2rem' : '1.5rem', padding: file ? '2rem' : '4rem 2rem' }}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
      >
        <input type="file" accept=".csv,.xlsx" onChange={(e) => handleFile(e.target.files[0])} />

        <div className="upload-icon-wrap">
          {file ? <FileIcon /> : <UploadIcon />}
        </div>

        {file ? (
          <>
            <p style={{ color: 'var(--green)', fontWeight: 600, fontSize: '0.92rem' }}>{file.name}</p>
            <p className="upload-hint">
              {(file.size / 1024).toFixed(1)} KB
              {preview ? ` · ${preview.headers.length} columns` : ''}
              {' · click to replace'}
            </p>
          </>
        ) : (
          <>
            <p style={{ color: 'var(--text)', fontWeight: 500, fontSize: '0.95rem' }}>Drop your dataset here</p>
            <p className="upload-hint">CSV or Excel (.xlsx) · Max 200 MB · or click to browse</p>
          </>
        )}
      </div>

      {/* CSV Preview */}
      {preview && (
        <div style={{ marginBottom: '1.5rem', overflowX: 'auto' }}>
          <div className="form-label" style={{ marginBottom: '0.5rem' }}>Preview — first 5 rows</div>
          <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', overflow: 'hidden' }}>
            <table className="data-table" style={{ fontSize: '0.73rem' }}>
              <thead>
                <tr>{preview.headers.map(h => <th key={h}>{h}</th>)}</tr>
              </thead>
              <tbody>
                {preview.rows.map((row, i) => (
                  <tr key={i}>{row.map((cell, j) => <td key={j}>{cell}</td>)}</tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Action button */}
      <button
        className="btn btn-primary"
        style={{ marginBottom: '1.5rem', padding: '0.65rem 2.2rem', fontSize: '0.85rem', letterSpacing: '0.05em' }}
        onClick={runAnalysis}
        disabled={running || !file}
      >
        {running ? 'Analysing...' : 'Analyze Dataset'}
      </button>

      {/* Error */}
      {error && <div className="alert alert-error" style={{ marginBottom: '1rem' }}>Error: {error}</div>}

      {/* Progress */}
      {running && (
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <PipelineStepper currentStep={step} />
          <div className="status-bar" style={{ marginTop: '1rem' }}>
            <div className="status-dot running" />
            <span style={{ color: 'var(--text)', fontSize: '0.82rem' }}>{stepLabel || 'Processing…'}</span>
          </div>
        </div>
      )}

      {/* Results */}
      {result && !running && (
        <>
          <div className="status-bar" style={{ marginBottom: '1.5rem', background: 'rgba(76,175,80,0.06)', border: '1px solid rgba(76,175,80,0.2)' }}>
            <div className="status-dot done" />
            <span style={{ color: 'var(--green)', fontWeight: 600, fontSize: '0.82rem' }}>Analysis complete</span>
          </div>
          <PipelineStepper currentStep={8} />
          <ResultTabs result={result} />
        </>
      )}
    </div>
  )
}
