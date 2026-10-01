import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { tokenStore } from '../api/client'

export function ProtectedRoute() {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) return <div className="center muted">Carregando…</div>
  // Se não tem user e também não tem token salvo, redireciona para login
  if (!user && !tokenStore.get()) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }
  return <Outlet />
}

/** Rotas públicas (login/cadastro): se já estiver logado, vai direto para o app. */
export function PublicOnlyRoute() {
  const { user, loading } = useAuth()
  if (loading) return <div className="center muted">Carregando…</div>
  if (user) return <Navigate to="/materiais" replace />
  return <Outlet />
}
