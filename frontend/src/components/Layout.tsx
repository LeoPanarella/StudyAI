import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { ThemeToggle } from './ThemeToggle'

export function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  async function handleLogout() {
    await logout()
    navigate('/login')
  }

  const initial = (user?.name?.trim()?.[0] || 'U').toUpperCase()

  return (
    <div className="app">
      <header className="topbar">
        <div className="container topbar-inner">
          <Link to="/materiais" className="brand">
            <span className="brand-mark" aria-hidden="true">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
                <path d="M6 6h10" />
                <path d="M6 10h7" />
              </svg>
            </span>
            <span className="brand-name">
              Study<strong>AI</strong>
            </span>
            <span className="brand-version-badge">v1.1</span>
          </Link>

          <nav className="nav">
            <NavLink to="/materiais">Meus materiais</NavLink>
          </nav>

          <div className="topbar-user">
            <ThemeToggle />
            <div className="user-avatar" title={user?.email || ''}>
              {initial}
            </div>
            <span className="user-name muted" style={{ fontSize: '0.88rem' }}>
              {user?.name}
            </span>
            <button className="btn btn-ghost btn-sm" onClick={handleLogout}>
              Sair
            </button>
          </div>
        </div>
      </header>

      <main className="container page">
        <Outlet />
      </main>
    </div>
  )
}
