import { useEffect, useState, type FormEvent } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { Alert } from '../components/Alert'
import { ThemeToggle } from '../components/ThemeToggle'
import { IconBook, IconBrain, IconConnections, IconFlashcards, IconSparkles } from '../components/Icons'

export function LoginPage() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  // Redireciona imediatamente assim que o usuário estiver autenticado
  useEffect(() => {
    if (user) {
      const target = (location.state as { from?: string } | null)?.from ?? '/materiais'
      navigate(target, { replace: true })
    }
  }, [user, navigate, location])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      const logged = await login(email, password)
      if (logged) {
        navigate('/materiais', { replace: true })
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Não foi possível entrar.')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleQuickDemoLogin() {
    setError(null)
    setSubmitting(true)
    try {
      const logged = await login('maria@exemplo.com', 'senha-forte-123')
      if (logged) {
        navigate('/materiais', { replace: true })
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao autenticar conta de teste.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="bento-auth-wrapper">
      <div className="bento-auth-corner">
        <ThemeToggle />
      </div>

      <div className="bento-auth-container">
        {/* Coluna Esquerda: Formulário de Acesso */}
        <div className="bento-auth-form-side">
          <div className="bento-brand-header">
            <span className="brand-logo-badge" aria-hidden="true">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
                <path d="M6 6h10" />
                <path d="M6 10h7" />
              </svg>
            </span>
            <div className="bento-brand-titles">
              <div className="bento-brand-name">
                Study<strong>AI</strong>
                <span className="bento-version-pill">Workspace</span>
              </div>
              <p className="bento-brand-desc">Ambiente inteligente de aprendizagem ativa</p>
            </div>
          </div>

          <div className="bento-demo-card">
            <div className="bento-demo-header">
              <span className="bento-demo-tag">Demonstração da Banca</span>
              <span className="bento-demo-badge">1-Clique</span>
            </div>
            <p className="bento-demo-text">
              Acesse instantaneamente a conta de teste pré-configurada com PDFs, resumos e repetição espaçada:
            </p>
            <button
              type="button"
              className="btn btn-demo-action"
              onClick={handleQuickDemoLogin}
              disabled={submitting}
            >
              <IconSparkles size={16} /> Entrar com Conta de Demonstração (Maria)
            </button>
          </div>

          <div className="bento-divider">
            <span>ou entre com suas credenciais</span>
          </div>

          <form onSubmit={handleSubmit} className="form">
            {error && <Alert>{error}</Alert>}
            <label>
              E-mail
              <input
                type="email"
                placeholder="seu.email@exemplo.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </label>
            <label>
              Senha
              <input
                type="password"
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
              />
            </label>
            <button className="btn btn-primary btn-block" disabled={submitting}>
              {submitting ? 'Autenticando…' : 'Entrar no Sistema'}
            </button>
          </form>

          <p className="auth-switch muted">
            Novo por aqui? <Link to="/cadastro">Criar nova conta</Link>
          </p>
        </div>

        {/* Coluna Direita: Showcase Bento Grid (Skills: bento + claude) */}
        <div className="bento-auth-showcase">
          <div className="bento-showcase-badge">Arquitetura de Aprendizagem</div>
          <h2 className="bento-showcase-title">Aprenda com profundidade e retenha no longo prazo.</h2>
          <p className="bento-showcase-subtitle">
            Combinamos inteligência artificial generativa com os métodos cientificamente comprovados de estudo ativo:
          </p>

          <div className="bento-features-grid">
            <div className="bento-feature-card">
              <div className="bento-feature-icon icon-blue">
                <IconBook size={20} />
              </div>
              <div className="bento-feature-content">
                <h4>Leitura & Extração de PDFs</h4>
                <p>Processamento vetorial com validação de integridade e contagem instantânea de páginas.</p>
              </div>
            </div>

            <div className="bento-feature-card">
              <div className="bento-feature-icon icon-amber">
                <IconBrain size={20} />
              </div>
              <div className="bento-feature-content">
                <h4>Sínteses Cognitivas (IA)</h4>
                <p>Resumos estruturados em 4 blocos pedagógicos gerados assincronamente pelo Google Gemini.</p>
              </div>
            </div>

            <div className="bento-feature-card">
              <div className="bento-feature-icon icon-emerald">
                <IconFlashcards size={20} />
              </div>
              <div className="bento-feature-content">
                <h4>Repetição Espaçada SM-2</h4>
                <p>Flashcards inteligentes no modo AnkiWeb com atalhos de teclado e cálculo de intervalos ideais.</p>
              </div>
            </div>

            <div className="bento-feature-card">
              <div className="bento-feature-icon icon-indigo">
                <IconConnections size={20} />
              </div>
              <div className="bento-feature-content">
                <h4>Grafo de Conhecimento</h4>
                <p>Conexões semânticas bidirecionais e navegação por backlinks no estilo Obsidian.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
