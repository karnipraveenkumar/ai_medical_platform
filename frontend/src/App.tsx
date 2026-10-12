import { useState } from 'react'
import { HeartPulse, Menu } from 'lucide-react'
import { Sidebar, type Page, type Role } from './components/Sidebar'
import { Topbar } from './components/Topbar'
import Overview from './pages/Overview'
import { AIPage, AppointmentsPage, DirectoryPage, PlaceholderPage } from './pages/DataPages'
import AuthPage from './pages/AuthPage'

export default function App() {
  const [role, setRole] = useState<Role>('Admin')
  const [page, setPage] = useState<Page>('Overview')
  const [mobileOpen, setMobileOpen] = useState(false)
  const [authOpen, setAuthOpen] = useState(false)
  const [loggedIn, setLoggedIn] = useState(Boolean(localStorage.getItem('careflow_token')))
  function logout() { localStorage.removeItem('careflow_token'); localStorage.removeItem('careflow_user'); setLoggedIn(false); setAuthOpen(false); setPage('Overview') }
  function authenticated(name: string) { setLoggedIn(true); setAuthOpen(false); window.setTimeout(() => { if (name) setPage('Overview') }, 0) }
  if (authOpen) return <AuthPage onClose={() => setAuthOpen(false)} onAuthenticated={authenticated}/>
  return <div className="app-shell"><Sidebar role={role} page={page} setPage={setPage} onLogout={logout} mobileOpen={mobileOpen} closeMobile={() => setMobileOpen(false)}/><main className="main-area"><Topbar role={role} setRole={setRole} onMenu={() => setMobileOpen(true)} onLogin={() => setAuthOpen(true)} loggedIn={loggedIn}/><div className="content-scroll">{page === 'Overview' && <Overview role={role} onNavigate={setPage}/ >}{page === 'Patients' && <DirectoryPage page="Patients"/>}{page === 'Doctors' && <DirectoryPage page="Doctors"/>}{page === 'Appointments' && <AppointmentsPage role={role}/ >}{page === 'AI assistant' && <AIPage/>}{(page === 'Medical records' || page === 'Analytics' || page === 'Billing' || page === 'Settings') && <PlaceholderPage page={page} role={role} onNavigate={setPage}/>}</div><footer className="app-footer"><span><span className="status-dot"/> All systems operational <i/></span><span>Careflow Health Systems <b>·</b> Made for better care</span></footer></main></div>
}
