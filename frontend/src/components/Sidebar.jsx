// SVG icons as inline components — no emojis
const HomeIcon = () => (
  <svg viewBox="0 0 24 24"><path d="M3 12L12 3l9 9"/><path d="M9 21V12h6v9"/><path d="M3 12v9h6M15 21v-9h6v9"/></svg>
)
const AnalysisIcon = () => (
  <svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><path d="M14 17.5h7M17.5 14v7"/></svg>
)
const HistoryIcon = () => (
  <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/></svg>
)

export default function Sidebar({ page, setPage }) {
  const nav = [
    { key: 'home',     Icon: HomeIcon,     label: 'Home' },
    { key: 'analysis', Icon: AnalysisIcon, label: 'Analysis' },
    { key: 'history',  Icon: HistoryIcon,  label: 'History' },
  ]

  return (
    <nav className="sidebar">
      <div className="sidebar-section">
        <div className="sidebar-section-label">Navigation</div>
        {nav.map(({ key, Icon, label }) => (
          <button
            key={key}
            className={`nav-item ${page === key ? 'active' : ''}`}
            onClick={() => setPage(key)}
          >
            <span className="nav-icon"><Icon /></span>
            {label}
          </button>
        ))}
      </div>

      <div className="sidebar-footer">
        LangGraph + Groq<br />
        <span className="dot">●</span> Multi-agent pipeline
      </div>
    </nav>
  )
}
