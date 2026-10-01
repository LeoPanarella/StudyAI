import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'
import { ApiError, authApi, tokenStore, type User } from '../api/client'

interface AuthState {
  user: User | null
  loading: boolean // true enquanto verificamos a sessão existente ao abrir o app
  login: (email: string, password: string) => Promise<User>
  register: (name: string, email: string, password: string) => Promise<User>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  // Ao carregar a página, pergunta à API quem está logado (o token vai junto)
  useEffect(() => {
    authApi
      .me()
      .then((u) => {
        setUser(u)
      })
      .catch((err) => {
        if (!(err instanceof ApiError && err.status === 401)) console.error(err)
        setUser(null)
      })
      .finally(() => setLoading(false))
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const loggedUser = await authApi.login(email, password)
    setUser(loggedUser)
    return loggedUser
  }, [])

  const register = useCallback(async (name: string, email: string, password: string) => {
    const loggedUser = await authApi.register(name, email, password)
    setUser(loggedUser)
    return loggedUser
  }, [])

  const logout = useCallback(async () => {
    try {
      await authApi.logout()
    } finally {
      tokenStore.clear()
      setUser(null)
    }
  }, [])

  return <AuthContext.Provider value={{ user, loading, login, register, logout }}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth deve ser usado dentro de <AuthProvider>')
  return ctx
}
