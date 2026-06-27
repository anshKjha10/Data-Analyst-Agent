import PipelineStepper from './PipelineStepper'

const AGENTS = [
  { name: 'Dataset Agent',       role: 'Loads and profiles data',    out: 'Schema, dtypes, shape' },
  { name: 'Planner Agent',       role: 'Creates analysis plan',      out: 'Task list per agent' },
  { name: 'EDA Agent',           role: 'Statistical analysis',       out: 'Stats, correlations, missing' },
  { name: 'Visualization Agent', role: 'Generates charts',           out: 'PNG plots' },
  { name: 'Insight Agent',       role: 'Business insights',          out: 'Findings, trends, risks' },
  { name: 'Reviewer Agent',      role: 'Quality assurance',          out: 'Pass/Fail + scores' },
  { name: 'Reflection Agent',    role: 'Self-correction loop',       out: 'Refined analysis plan' },
  { name: 'Report Agent',        role: 'Final report writer',        out: 'Markdown report' },
]

export default function HomePage({ setPage }) {
  return (
    <div>
      {/* Hero */}
      <div className="hero">
        <h1>DataMind <span>AI Analyst</span></h1>
        <p>Upload your dataset · Get a full AI-powered analysis report</p>
        <div style={{ marginTop: '1.5rem', display: 'flex', gap: '0.8rem', justifyContent: 'center' }}>
          <button className="btn btn-primary btn-lg" onClick={() => setPage('analysis')}>
            Start Analysis
          </button>
          <button className="btn btn-ghost btn-lg" onClick={() => setPage('history')}>
            View History
          </button>
        </div>
      </div>

      {/* KPI row */}
      <div className="grid-3" style={{ marginBottom: '2rem' }}>
        {[
          { label: 'AGENTS',       value: '8',          sub: 'Specialist AI agents' },
          { label: 'POWERED BY',   value: 'Groq',       sub: 'LLaMA 3.3 · 70B' },
          { label: 'FRAMEWORK',    value: 'LangGraph',  sub: 'Agentic state machine' },
        ].map(({ label, value, sub }) => (
          <div className="metric-card" key={label}>
            <div className="mcard-label">{label}</div>
            <div className="mcard-value">{value}</div>
            <div className="mcard-sub">{sub}</div>
          </div>
        ))}
      </div>

      {/* Pipeline */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div className="section-title">How It Works</div>
        <PipelineStepper currentStep={-1} />
      </div>

      {/* Agent table */}
      <div className="card">
        <div className="section-title">Agent Pipeline</div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Agent</th>
              <th>Role</th>
              <th>Output</th>
            </tr>
          </thead>
          <tbody>
            {AGENTS.map(({ name, role, out }) => (
              <tr key={name}>
                <td style={{ fontWeight: 600, color: 'var(--text)' }}>{name}</td>
                <td>{role}</td>
                <td style={{ fontFamily: 'Fira Code', fontSize: '0.75rem' }}>{out}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
