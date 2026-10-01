import { useEffect, useRef, useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { formatBytes, formatDate, materialsApi, type Material } from '../api/client'
import { Alert } from '../components/Alert'
import { IconBook, IconCheck, IconFlashcards, IconPlus } from '../components/Icons'

export function MaterialsPage() {
  const navigate = useNavigate()
  const [materials, setMaterials] = useState<Material[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')

  // estado do painel de upload
  const [showUpload, setShowUpload] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [title, setTitle] = useState('')
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  async function load() {
    try {
      setMaterials(await materialsApi.list())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar materiais.')
    }
  }

  useEffect(() => {
    load()
  }, [])

  function handleFileChange(f: File | null) {
    setFile(f)
    setUploadError(null)
    if (f && !title) setTitle(f.name.replace(/\.pdf$/i, '').replace(/[_-]+/g, ' ').trim())
  }

  async function handleUpload(e: FormEvent) {
    e.preventDefault()
    if (!file) return setUploadError('Selecione um arquivo PDF.')
    setUploading(true)
    setUploadError(null)
    try {
      const created = await materialsApi.upload(file, title)
      navigate(`/materiais/${created.id}`)
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Falha no upload.')
    } finally {
      setUploading(false)
    }
  }

  function cancelUpload() {
    setShowUpload(false)
    setFile(null)
    setTitle('')
    setUploadError(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  // Estatísticas do Bento Dashboard
  const totalPages = materials?.reduce((acc, m) => acc + (m.page_count || 0), 0) || 0
  const totalCards = materials?.reduce((acc, m) => acc + (m.flashcard_count || 0), 0) || 0
  const totalSummaries = materials?.filter((m) => m.has_summary).length || 0

  const filteredMaterials = (materials || []).filter((m) =>
    m.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    m.filename.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <>
      <div className="page-header">
        <div>
          <span className="section-pill">Acervo Acadêmico</span>
          <h1>Meus materiais de estudo</h1>
          <p className="muted">Gerencie seus PDFs, gere sínteses com IA e pratique repetição espaçada SM-2.</p>
        </div>
        {!showUpload && (
          <button className="btn btn-primary" onClick={() => setShowUpload(true)}>
            <IconPlus size={16} /> Enviar Novo PDF
          </button>
        )}
      </div>

      {/* Bento Stats Bar (Skill: bento + claude) */}
      {materials && materials.length > 0 && (
        <div className="bento-stats-row">
          <div className="bento-stat-card">
            <span className="bento-stat-label">Documentos</span>
            <div className="bento-stat-value">{materials.length}</div>
            <span className="bento-stat-sub">{totalPages} páginas indexadas</span>
          </div>
          <div className="bento-stat-card">
            <span className="bento-stat-label">Flashcards Ativos</span>
            <div className="bento-stat-value color-cards">{totalCards}</div>
            <span className="bento-stat-sub">Algoritmo SM-2</span>
          </div>
          <div className="bento-stat-card">
            <span className="bento-stat-label">Sínteses Geradas</span>
            <div className="bento-stat-value color-summaries">{totalSummaries}</div>
            <span className="bento-stat-sub">Google Gemini AI</span>
          </div>
        </div>
      )}

      {showUpload && (
        <form className="card upload-card" onSubmit={handleUpload}>
          <h2>Novo material de estudo</h2>
          <p className="muted" style={{ marginBottom: '1rem' }}>
            Selecione uma apostila, artigo ou livro em PDF para validação e extração de texto imediata.
          </p>
          {uploadError && <Alert>{uploadError}</Alert>}
          <label className="file-drop">
            <input
              ref={fileInputRef}
              type="file"
              accept="application/pdf,.pdf"
              onChange={(e) => handleFileChange(e.target.files?.[0] ?? null)}
              disabled={uploading}
            />
            <div className="file-drop-icon">
              <IconBook size={22} />
            </div>
            {file ? (
              <span>
                <strong>{file.name}</strong> <span className="muted">({formatBytes(file.size)})</span>
              </span>
            ) : (
              <span className="muted">Arraste ou clique para selecionar um arquivo PDF (até 25 MB)</span>
            )}
          </label>
          <label style={{ marginTop: '1rem' }}>
            Título de referência
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Ex.: Redes — Modelo OSI e Protocolo TCP/IP"
              maxLength={200}
              disabled={uploading}
            />
          </label>
          <div className="row-end" style={{ marginTop: '1.25rem' }}>
            <button type="button" className="btn btn-ghost" onClick={cancelUpload} disabled={uploading}>
              Cancelar
            </button>
            <button className="btn btn-primary" disabled={uploading || !file}>
              {uploading ? 'Validando e extraindo texto…' : 'Salvar e Abrir'}
            </button>
          </div>
        </form>
      )}

      {error && <Alert>{error}</Alert>}

      {materials === null && !error && (
        <div className="center">
          <div className="spinner" style={{ margin: '0 auto 0.75rem' }} />
          <p className="muted">Carregando acervo de estudos…</p>
        </div>
      )}

      {materials && materials.length === 0 && !showUpload && (
        <div className="card empty-bento-card">
          <div className="empty-icon-circle">
            <IconBook size={28} />
          </div>
          <h3>Nenhum material cadastrado ainda</h3>
          <p className="muted" style={{ maxWidth: '420px', margin: '0.4rem auto 1.5rem' }}>
            Envie sua primeira apostila em PDF para gerar resumos pedagógicos e flashcards de repetição espaçada.
          </p>
          <button className="btn btn-primary" onClick={() => setShowUpload(true)}>
            <IconPlus size={16} /> Enviar meu primeiro PDF
          </button>
        </div>
      )}

      {materials && materials.length > 0 && (
        <>
          <div className="material-filter-bar">
            <input
              type="text"
              className="search-input"
              placeholder="Pesquisar por título ou nome do arquivo…"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <ul className="material-list">
            {filteredMaterials.map((m) => (
              <li key={m.id}>
                <Link to={`/materiais/${m.id}`} className="card material-item">
                  <div className="material-icon" aria-hidden="true">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
                      <polyline points="14 2 14 8 20 8" />
                      <path d="M9 13h6" />
                      <path d="M9 17h3" />
                    </svg>
                  </div>
                  <div className="material-info">
                    <h3 className="material-title">{m.title}</h3>
                    <p className="muted">
                      {m.filename} · {m.page_count} {m.page_count === 1 ? 'página' : 'páginas'} · {formatBytes(m.file_size)} · enviado em{' '}
                      {formatDate(m.uploaded_at)}
                    </p>
                  </div>
                  <div className="material-badges">
                    {m.char_count === 0 && <span className="badge badge-warn">sem texto</span>}
                    {m.has_summary && (
                      <span className="badge badge-green" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                        <IconCheck size={11} /> resumo pronto
                      </span>
                    )}
                    {m.flashcard_count > 0 && (
                      <span className="badge badge-indigo" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                        <IconFlashcards size={11} /> {m.flashcard_count} flashcards
                      </span>
                    )}
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        </>
      )}
    </>
  )
}
