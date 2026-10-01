import { useState, type FormEvent } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { Alert } from '../components/Alert'
import { ThemeToggle } from '../components/ThemeToggle'

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await login(email, password)
      navigate((location.state as { from?: string } | null)?.from ?? '/materiais', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Não foi possível entrar.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-wrap">
      <div className="auth-theme-corner">
        <ThemeToggle />
      </div>
      <div className="card auth-card">
        <div className="auth-brand">
          <span className="brand-mark" aria-hidden="true">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
              <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
              <path d="M6 6h10" />
              <path d="M6 10h7" />
            </svg>
          </span>
          <h1>Study<strong>AI</strong></h1>
          <p className="muted">Ambiente inteligente de estudos e repetição espaçada.</p>
        </div>
        <form onSubmit={handleSubmit} className="form">
          {error && <Alert>{error}</Alert>}
          <label>
            E-mail
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="email" autoFocus />
          </label>
          <label>
            Senha
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required autoComplete="current-password" />
          </label>
          <button className="btn btn-primary btn-block" disabled={submitting}>
            {submitting ? 'Entrando…' : 'Entrar'}
          </button>
          <button
            type="button"
            className="btn btn-ghost btn-sm btn-block"
            style={{ marginTop: '0.4rem', border: '1px dashed var(--border)', fontSize: '0.85rem' }}
            onClick={() => {
              setEmail('maria@exemplo.com')
              setPassword('senha-forte-123')
            }}
          >
            Preencher com conta de teste (Maria)
          </button>
        </form>
        <p className="auth-switch muted">
          Ainda não tem conta? <Link to="/cadastro">Criar conta</Link>
        </p>
        <div style={{ textAlign: 'center', marginTop: '1rem', fontSize: '0.75rem', color: '#94a3b8' }}>
          StudyAI v1.1 • Modo iframe seguro
        </div>
      </div>
    </div>
  )
}
