import { useState } from 'react'
import Sidebar from './components/Sidebar'
import HomePage from './components/HomePage'
import AnalysisPage from './components/AnalysisPage'
import HistoryPage from './components/HistoryPage'

export default function App() {
  const [page, setPage] = useState('home')

  return (
    <div className="app-shell">
      <Sidebar page={page} setPage={setPage} />
      <main className="main-content">
        {page === 'home'     && <HomePage setPage={setPage} />}
        {page === 'analysis' && <AnalysisPage />}
        {page === 'history'  && <HistoryPage />}
      </main>
    </div>
  )
}
