// Cliente HTTP com suporte robusto a autenticação em iframe e topo.
// Guarda o token de sessão em memória RAM (inMemoryToken), sessionStorage, localStorage
// e window.name — garantindo que a autenticação funcione MESMO quando o app está embutido
// em um iframe de outro domínio onde navegadores bloqueiam cookies e localStorage de terceiros.

const TOKEN_KEY = 'studyai_token'

let inMemoryToken: string | null = null

function readWindowName(): string | null {
  try {
    if (typeof window === 'undefined' || !window.name) return null
    if (window.name.startsWith('{')) {
      const data = JSON.parse(window.name)
      if (typeof data?.[TOKEN_KEY] === 'string') return data[TOKEN_KEY]
    }
  } catch {
    /* ignore */
  }
  return null
}

function writeWindowName(token: string | null) {
  try {
    if (typeof window === 'undefined') return
    let data: Record<string, unknown> = {}
    if (window.name && window.name.startsWith('{')) {
      try {
        data = JSON.parse(window.name)
      } catch {
        data = {}
      }
    }
    if (token) {
      data[TOKEN_KEY] = token
    } else {
      delete data[TOKEN_KEY]
    }
    window.name = JSON.stringify(data)
  } catch {
    /* ignore */
  }
}

function readStorage(): string | null {
  // 0. Propriedade global do Window (acessível no iframe mesmo com storage bloqueado)
  try {
    const g = (window as unknown as { __STUDYAI_TOKEN__?: string }).__STUDYAI_TOKEN__
    if (g) {
      inMemoryToken = g
      return g
    }
  } catch {
    /* ignore */
  }

  // 1. Memória RAM (sempre acessível na mesma sessão da aba)
  if (inMemoryToken) return inMemoryToken

  // 2. localStorage (navegação normal ou iframe particionado)
  try {
    const val = localStorage.getItem(TOKEN_KEY)
    if (val) {
      inMemoryToken = val
      return val
    }
  } catch {
    /* bloqueado por política de iframe */
  }

  // 3. sessionStorage
  try {
    const val = sessionStorage.getItem(TOKEN_KEY)
    if (val) {
      inMemoryToken = val
      return val
    }
  } catch {
    /* bloqueado por política de iframe */
  }

  // 4. window.name (sobrevive a F5 / reload mesmo quando storages são bloqueados no iframe)
  const winVal = readWindowName()
  if (winVal) {
    inMemoryToken = winVal
    return winVal
  }

  return null
}

export const tokenStore = {
  get: (): string | null => readStorage(),
  set: (token: string) => {
    inMemoryToken = token
    try {
      ;(window as unknown as { __STUDYAI_TOKEN__?: string }).__STUDYAI_TOKEN__ = token
    } catch {
      /* ignore */
    }
    try {
      localStorage.setItem(TOKEN_KEY, token)
    } catch {
      /* bloqueado em iframe de terceiros: RAM e window.name cobrem */
    }
    try {
      sessionStorage.setItem(TOKEN_KEY, token)
    } catch {
      /* bloqueado em iframe de terceiros */
    }
    writeWindowName(token)
    console.info('[StudyAI Auth] Token armazenado com sucesso')
  },
  clear: () => {
    inMemoryToken = null
    try {
      delete (window as unknown as { __STUDYAI_TOKEN__?: string }).__STUDYAI_TOKEN__
    } catch {
      /* ignore */
    }
    try {
      localStorage.removeItem(TOKEN_KEY)
    } catch {
      /* ignore */
    }
    try {
      sessionStorage.removeItem(TOKEN_KEY)
    } catch {
      /* ignore */
    }
    writeWindowName(null)
  },
}

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function parseError(res: Response): Promise<string> {
  let text = ''
  try {
    text = await res.text()
    const data = JSON.parse(text)
    if (typeof data?.detail === 'string') return data.detail
    if (typeof data?.message === 'string') return data.message
    if (typeof data?.error === 'string') return data.error
    if (Array.isArray(data?.detail)) {
      return data.detail.map((d: { msg?: string }) => d.msg?.replace(/^Value error, /, '')).join(' ')
    }
  } catch {
    /* corpo não é JSON */
  }
  if (res.status === 502 || res.status === 503 || res.status === 504) {
    return 'Servidor backend reiniciando ou temporariamente indisponível. Aguarde alguns instantes.'
  }
  if (res.status === 401) {
    return 'E-mail ou senha incorretos.'
  }
  if (res.status === 429) {
    return 'Muitas tentativas em pouco tempo. Aguarde alguns instantes antes de tentar novamente.'
  }
  return text || res.statusText || `Erro no servidor (código HTTP ${res.status}).`
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  const isForm = init.body instanceof FormData
  if (!isForm && init.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  let targetUrl = path
  const token = tokenStore.get()
  const isAuthRoute = path.startsWith('/api/auth/login') || path.startsWith('/api/auth/register')
  if (token && !isAuthRoute) {
    if (!headers.has('Authorization')) {
      headers.set('Authorization', `Bearer ${token}`)
    }
    if (!headers.has('X-Session-Token')) {
      headers.set('X-Session-Token', token)
    }
    // Adiciona ?auth_token=... na URL para garantir transmissão mesmo se o navegador filtrar headers no iframe
    const sep = targetUrl.includes('?') ? '&' : '?'
    targetUrl = `${targetUrl}${sep}auth_token=${encodeURIComponent(token)}`
  }

  console.info(`[StudyAI API] ${init.method || 'GET'} ${path} (token=${Boolean(token)})`)
  let res: Response
  try {
    res = await fetch(targetUrl, { credentials: 'include', ...init, headers })
  } catch (netErr) {
    console.error('[StudyAI API Network Error]', netErr)
    throw new ApiError(0, 'Não foi possível conectar ao servidor. Aguarde alguns instantes e tente novamente.')
  }

  if (!res.ok) {
    // Se a rota era autenticada e deu 401, limpa o token. Não limpa na rota /auth/me inicial vazia.
    if (res.status === 401 && token) {
      tokenStore.clear()
    }
    throw new ApiError(res.status, await parseError(res))
  }
  if (res.status === 204) return undefined as T
  return (await res.json()) as T
}

// ---------- Tipos ----------

export interface User {
  id: number
  name: string
  email: string
  created_at: string
}

export interface Material {
  id: number
  title: string
  filename: string
  file_size: number
  page_count: number
  char_count: number
  uploaded_at: string
  has_summary: boolean
  flashcard_count: number
}

export interface Summary {
  id: number
  material_id: number
  text: string
  model: string | null
  generated_at: string
}

export interface AIJob {
  id: number
  kind: string
  status: 'pending' | 'running' | 'done' | 'failed'
  error: string | null
  focus?: string | null
  created_at: string
  finished_at: string | null
}

export interface ConnectionOut {
  id: number
  source_material_id: number
  target_material_id: number
  target_material_title: string
  target_material_filename: string
  relation_type: string
  note: string | null
  created_at: string
}

export interface BacklinkOut {
  id: number
  source_material_id: number
  source_material_title: string
  source_material_filename: string
  relation_type: string
  note: string | null
  created_at: string
}

export interface AvailableTarget {
  id: number
  title: string
  filename: string
}

export interface MaterialConnectionsResponse {
  outgoing: ConnectionOut[]
  incoming: BacklinkOut[]
  available_targets: AvailableTarget[]
}

export interface Flashcard {
  id: number
  material_id: number
  question: string
  answer: string
  created_at: string
  repetitions: number
  interval_days: number
  ease_factor: number
  next_review_at: string | null
  last_reviewed_at: string | null
  is_due: boolean
}

export interface FlashcardListResponse {
  items: Flashcard[]
  total_count: number
  due_count: number
}

export interface MaterialDetail extends Material {
  content_preview: string
  extraction_warning: string | null
  summary: Summary | null
  summary_job: AIJob | null
  flashcards_job: AIJob | null
  flashcards_due_count: number
}

export interface AuthResponse {
  user: User
  access_token: string
  token_type: string
}

// ---------- Auth ----------

async function authenticate(path: string, body: object): Promise<User> {
  tokenStore.clear()
  const data = await api<AuthResponse>(path, { method: 'POST', body: JSON.stringify(body) })
  tokenStore.set(data.access_token)
  return data.user
}

export const authApi = {
  me: () => api<User>('/api/auth/me'),
  login: (email: string, password: string) => authenticate('/api/auth/login', { email, password }),
  register: (name: string, email: string, password: string) =>
    authenticate('/api/auth/register', { name, email, password }),
  logout: async () => {
    try {
      await api<void>('/api/auth/logout', { method: 'POST' })
    } finally {
      tokenStore.clear()
    }
  },
}

// ---------- Materiais ----------

export const materialsApi = {
  list: () => api<Material[]>('/api/materials'),
  get: (id: number) => api<MaterialDetail>(`/api/materials/${id}`),
  content: (id: number) => api<{ id: number; content_text: string }>(`/api/materials/${id}/content`),
  upload: (file: File, title?: string) => {
    const form = new FormData()
    form.append('file', file)
    if (title?.trim()) form.append('title', title.trim())
    return api<MaterialDetail>('/api/materials', { method: 'POST', body: form })
  },
  rename: (id: number, title: string) =>
    api<MaterialDetail>(`/api/materials/${id}`, { method: 'PATCH', body: JSON.stringify({ title }) }),
  remove: (id: number) => api<void>(`/api/materials/${id}`, { method: 'DELETE' }),
  /** Enfileira a geração do resumo; acompanhe via `summary_job` no detalhe do material. */
  generateSummary: (id: number) => api<AIJob>(`/api/materials/${id}/summary`, { method: 'POST' }),
}

// ---------- Flashcards ----------

export const flashcardsApi = {
  list: (materialId: number) => api<FlashcardListResponse>(`/api/materials/${materialId}/flashcards`),
  create: (materialId: number, question: string, answer: string) =>
    api<Flashcard>(`/api/materials/${materialId}/flashcards`, {
      method: 'POST',
      body: JSON.stringify({ question, answer }),
    }),
  generate: (materialId: number, focus?: string) =>
    api<AIJob>(`/api/materials/${materialId}/flashcards/generate`, {
      method: 'POST',
      body: JSON.stringify({ focus: focus?.trim() || null }),
    }),
  study: (materialId: number, mode: 'due' | 'all' = 'all') =>
    api<Flashcard[]>(`/api/materials/${materialId}/flashcards/study?mode=${mode}`),
  review: (cardId: number, rating: number) =>
    api<Flashcard>(`/api/flashcards/${cardId}/review`, {
      method: 'POST',
      body: JSON.stringify({ rating }),
    }),
  update: (cardId: number, data: { question?: string; answer?: string }) =>
    api<Flashcard>(`/api/flashcards/${cardId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  remove: (cardId: number) => api<void>(`/api/flashcards/${cardId}`, { method: 'DELETE' }),
}

// ---------- Conexões de Conhecimento (Grafo) ----------

export const connectionsApi = {
  get: (materialId: number) => api<MaterialConnectionsResponse>(`/api/materials/${materialId}/connections`),
  create: (materialId: number, targetMaterialId: number, relationType: string, note?: string) =>
    api<ConnectionOut>(`/api/materials/${materialId}/connections`, {
      method: 'POST',
      body: JSON.stringify({
        target_material_id: targetMaterialId,
        relation_type: relationType,
        note: note?.trim() || null,
      }),
    }),
  remove: (connectionId: number) => api<void>(`/api/connections/${connectionId}`, { method: 'DELETE' }),
}

// ---------- Utilidades ----------

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' })
}

export function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

export function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}
